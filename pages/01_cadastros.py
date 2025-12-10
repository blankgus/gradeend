import streamlit as st
import database
from models import Turma, Professor, Disciplina, Sala

st.set_page_config(page_title="Cadastros", page_icon="➕")

st.title("➕ Cadastro de Dados")

tab1, tab2, tab3, tab4 = st.tabs(["Turmas", "Professores", "Disciplinas", "Salas"])

# ============ TURMAS ============
with tab1:
    st.subheader("Cadastrar Turma")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        nome_turma = st.text_input("Nome da Turma", placeholder="Ex: 6anoA")
    with col2:
        serie = st.selectbox("Série", ["6", "7", "8", "9", "1em", "2em", "3em"])
    with col3:
        turno = st.selectbox("Turno", ["matutino", "vespertino", "noturno"])
    
    if st.button("✅ Adicionar Turma", key="btn_turma"):
        if nome_turma:
            nova_turma = Turma(nome=nome_turma, serie=serie, turno=turno)
            st.session_state.turmas.append(nova_turma)
            database.salvar_turmas(st.session_state.turmas)
            st.success(f"✅ Turma {nome_turma} cadastrada!")
            st.rerun()
    
    st.divider()
    st.subheader("Turmas Cadastradas")
    
    if st.session_state.turmas:
        df_turmas = []
        for t in st.session_state.turmas:
            df_turmas.append({
                "Nome": t.nome,
                "Série": t.serie,
                "Turno": t.turno
            })
        
        import pandas as pd
        st.dataframe(pd.DataFrame(df_turmas), use_container_width=True, hide_index=True)
        
        # Remover turma
        turma_remover = st.selectbox("Remover turma:", [t.nome for t in st.session_state.turmas], key="remove_turma")
        if st.button("🗑️ Remover", key="btn_remove_turma"):
            st.session_state.turmas = [t for t in st.session_state.turmas if t.nome != turma_remover]
            database.salvar_turmas(st.session_state.turmas)
            st.success("✅ Turma removida!")
            st.rerun()
    else:
        st.info("Nenhuma turma cadastrada")

# ============ PROFESSORES ============
with tab2:
    st.subheader("Cadastrar Professor")
    
    col1, col2 = st.columns(2)
    with col1:
        nome_prof = st.text_input("Nome do Professor", placeholder="Ex: João Silva")
    with col2:
        disciplinas_selecionadas = st.multiselect(
            "Disciplinas que leciona",
            [d.nome for d in st.session_state.disciplinas],
            key="disc_prof"
        )
    
    if st.button("✅ Adicionar Professor", key="btn_prof"):
        if nome_prof and disciplinas_selecionadas:
            novo_prof = Professor(nome=nome_prof, disciplinas=disciplinas_selecionadas)
            st.session_state.professores.append(novo_prof)
            database.salvar_professores(st.session_state.professores)
            st.success(f"✅ Professor {nome_prof} cadastrado!")
            st.rerun()
        else:
            st.error("Preencha nome e selecione disciplinas")
    
    st.divider()
    st.subheader("Professores Cadastrados")
    
    if st.session_state.professores:
        import pandas as pd
        df_profs = []
        for p in st.session_state.professores:
            df_profs.append({
                "Nome": p.nome,
                "Disciplinas": ", ".join(p.disciplinas)
            })
        
        st.dataframe(pd.DataFrame(df_profs), use_container_width=True, hide_index=True)
        
        # Remover professor
        prof_remover = st.selectbox("Remover professor:", [p.nome for p in st.session_state.professores], key="remove_prof")
        if st.button("🗑️ Remover", key="btn_remove_prof"):
            st.session_state.professores = [p for p in st.session_state.professores if p.nome != prof_remover]
            database.salvar_professores(st.session_state.professores)
            st.success("✅ Professor removido!")
            st.rerun()
    else:
        st.info("Nenhum professor cadastrado")

# ============ DISCIPLINAS ============
with tab3:
    st.subheader("Cadastrar Disciplina")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        nome_disc = st.text_input("Nome da Disciplina", placeholder="Ex: Português")
    with col2:
        carga_semanal = st.number_input("Carga Semanal (aulas/semana)", min_value=1, max_value=10, value=2)
    with col3:
        tipo = st.selectbox("Tipo", ["media", "pesada", "leve"])
    
    col1, col2 = st.columns(2)
    with col1:
        cor_fundo = st.color_picker("Cor Fundo", "#4A90E2")
    with col2:
        cor_fonte = st.color_picker("Cor Fonte", "#FFFFFF")
    
    series_selecionadas = st.multiselect("Séries que usam:", ["6", "7", "8", "9", "1em", "2em", "3em"])
    
    if st.button("✅ Adicionar Disciplina", key="btn_disc"):
        if nome_disc and series_selecionadas:
            nova_disc = Disciplina(
                nome=nome_disc,
                carga_semanal=carga_semanal,
                tipo=tipo,
                turmas=series_selecionadas,
                cor_fundo=cor_fundo,
                cor_fonte=cor_fonte
            )
            st.session_state.disciplinas.append(nova_disc)
            database.salvar_disciplinas(st.session_state.disciplinas)
            st.success(f"✅ Disciplina {nome_disc} cadastrada!")
            st.rerun()
        else:
            st.error("Preencha nome e selecione séries")
    
    st.divider()
    st.subheader("Disciplinas Cadastradas")
    
    if st.session_state.disciplinas:
        import pandas as pd
        df_discs = []
        for d in st.session_state.disciplinas:
            df_discs.append({
                "Nome": d.nome,
                "Carga": d.carga_semanal,
                "Tipo": d.tipo,
                "Séries": ", ".join(d.turmas)
            })
        
        st.dataframe(pd.DataFrame(df_discs), use_container_width=True, hide_index=True)
        
        # Remover disciplina
        disc_remover = st.selectbox("Remover disciplina:", [d.nome for d in st.session_state.disciplinas], key="remove_disc")
        if st.button("🗑️ Remover", key="btn_remove_disc"):
            st.session_state.disciplinas = [d for d in st.session_state.disciplinas if d.nome != disc_remover]
            database.salvar_disciplinas(st.session_state.disciplinas)
            st.success("✅ Disciplina removida!")
            st.rerun()
    else:
        st.info("Nenhuma disciplina cadastrada")

# ============ SALAS ============
with tab4:
    st.subheader("Cadastrar Sala")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        nome_sala = st.text_input("Nome da Sala", placeholder="Ex: Sala 1")
    with col2:
        capacidade = st.number_input("Capacidade", min_value=10, max_value=200, value=30)
    with col3:
        tipo_sala = st.selectbox("Tipo", ["normal", "laboratorio", "auditorio", "informatica"])
    
    if st.button("✅ Adicionar Sala", key="btn_sala"):
        if nome_sala:
            nova_sala = Sala(nome=nome_sala, capacidade=capacidade, tipo=tipo_sala)
            st.session_state.salas.append(nova_sala)
            database.salvar_salas(st.session_state.salas)
            st.success(f"✅ Sala {nome_sala} cadastrada!")
            st.rerun()
    
    st.divider()
    st.subheader("Salas Cadastradas")
    
    if st.session_state.salas:
        import pandas as pd
        df_salas = []
        for s in st.session_state.salas:
            df_salas.append({
                "Nome": s.nome,
                "Capacidade": s.capacidade,
                "Tipo": s.tipo
            })
        
        st.dataframe(pd.DataFrame(df_salas), use_container_width=True, hide_index=True)
        
        # Remover sala
        sala_remover = st.selectbox("Remover sala:", [s.nome for s in st.session_state.salas], key="remove_sala")
        if st.button("🗑️ Remover", key="btn_remove_sala"):
            st.session_state.salas = [s for s in st.session_state.salas if s.nome != sala_remover]
            database.salvar_salas(st.session_state.salas)
            st.success("✅ Sala removida!")
            st.rerun()
    else:
        st.info("Nenhuma sala cadastrada")
