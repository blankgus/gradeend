"""
app.py - GELEIA v2.6 - GRADE SEMANAL COM RENDERIZAÇÃO HTML CORRETA
COM OR-TOOLS, ÍCONES GRANDES E CORES SUAVES
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from models import Turma, Professor, Disciplina, Sala, GradeHoraria, DIAS_SEMANA, HORARIOS_REAIS
from database import (
    salvar_tudo, carregar_tudo, limpar_banco,
    dict_para_turma, dict_para_professor, dict_para_disciplina, dict_para_sala
)
from simple_scheduler import SimpleGradeHoraria

# ============================================================================
# CONFIG
# ============================================================================

st.set_page_config(page_title="GELEIA v2.6", page_icon="🎓", layout="wide")

# CSS para aumentar ícones das abas
st.markdown("""
<style>
    [data-testid="stTabs"] [role="tablist"] button {
        font-size: 24px !important;
        padding: 15px 20px !important;
        gap: 10px !important;
    }
    [data-testid="stTabs"] [role="tablist"] button span {
        font-size: 24px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎓 GELEIA - Grade Horária com OR-Tools")
st.markdown("---")

# ============================================================================
# INIT
# ============================================================================

def validar_dados():
    turmas_json, profs_json, discs_json, salas_json = carregar_tudo()
    
    turmas = [dict_para_turma(t) for t in turmas_json if isinstance(t, dict)]
    turmas += [t for t in turmas_json if isinstance(t, Turma)]
    turmas = [t for t in turmas if t]
    
    profs = [dict_para_professor(p) for p in profs_json if isinstance(p, dict)]
    profs += [p for p in profs_json if isinstance(p, Professor)]
    profs = [p for p in profs if p]
    
    discs = [dict_para_disciplina(d) for d in discs_json if isinstance(d, dict)]
    discs += [d for d in discs_json if isinstance(d, Disciplina)]
    discs = [d for d in discs if d]
    
    salas = [dict_para_sala(s) for s in salas_json if isinstance(s, dict)]
    salas += [s for s in salas_json if isinstance(s, Sala)]
    salas = [s for s in salas if s]
    
    return turmas, profs, discs, salas

def init():
    if 'turmas' not in st.session_state:
        t, p, d, s = validar_dados()
        st.session_state.turmas = t
        st.session_state.professores = p
        st.session_state.disciplinas = d
        st.session_state.salas = s
        st.session_state.grade_horaria = GradeHoraria()
        st.session_state.grade_gerada = False

init()

# ============================================================================
# VALIDAÇÃO PRÉ-GERAÇÃO
# ============================================================================

def validar_antes_gerar(turmas_v, profs_v, discs_v, salas_v):
    erros = []
    warnings = []
    
    if not turmas_v:
        erros.append("❌ Nenhuma turma cadastrada")
    if not profs_v:
        erros.append("❌ Nenhum professor cadastrado")
    if not discs_v:
        erros.append("❌ Nenhuma disciplina cadastrada")
    if not salas_v:
        erros.append("❌ Nenhuma sala cadastrada")
    
    if erros:
        return False, erros, warnings
    
    nomes_profs = {p.nome for p in profs_v}
    nomes_turmas = {t.nome for t in turmas_v}
    
    for disc in discs_v:
        tem_prof = any(disc.nome in p.disciplinas for p in profs_v)
        if not tem_prof:
            erros.append(f"⚠️ Disciplina '{disc.nome}' sem professor")
        
        if not disc.turmas:
            erros.append(f"⚠️ Disciplina '{disc.nome}' sem turmas")
        else:
            for turma in disc.turmas:
                if turma not in nomes_turmas:
                    erros.append(f"⚠️ Disciplina '{disc.nome}' → turma '{turma}' não existe")
        
        if disc.carga_semanal < 1 or disc.carga_semanal > 10:
            erros.append(f"⚠️ Disciplina '{disc.nome}' carga inválida")
    
    for turma in turmas_v:
        discs_turma = [d for d in discs_v if turma.nome in d.turmas]
        if not discs_turma:
            warnings.append(f"⚠️ Turma '{turma.nome}' sem disciplinas")
    
    for prof in profs_v:
        if not prof.disciplinas:
            warnings.append(f"⚠️ Professor '{prof.nome}' sem disciplinas")
    
    sucesso = len(erros) == 0
    return sucesso, erros, warnings

# ============================================================================
# HELPERS
# ============================================================================

def salvar(): 
    return salvar_tudo(st.session_state.turmas, st.session_state.professores, 
                      st.session_state.disciplinas, st.session_state.salas)

def val_multiselect(defaults, options):
    if not defaults: return []
    return [v for v in (defaults if isinstance(defaults, list) else [defaults]) if v in options]

def gerar_html_grade(grade, turma_nome=None):
    """
    Gera HTML da grade semanal com cores suaves
    Retorna: string HTML
    """
    if not grade or not grade.aulas:
        return "<p>Nenhuma aula</p>"
    
    DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
    HORARIOS = ["08:00-10:00", "10:30-12:30"]
    
    # Estrutura: {horario: {dia: [aulas]}}
    grade_data = {h: {d: [] for d in DIAS} for h in HORARIOS}
    
    # Preencher grade
    for aula in grade.aulas:
        if turma_nome and aula.turma != turma_nome:
            continue
        
        dia_map = {
            'segunda': 'Segunda', 'seg': 'Segunda',
            'terça': 'Terça', 'ter': 'Terça',
            'quarta': 'Quarta', 'qua': 'Quarta',
            'quinta': 'Quinta', 'qui': 'Quinta',
            'sexta': 'Sexta', 'sex': 'Sexta',
        }
        
        dia = dia_map.get(aula.dia.lower(), '')
        horario = HORARIOS_REAIS.get(aula.horario, '')
        
        if horario and dia in DIAS:
            grade_data[horario][dia].append({
                'disciplina': aula.disciplina,
                'professor': aula.professor,
                'sala': aula.sala
            })
    
    # ===== GERAR HTML =====
    html = """
    <style>
        .grade-wrapper { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .grade-table { 
            width: 100%; 
            border-collapse: collapse;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border-radius: 12px;
            overflow: hidden;
            background: white;
        }
        .grade-header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 16px; 
            font-weight: bold;
            font-size: 15px;
            text-align: center;
        }
        .grade-horario {
            background: linear-gradient(135deg, #f0f4f8 0%, #e8ecf1 100%);
            color: #2c3e50;
            padding: 14px;
            font-weight: bold;
            min-width: 110px;
            text-align: center;
        }
        .grade-celula {
            border: 1px solid #e8eef5;
            padding: 12px;
            height: 130px;
            background: #ffffff;
            vertical-align: top;
            font-size: 13px;
            overflow-y: auto;
        }
        .grade-celula:hover {
            background: #f8fafc;
        }
        .aula {
            background: linear-gradient(135deg, #c8dff8 0%, #d5e8f7 100%);
            color: #1e3a5f;
            border-radius: 8px;
            padding: 10px;
            margin: 5px 0;
            font-weight: 500;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 4px rgba(102, 126, 234, 0.15);
        }
        .aula-disciplina { 
            font-weight: bold; 
            font-size: 13px;
            margin-bottom: 4px;
        }
        .aula-prof { 
            font-size: 11px; 
            color: #4a5f7f;
            margin: 2px 0;
        }
        .aula-sala { 
            font-size: 11px; 
            color: #6b7c94;
            margin-top: 2px;
        }
        .vago {
            color: #cbd5e1;
            text-align: center;
            font-style: italic;
            padding-top: 50px;
            font-size: 14px;
        }
    </style>
    <div class="grade-wrapper">
        <table class="grade-table">
            <tr>
                <th class="grade-header">⏰ Horário</th>
    """
    
    # Headers dos dias
    for dia in DIAS:
        html += f'<th class="grade-header">{dia}</th>'
    html += '</tr>'
    
    # Linhas de horários
    for horario in HORARIOS:
        html += f'<tr><td class="grade-horario">{horario}</td>'
        
        for dia in DIAS:
            html += '<td class="grade-celula">'
            aulas = grade_data[horario].get(dia, [])
            
            if aulas:
                for aula in aulas:
                    html += f'''
                        <div class="aula">
                            <div class="aula-disciplina">{aula['disciplina']}</div>
                            <div class="aula-prof">👨‍🏫 {aula['professor']}</div>
                            <div class="aula-sala">🚪 {aula['sala']}</div>
                        </div>
                    '''
            else:
                html += '<div class="vago">—</div>'
            
            html += '</td>'
        html += '</tr>'
    
    html += '</table></div>'
    return html

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.header("📊 Status")
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("📚", len([t for t in st.session_state.turmas if isinstance(t, Turma)]))
        st.metric("📖", len([d for d in st.session_state.disciplinas if isinstance(d, Disciplina)]))
    with c2:
        st.metric("👨‍🏫", len([p for p in st.session_state.professores if isinstance(p, Professor)]))
        st.metric("🏛️", len([s for s in st.session_state.salas if isinstance(s, Sala)]))
    
    st.divider()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💾", use_container_width=True):
            salvar()
            st.success("✅")
    with c2:
        if st.button("🔄", use_container_width=True):
            st.rerun()
    with c3:
        if st.button("🧹", use_container_width=True):
            limpar_banco()
            init()
            st.rerun()

# ============================================================================
# ABAS - COM ÍCONES MAIORES
# ============================================================================

aba_inicio, aba_disc, aba_prof, aba_turmas, aba_salas, aba_grade, aba_rel = st.tabs([
    "🏠 Início",
    "📚 Disciplinas",
    "👨‍🏫 Professores",
    "🎓 Turmas",
    "🏛️ Salas",
    "📅 Grade",
    "📊 Relatórios"
])

# ============================================================================
# ABA: INÍCIO
# ============================================================================

with aba_inicio:
    st.header("Dashboard")
    
    t_count = len([t for t in st.session_state.turmas if isinstance(t, Turma)])
    p_count = len([p for p in st.session_state.professores if isinstance(p, Professor)])
    d_count = len([d for d in st.session_state.disciplinas if isinstance(d, Disciplina)])
    s_count = len([s for s in st.session_state.salas if isinstance(s, Sala)])
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Turmas", t_count)
    with c2: st.metric("Professores", p_count)
    with c3: st.metric("Disciplinas", d_count)
    with c4: st.metric("Salas", s_count)
    
    if all([t_count > 0, p_count > 0, d_count > 0, s_count > 0]):
        st.success("✅ Pronto para gerar!")
    else:
        st.warning("⚠️ Complete o cadastro")

# ============================================================================
# ABA: DISCIPLINAS
# ============================================================================

with aba_disc:
    st.header("Disciplinas")
    
    with st.expander("➕ Nova"):
        with st.form("add_disc"):
            c1, c2 = st.columns(2)
            with c1:
                nome = st.text_input("Nome*")
                carga = st.number_input("Carga", 1, 10, 2, key="carga_new_disc")
            with c2:
                turmas_opt = [t.nome for t in st.session_state.turmas if isinstance(t, Turma)]
                turmas = st.multiselect("Turmas*", turmas_opt, key="turmas_new_disc") if turmas_opt else []
            
            if st.form_submit_button("✅"):
                if nome and turmas:
                    st.session_state.disciplinas.append(Disciplina(nome, carga, turmas))
                    salvar()
                    st.rerun()
    
    discs = [d for d in st.session_state.disciplinas if isinstance(d, Disciplina)]
    if discs:
        df = pd.DataFrame([{'Nome': d.nome, 'Carga': d.carga_semanal, 'Turmas': ', '.join(d.turmas)} for d in discs])
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        for d in discs:
            with st.expander(f"{d.nome}"):
                with st.form(f"edit_disc_{d.id}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        novo_nome = st.text_input("Nome", d.nome, key=f"dn_{d.id}")
                        nova_carga = st.number_input("Carga", 1, 10, d.carga_semanal, key=f"dc_{d.id}")
                    with c2:
                        turmas_opt = [t.nome for t in st.session_state.turmas if isinstance(t, Turma)]
                        turmas_val = val_multiselect(d.turmas, turmas_opt)
                        novas_turmas = st.multiselect("Turmas", turmas_opt, default=turmas_val, key=f"dt_{d.id}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.form_submit_button("💾", key=f"sd_{d.id}"):
                            d.nome = novo_nome
                            d.carga_semanal = nova_carga
                            d.turmas = novas_turmas
                            salvar()
                            st.rerun()
                    with c2:
                        if st.form_submit_button("🗑️", key=f"dd_{d.id}"):
                            st.session_state.disciplinas.remove(d)
                            salvar()
                            st.rerun()

# ============================================================================
# ABA: PROFESSORES
# ============================================================================

with aba_prof:
    st.header("Professores")
    
    with st.expander("➕ Novo"):
        with st.form("add_prof"):
            nome = st.text_input("Nome*", key="nome_new_prof")
            disc_opt = [d.nome for d in st.session_state.disciplinas if isinstance(d, Disciplina)]
            disc = st.multiselect("Disciplinas*", disc_opt, key="disc_new_prof") if disc_opt else []
            
            if st.form_submit_button("✅"):
                if nome and disc:
                    st.session_state.professores.append(Professor(nome, disc))
                    salvar()
                    st.rerun()
    
    profs = [p for p in st.session_state.professores if isinstance(p, Professor)]
    if profs:
        df = pd.DataFrame([{'Nome': p.nome, 'Disciplinas': ', '.join(p.disciplinas)} for p in profs])
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        for p in profs:
            with st.expander(f"{p.nome}"):
                with st.form(f"edit_prof_{p.id}"):
                    novo_nome = st.text_input("Nome", p.nome, key=f"pn_{p.id}")
                    disc_opt = [d.nome for d in st.session_state.disciplinas if isinstance(d, Disciplina)]
                    disc_val = val_multiselect(p.disciplinas, disc_opt)
                    novas_disc = st.multiselect("Disciplinas", disc_opt, default=disc_val, key=f"pd_{p.id}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.form_submit_button("💾", key=f"sp_{p.id}"):
                            p.nome = novo_nome
                            p.disciplinas = novas_disc
                            salvar()
                            st.rerun()
                    with c2:
                        if st.form_submit_button("🗑️", key=f"dp_{p.id}"):
                            st.session_state.professores.remove(p)
                            salvar()
                            st.rerun()

# ============================================================================
# ABA: TURMAS
# ============================================================================

with aba_turmas:
    st.header("Turmas")
    
    with st.expander("➕ Nova"):
        with st.form("add_turma"):
            c1, c2 = st.columns(2)
            with c1:
                nome = st.text_input("Nome*", key="nome_new_turma")
                sem = st.number_input("Semestre*", 1, 8, 1, key="sem_new_turma")
            with c2:
                curso = st.text_input("Curso*", key="curso_new_turma")
                alunos = st.number_input("Alunos*", 1, 100, 30, key="alunos_new_turma")
            
            if st.form_submit_button("✅"):
                if nome and curso:
                    st.session_state.turmas.append(Turma(nome, sem, curso, alunos))
                    salvar()
                    st.rerun()
    
    turmas = [t for t in st.session_state.turmas if isinstance(t, Turma)]
    if turmas:
        df = pd.DataFrame([{'Nome': t.nome, 'Curso': t.curso, 'Sem': t.semestre, 'Alunos': t.quantidade_alunos} for t in turmas])
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        for t in turmas:
            with st.expander(f"{t.nome}"):
                with st.form(f"edit_turma_{t.id}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        novo_nome = st.text_input("Nome", t.nome, key=f"tn_{t.id}")
                        novo_sem = st.number_input("Semestre", 1, 8, max(1, min(8, t.semestre)), key=f"ts_{t.id}")
                    with c2:
                        novo_curso = st.text_input("Curso", t.curso, key=f"tc_{t.id}")
                        novo_alunos = st.number_input("Alunos", 1, 100, max(1, min(100, t.quantidade_alunos)), key=f"ta_{t.id}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.form_submit_button("💾", key=f"st_{t.id}"):
                            t.nome = novo_nome
                            t.semestre = novo_sem
                            t.curso = novo_curso
                            t.quantidade_alunos = novo_alunos
                            salvar()
                            st.rerun()
                    with c2:
                        if st.form_submit_button("🗑️", key=f"dt_{t.id}"):
                            st.session_state.turmas.remove(t)
                            salvar()
                            st.rerun()

# ============================================================================
# ABA: SALAS
# ============================================================================

with aba_salas:
    st.header("Salas")
    
    with st.expander("➕ Nova"):
        with st.form("add_sala"):
            c1, c2 = st.columns(2)
            with c1:
                nome = st.text_input("Nome*", key="nome_new_sala")
                cap = st.number_input("Capacidade*", 10, 100, 40, key="cap_new_sala")
            with c2:
                pred = st.text_input("Prédio*", key="pred_new_sala")
                and_s = st.number_input("Andar*", 0, 10, 1, key="and_new_sala")
            
            if st.form_submit_button("✅"):
                if nome and pred:
                    st.session_state.salas.append(Sala(nome, cap, pred, and_s))
                    salvar()
                    st.rerun()
    
    salas = [s for s in st.session_state.salas if isinstance(s, Sala)]
    if salas:
        df = pd.DataFrame([{'Nome': s.nome, 'Cap': s.capacidade, 'Prédio': s.predio, 'Andar': s.andar} for s in salas])
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        for s in salas:
            with st.expander(f"{s.nome}"):
                with st.form(f"edit_sala_{s.id}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        novo_nome = st.text_input("Nome", s.nome, key=f"sn_{s.id}")
                        nova_cap = st.number_input("Cap", 10, 100, max(10, min(100, s.capacidade)), key=f"sc_{s.id}")
                    with c2:
                        novo_pred = st.text_input("Prédio", s.predio, key=f"sp_{s.id}")
                        novo_and = st.number_input("Andar", 0, 10, max(0, min(10, s.andar)), key=f"sa_{s.id}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.form_submit_button("💾", key=f"ss_{s.id}"):
                            s.nome = novo_nome
                            s.capacidade = nova_cap
                            s.predio = novo_pred
                            s.andar = novo_and
                            salvar()
                            st.rerun()
                    with c2:
                        if st.form_submit_button("🗑️", key=f"ds_{s.id}"):
                            st.session_state.salas.remove(s)
                            salvar()
                            st.rerun()

# ============================================================================
# ABA: GRADE - COM OR-TOOLS E HTML st.html()
# ============================================================================

with aba_grade:
    st.header("📅 Grade Horária - Semanal Padrão")
    
    turmas_v = [t for t in st.session_state.turmas if isinstance(t, Turma)]
    profs_v = [p for p in st.session_state.professores if isinstance(p, Professor)]
    discs_v = [d for d in st.session_state.disciplinas if isinstance(d, Disciplina)]
    salas_v = [s for s in st.session_state.salas if isinstance(s, Sala)]
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("📚", len(turmas_v))
    with c2: st.metric("👨‍🏫", len(profs_v))
    with c3: st.metric("📖", len(discs_v))
    with c4: st.metric("🏛️", len(salas_v))
    
    st.divider()
    
    # ===== GERAR GRADE =====
    c1, c2, c3 = st.columns([2, 1, 1])
    
    with c1:
        if st.button("🚀 Gerar Grade (OR-Tools)", use_container_width=True):
            sucesso, erros, warnings = validar_antes_gerar(turmas_v, profs_v, discs_v, salas_v)
            
            if erros:
                st.error("❌ **Erros:**")
                for erro in erros:
                    st.error(erro)
                st.stop()
            
            if warnings:
                with st.expander("⚠️ Avisos"):
                    for warn in warnings:
                        st.warning(warn)
            
            if sucesso:
                with st.spinner("⏳ OR-Tools processando..."):
                    try:
                        scheduler = SimpleGradeHoraria(turmas_v, profs_v, discs_v, salas_v)
                        st.session_state.grade_horaria = scheduler.gerar_grade()
                        st.session_state.grade_gerada = True
                        
                        if st.session_state.grade_horaria.aulas:
                            st.success(f"✅ Grade gerada com {len(st.session_state.grade_horaria.aulas)} aulas!")
                        else:
                            st.warning("⚠️ Grade vazia")
                    
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")
                        st.info("💡 Tente reduzir a carga ou adicionar mais turmas/salas")
    
    with c2:
        if st.session_state.grade_gerada and st.button("💾", use_container_width=True):
            salvar()
            st.success("✅")
    
    with c3:
        if st.session_state.grade_gerada and st.session_state.grade_horaria.aulas:
            dados = [{
                'Dia': a.dia.upper(),
                'Horário': HORARIOS_REAIS.get(a.horario, ''),
                'Disciplina': a.disciplina,
                'Professor': a.professor,
                'Sala': a.sala,
                'Turma': a.turma
            } for a in st.session_state.grade_horaria.aulas]
            df = pd.DataFrame(dados)
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button("📥", csv, f"grade.csv", "text/csv", use_container_width=True)
    
    st.divider()
    
    # ===== EXIBIÇÃO COM st.html() =====
    if st.session_state.grade_gerada:
        st.subheader("📊 Grade por Turma")
        
        turmas_com_aulas = sorted(set(a.turma for a in st.session_state.grade_horaria.aulas))
        
        if turmas_com_aulas:
            turma_selecionada = st.selectbox(
                "Selecione a turma:",
                turmas_com_aulas,
                key="turma_grade_selector"
            )
            
            # ===== RENDERIZAR COM st.html() =====
            html_grade = gerar_html_grade(st.session_state.grade_horaria, turma_selecionada)
            st.html(html_grade)
            
            # Resumo
            with st.expander("📈 Resumo"):
                aulas_turma = [a for a in st.session_state.grade_horaria.aulas if a.turma == turma_selecionada]
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.metric("Aulas", len(aulas_turma))
                with c2: st.metric("Disciplinas", len(set(a.disciplina for a in aulas_turma)))
                with c3: st.metric("Professores", len(set(a.professor for a in aulas_turma)))
                with c4: st.metric("Salas", len(set(a.sala for a in aulas_turma)))
        else:
            st.info("Nenhuma turma com aulas")
    else:
        st.info("Clique em 'Gerar Grade' para criar")

# ============================================================================
# ABA: RELATÓRIOS
# ============================================================================

with aba_rel:
    st.header("Relatórios")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Disciplinas por Turma")
        for t in turmas_v:
            discs = [d for d in discs_v if t.nome in d.turmas]
            with st.expander(f"{t.nome} ({len(discs)})"):
                for d in discs:
                    st.write(f"📖 {d.nome} ({d.carga_semanal}h)")
    
    with c2:
        st.subheader("Disciplinas por Prof")
        for p in profs_v:
            with st.expander(f"{p.nome} ({len(p.disciplinas)})"):
                for d in p.disciplinas:
                    st.write(f"📖 {d}")

st.markdown("---")
st.markdown("<div style='text-align: center;'>🎓 GELEIA v2.6 | OR-Tools ✅</div>", unsafe_allow_html=True)
