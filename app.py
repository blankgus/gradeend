"""
app.py - Aplicação Principal GELEIA
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List

from models import (
    Turma, Professor, Disciplina, Sala, Aula, GradeHoraria,
    DIAS_SEMANA, HORARIOS_REAIS
)
from database import salvar_tudo, carregar_tudo, limpar_banco
from simple_scheduler import SimpleGradeHoraria

# ============================================================================
# CONFIGURAÇÃO INICIAL
# ============================================================================

st.set_page_config(
    page_title="GELEIA - Gerador de Grade Horária",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# INICIALIZAÇÃO DO ESTADO DA SESSÃO
# ============================================================================

def init_session_state():
    """Inicializa o estado da sessão com dados persistidos"""
    if 'turmas' not in st.session_state:
        turmas, professores, disciplinas, salas = carregar_tudo()
        st.session_state.turmas = turmas
        st.session_state.professores = professores
        st.session_state.disciplinas = disciplinas
        st.session_state.salas = salas
    
    if 'grade_horaria' not in st.session_state:
        st.session_state.grade_horaria = GradeHoraria()
    
    if 'grade_gerada' not in st.session_state:
        st.session_state.grade_gerada = False

init_session_state()

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def validar_default_multiselect(default_values, available_options):
    """Valida valores padrão em multiselect"""
    if not default_values:
        return []
    
    if isinstance(default_values, str):
        default_values = [default_values]
    
    valid_values = [v for v in default_values if v in available_options]
    return valid_values if valid_values else []

def salvar_tudo_local():
    """Salva todos os dados da sessão no banco de dados"""
    return salvar_tudo(
        st.session_state.turmas,
        st.session_state.professores,
        st.session_state.disciplinas,
        st.session_state.salas
    )

def exibir_grade(grade):
    """Exibe a grade horária com horários nas LINHAS e dias nas COLUNAS"""
    st.subheader("📅 Grade Horária Completa")
    
    DIAS = [dia.capitalize() for dia in DIAS_SEMANA]
    HORARIOS = ["08:00-10:00", "10:30-12:30"]
    
    # Estrutura: horario -> dia -> aulas
    grade_data = {
        horario: {dia: [] for dia in DIAS} 
        for horario in HORARIOS
    }
    
    for aula in grade.aulas:
        dia = aula.dia.capitalize()
        horario = HORARIOS_REAIS[aula.horario]
        
        if horario in grade_data and dia in grade_data[horario]:
            info_aula = f"{aula.disciplina}\n({aula.professor})\nSala: {aula.sala}"
            grade_data[horario][dia].append(info_aula)
    
    html = """
    <style>
        .grade-table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }
        .grade-table th, .grade-table td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: center;
            vertical-align: top;
        }
        .grade-table th {
            background-color: #4A90E2;
            color: white;
            font-weight: bold;
        }
        .grade-table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .aula-item {
            background-color: #f0f8ff;
            border-radius: 4px;
            padding: 8px;
            margin: 4px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            font-size: 12px;
        }
    </style>
    <table class="grade-table">
        <tr>
            <th>⏰ Horário</th>
    """
    
    # Cabeçalho com os dias da semana
    for dia in DIAS:
        html += f"<th>{dia}</th>"
    html += "</tr>"
    
    # Linhas para cada horário
    for horario in HORARIOS:
        html += f"<tr><td><strong>{horario}</strong></td>"
        for dia in DIAS:
            aulas_dia_horario = grade_data[horario].get(dia, [])
            html += "<td>"
            for aula_info in aulas_dia_horario:
                html += f'<div class="aula-item">{aula_info}</div>'
            if not aulas_dia_horario:
                html += "<div style='color: #999; font-style: italic;'>Livre</div>"
            html += "</td>"
        html += "</tr>"
    
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)

# ============================================================================
# HEADER PRINCIPAL
# ============================================================================

st.title("🎓 GELEIA - Gerador de Grade Horária Escolar")

# ============================================================================
# CRIAÇÃO DE TODAS AS ABAS
# ============================================================================

aba_inicio, aba_disciplinas, aba_professores, aba_turmas, aba_salas, aba_grade, aba_relatorios = st.tabs([
    "🏠 Início",
    "📚 Disciplinas",
    "👩‍🏫 Professores",
    "🎓 Turmas",
    "🏫 Salas",
    "📋 Gerar Grade",
    "📊 Relatórios"
])

# ============================================================================
# ABA 0: INÍCIO
# ============================================================================

with aba_inicio:
    st.header("🏠 Dashboard Principal")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Turmas", len(st.session_state.turmas))
    with col2:
        st.metric("Professores", len(st.session_state.professores))
    with col3:
        st.metric("Disciplinas", len(st.session_state.disciplinas))
    with col4:
        st.metric("Salas", len(st.session_state.salas))
    
    st.divider()
    
    st.subheader("ℹ️ Informações do Projeto")
    st.info("""
    **GELEIA - Grade Escolar Livre Elaborada com Inteligência Artificial**
    
    - A grade apresenta o horário completo contendo todas as aulas definidas pelo usuário
    - A grade é construída considerando uma semana de 5 dias (segunda a sexta)
    - Cada dia tem 2 horários para aula (08:00-10:00 e 10:30-12:30)
    - O número máximo de disciplinas do curso é 50 (10 horários X 5 salas)
    """)

    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Salvar Todos os Dados", use_container_width=True):
            if salvar_tudo_local():
                st.success("✅ Dados salvos com sucesso!")
    
    with col2:
        if st.button("🔄 Recarregar Dados", use_container_width=True):
            init_session_state()
            st.success("✅ Dados recarregados!")
            st.rerun()
    
    with col3:
        if st.button("🧹 Limpar Banco de Dados", use_container_width=True):
            if limpar_banco():
                init_session_state()
                st.success("✅ Banco limpo e dados recarregados!")
                st.rerun()

# ============================================================================
# ABA 1: DISCIPLINAS
# ============================================================================

with aba_disciplinas:
    st.header("📚 Gerenciamento de Disciplinas")
    
    with st.expander("➕ Adicionar Nova Disciplina", expanded=False):
        with st.form("form_add_disc"):
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome da Disciplina*", key="input_nome_disc")
                carga = st.number_input("Carga Semanal*", 1, 10, 2, key="input_carga_disc")
            
            with col2:
                turmas_opcoes = [t.nome for t in st.session_state.turmas]
                turmas_selecionadas = st.multiselect("Turmas*", turmas_opcoes, key="multi_turmas_add_disc")
            
            if st.form_submit_button("✅ Adicionar Disciplina"):
                if nome and turmas_selecionadas:
                    try:
                        nova_disciplina = Disciplina(
                            nome, carga, turmas_selecionadas
                        )
                        st.session_state.disciplinas.append(nova_disciplina)
                        if salvar_tudo_local():
                            st.success(f"✅ Disciplina '{nome}' adicionada!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")
                else:
                    st.error("❌ Preencha todos os campos obrigatórios (*)")
    
    st.subheader("📋 Lista de Disciplinas")
    
    if not st.session_state.disciplinas:
        st.info("📝 Nenhuma disciplina cadastrada.")
    else:
        df_discs = pd.DataFrame([{
            'Nome': d.nome,
            'Carga': d.carga_semanal,
            'Turmas': ', '.join(d.turmas)
        } for d in st.session_state.disciplinas])
        
        st.dataframe(df_discs, use_container_width=True, hide_index=True)
        
        st.divider()
        
        for disc in st.session_state.disciplinas:
            with st.expander(f"📖 {disc.nome}", expanded=False):
                with st.form(f"form_edit_disc_{disc.id}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        novo_nome = st.text_input("Nome", disc.nome, key=f"edit_nome_disc_{disc.id}")
                        nova_carga = st.number_input("Carga", 1, 10, disc.carga_semanal, key=f"edit_carga_disc_{disc.id}")
                    
                    with col2:
                        turmas_opcoes = [t.nome for t in st.session_state.turmas]
                        turmas_validas = validar_default_multiselect(disc.turmas, turmas_opcoes)
                        
                        turmas_selecionadas = st.multiselect(
                            "Turmas",
                            turmas_opcoes,
                            default=turmas_validas,
                            key=f"edit_turmas_disc_{disc.id}"
                        )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Salvar", key=f"btn_save_disc_{disc.id}"):
                            if novo_nome and turmas_selecionadas:
                                disc.nome = novo_nome
                                disc.carga_semanal = nova_carga
                                disc.turmas = turmas_selecionadas
                                if salvar_tudo_local():
                                    st.success("✅ Atualizado!")
                                    st.rerun()
                    
                    with col2:
                        if st.form_submit_button("🗑️ Deletar", key=f"btn_delete_disc_{disc.id}"):
                            st.session_state.disciplinas.remove(disc)
                            if salvar_tudo_local():
                                st.success("✅ Removido!")
                                st.rerun()

# ============================================================================
# ABA 2: PROFESSORES
# ============================================================================

with aba_professores:
    st.header("👩‍🏫 Gerenciamento de Professores")
    
    with st.expander("➕ Adicionar Novo Professor", expanded=False):
        with st.form("form_add_prof"):
            nome = st.text_input("Nome do Professor*", key="input_nome_prof")
            disciplinas_opcoes = [d.nome for d in st.session_state.disciplinas]
            disciplinas_selecionadas = st.multiselect("Disciplinas*", disciplinas_opcoes, key="multi_disc_add_prof")
            
            st.subheader("Disponibilidade (marque os horários disponíveis)")
            disponibilidade = {}
            
            for dia in DIAS_SEMANA:
                col1, col2 = st.columns(2)
                with col1:
                    disp_manha = st.checkbox(f"{dia.capitalize()} (08:00-10:00)", True, key=f"disp_{dia}_0")
                    disponibilidade[f"{dia}-0"] = disp_manha
                with col2:
                    disp_tarde = st.checkbox(f"{dia.capitalize()} (10:30-12:30)", True, key=f"disp_{dia}_1")
                    disponibilidade[f"{dia}-1"] = disp_tarde
            
            if st.form_submit_button("✅ Adicionar Professor"):
                if nome and disciplinas_selecionadas:
                    try:
                        novo_prof = Professor(nome, disciplinas_selecionadas, disponibilidade)
                        st.session_state.professores.append(novo_prof)
                        if salvar_tudo_local():
                            st.success(f"✅ Professor '{nome}' adicionado!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")
                else:
                    st.error("❌ Preencha todos os campos obrigatórios (*)")
    
    st.subheader("📋 Lista de Professores")
    
    if not st.session_state.professores:
        st.info("📝 Nenhum professor cadastrado.")
    else:
        df_profs = pd.DataFrame([{
            'Nome': p.nome,
            'Disciplinas': ', '.join(p.disciplinas)
        } for p in st.session_state.professores])
        
        st.dataframe(df_profs, use_container_width=True, hide_index=True)
        
        st.divider()
        
        for prof in st.session_state.professores:
            with st.expander(f"👤 {prof.nome}", expanded=False):
                with st.form(f"form_edit_prof_{prof.id}"):
                    novo_nome = st.text_input("Nome", prof.nome, key=f"edit_nome_prof_{prof.id}")
                    
                    disciplinas_opcoes = [d.nome for d in st.session_state.disciplinas]
                    disciplinas_validas = validar_default_multiselect(prof.disciplinas, disciplinas_opcoes)
                    
                    prof_disciplinas = st.multiselect(
                        "Disciplinas",
                        disciplinas_opcoes,
                        default=disciplinas_validas,
                        key=f"edit_disc_prof_{prof.id}"
                    )
                    
                    st.subheader("Disponibilidade")
                    nova_disponibilidade = {}
                    
                    for dia in DIAS_SEMANA:
                        col1, col2 = st.columns(2)
                        with col1:
                            disp_manha = st.checkbox(
                                f"{dia.capitalize()} (08:00-10:00)", 
                                prof.disponibilidade.get(f"{dia}-0", True),
                                key=f"edit_disp_{prof.id}_{dia}_0"
                            )
                            nova_disponibilidade[f"{dia}-0"] = disp_manha
                        with col2:
                            disp_tarde = st.checkbox(
                                f"{dia.capitalize()} (10:30-12:30)", 
                                prof.disponibilidade.get(f"{dia}-1", True),
                                key=f"edit_disp_{prof.id}_{dia}_1"
                            )
                            nova_disponibilidade[f"{dia}-1"] = disp_tarde
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Salvar", key=f"btn_save_prof_{prof.id}"):
                            prof.nome = novo_nome
                            prof.disciplinas = prof_disciplinas
                            prof.disponibilidade = nova_disponibilidade
                            if salvar_tudo_local():
                                st.success("✅ Atualizado!")
                                st.rerun()
                    
                    with col2:
                        if st.form_submit_button("🗑️ Deletar", key=f"btn_delete_prof_{prof.id}"):
                            st.session_state.professores.remove(prof)
                            if salvar_tudo_local():
                                st.success("✅ Removido!")
                                st.rerun()

# ============================================================================
# ABA 3: TURMAS
# ============================================================================

with aba_turmas:
    st.header("🎓 Gerenciamento de Turmas")
    
    with st.expander("➕ Adicionar Nova Turma", expanded=False):
        with st.form("form_add_turma"):
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome da Turma*", key="input_nome_turma")
                serie = st.text_input("Série*", "6", key="input_serie_turma")
            with col2:
                grupo = st.selectbox("Grupo*", ["A", "B"], key="select_grupo_turma")
                capacidade = st.number_input("Capacidade*", 1, 50, 25, key="input_cap_turma")
            
            turno = st.selectbox("Turno*", ["Matutino", "Vespertino", "Noturno"], key="select_turno_turma")
            
            if st.form_submit_button("✅ Adicionar Turma"):
                if nome and serie:
                    try:
                        nova_turma = Turma(nome, serie, turno, grupo, capacidade=capacidade)
                        st.session_state.turmas.append(nova_turma)
                        if salvar_tudo_local():
                            st.success(f"✅ Turma '{nome}' adicionada!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")
    
    st.subheader("📋 Lista de Turmas")
    
    if not st.session_state.turmas:
        st.info("📝 Nenhuma turma cadastrada.")
    else:
        df_turmas = pd.DataFrame([{
            'Nome': t.nome,
            'Série': t.serie,
            'Grupo': t.grupo,
            'Capacidade': t.capacidade,
            'Turno': t.turno
        } for t in st.session_state.turmas])
        
        st.dataframe(df_turmas, use_container_width=True, hide_index=True)
        
        st.divider()
        
        for turma in st.session_state.turmas:
            with st.expander(f"🏫 {turma.nome} ({turma.serie}º - {turma.grupo})", expanded=False):
                with st.form(f"form_edit_turma_{turma.id}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        novo_nome = st.text_input("Nome", turma.nome, key=f"edit_nome_turma_{turma.id}")
                        nova_serie = st.text_input("Série", turma.serie, key=f"edit_serie_turma_{turma.id}")
                    
                    with col2:
                        novo_grupo = st.selectbox("Grupo", ["A", "B"], key=f"edit_grupo_turma_{turma.id}")
                        nova_capacidade = st.number_input("Capacidade", 1, 50, turma.capacidade, key=f"edit_cap_turma_{turma.id}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Salvar", key=f"btn_save_turma_{turma.id}"):
                            turma.nome = novo_nome
                            turma.serie = nova_serie
                            turma.grupo = novo_grupo
                            turma.capacidade = nova_capacidade
                            if salvar_tudo_local():
                                st.success("✅ Atualizado!")
                                st.rerun()
                    
                    with col2:
                        if st.form_submit_button("🗑️ Deletar", key=f"btn_delete_turma_{turma.id}"):
                            st.session_state.turmas.remove(turma)
                            if salvar_tudo_local():
                                st.success("✅ Removido!")
                                st.rerun()

# ============================================================================
# ABA 4: SALAS
# ============================================================================

with aba_salas:
    st.header("🏫 Gerenciamento de Salas")
    
    with st.expander("➕ Adicionar Nova Sala", expanded=False):
        with st.form("form_add_sala"):
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome da Sala*", key="input_nome_sala")
            with col2:
                capacidade = st.number_input("Capacidade*", 1, 60, 25, key="input_cap_sala")
            
            if st.form_submit_button("✅ Adicionar Sala"):
                if nome:
                    try:
                        nova_sala = Sala(nome, capacidade)
                        st.session_state.salas.append(nova_sala)
                        if salvar_tudo_local():
                            st.success(f"✅ Sala '{nome}' adicionada!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")
    
    st.subheader("📋 Lista de Salas")
    
    if not st.session_state.salas:
        st.info("📝 Nenhuma sala cadastrada.")
    else:
        df_salas = pd.DataFrame([{
            'Nome': s.nome,
            'Capacidade': s.capacidade
        } for s in st.session_state.salas])
        
        st.dataframe(df_salas, use_container_width=True, hide_index=True)
        
        st.divider()
        
        for sala in st.session_state.salas:
            with st.expander(f"🚪 {sala.nome}", expanded=False):
                with st.form(f"form_edit_sala_{sala.id}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        novo_nome = st.text_input("Nome", sala.nome, key=f"edit_nome_sala_{sala.id}")
                    with col2:
                        nova_capacidade = st.number_input("Capacidade", 1, 60, sala.capacidade, key=f"edit_cap_sala_{sala.id}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Salvar", key=f"btn_save_sala_{sala.id}"):
                            sala.nome = novo_nome
                            sala.capacidade = nova_capacidade
                            if salvar_tudo_local():
                                st.success("✅ Atualizado!")
                                st.rerun()
                    
                    with col2:
                        if st.form_submit_button("🗑️ Deletar", key=f"btn_delete_sala_{sala.id}"):
                            st.session_state.salas.remove(sala)
                            if salvar_tudo_local():
                                st.success("✅ Removido!")
                                st.rerun()

# ============================================================================
# ABA 5: GERAR GRADE
# ============================================================================

with aba_grade:
    st.header("📋 Geração de Grade Horária")
    
    valido = True
    mensagem = "✅ Dados válidos para geração"
    
    if not st.session_state.turmas:
        valido = False
        mensagem = "❌ Nenhuma turma cadastrada"
    elif not st.session_state.professores:
        valido = False
        mensagem = "❌ Nenhum professor cadastrado"
    elif not st.session_state.disciplinas:
        valido = False
        mensagem = "❌ Nenhuma disciplina cadastrada"
    elif not st.session_state.salas:
        valido = False
        mensagem = "❌ Nenhuma sala cadastrada"
    
    st.info(mensagem)
    
    if st.button("🚀 Gerar Grade", use_container_width=True, disabled=not valido):
        with st.spinner("⏳ Gerando grade horária..."):
            try:
                scheduler = SimpleGradeHoraria()
                grade = scheduler.gerar(
                    st.session_state.turmas,
                    st.session_state.professores,
                    st.session_state.disciplinas,
                    st.session_state.salas
                )
                
                st.session_state.grade_horaria = grade
                st.session_state.grade_gerada = True
                
                st.success(f"✅ Grade gerada com {len(grade.aulas)} aulas!")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erro ao gerar grade: {str(e)}")
    
    if st.session_state.grade_gerada:
        exibir_grade(st.session_state.grade_horaria)
        
        st.divider()
        st.subheader("📊 Estatísticas da Grade")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Aulas", len(st.session_state.grade_horaria.aulas))
        with col2:
            turmas_unicas = len(set(a.turma for a in st.session_state.grade_horaria.aulas))
            st.metric("Turmas Atendidas", turmas_unicas)
        with col3:
            salas_utilizadas = len(set(a.sala for a in st.session_state.grade_horaria.aulas))
            st.metric("Salas Utilizadas", salas_utilizadas)
        
        st.divider()
        st.subheader("📥 Exportação")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Exportar para CSV", use_container_width=True):
                df = pd.DataFrame([{
                    'Dia': a.dia.capitalize(),
                    'Horário': HORARIOS_REAIS[a.horario],
                    'Turma': a.turma,
                    'Disciplina': a.disciplina,
                    'Professor': a.professor,
                    'Sala': a.sala
                } for a in st.session_state.grade_horaria.aulas])
                
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Baixar CSV",
                    data=csv,
                    file_name=f"grade_horaria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with col2:
            if st.button("Gerar Nova Grade", use_container_width=True):
                st.session_state.grade_gerada = False
                st.session_state.grade_horaria = GradeHoraria()
                st.rerun()

# ============================================================================
# ABA 6: RELATÓRIOS
# ============================================================================

with aba_relatorios:
    st.header("📊 Relatórios")
    
    if not st.session_state.grade_gerada:
        st.warning("⚠️ Nenhuma grade gerada. Gere uma grade primeiro.")
    else:
        st.subheader("📈 Distribuição de Aulas")
        
        profs = [a.professor for a in st.session_state.grade_horaria.aulas]
        df_profs = pd.DataFrame(profs, columns=["Professor"])
        prof_count = df_profs["Professor"].value_counts().reset_index()
        prof_count.columns = ["Professor", "Aulas"]
        
        st.subheader("Aulas por Professor")
        st.bar_chart(prof_count.set_index("Professor"))
        
        discs = [a.disciplina for a in st.session_state.grade_horaria.aulas]
        df_discs = pd.DataFrame(discs, columns=["Disciplina"])
        disc_count = df_discs["Disciplina"].value_counts().reset_index()
        disc_count.columns = ["Disciplina", "Aulas"]
        
        st.subheader("Aulas por Disciplina")
        st.bar_chart(disc_count.set_index("Disciplina"))
        
        dias = [a.dia.capitalize() for a in st.session_state.grade_horaria.aulas]
        df_dias = pd.DataFrame(dias, columns=["Dia"])
        dia_count = df_dias["Dia"].value_counts().reset_index()
        dia_count.columns = ["Dia", "Aulas"]
        
        st.subheader("Aulas por Dia da Semana")
        st.bar_chart(dia_count.set_index("Dia"))

st.divider()
st.markdown("*GELEIA - Gerador de Grade Horária Escolar v1.0*")
