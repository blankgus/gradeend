import streamlit as st
from models import Turma, Professor, Disciplina, Sala
from database import salvar_tudo  # Importação atualizada

st.set_page_config(page_title="Dados Rápidos", page_icon="⚡")

st.title("⚡ Carregar Dados Padrão")
st.write("Carregue dados de exemplo para testar rapidamente o sistema")

col1, col2 = st.columns(2)

with col1:
    if st.button("📚 Carregar Turmas Padrão", use_container_width=True):
        turmas = [            Turma("6anoA", "6", "matutino"),
            Turma("6anoB", "6", "matutino"),
            Turma("7anoA", "7", "matutino"),
            Turma("7anoB", "7", "matutino"),
            Turma("8anoA", "8", "matutino"),
            Turma("8anoB", "8", "matutino"),
        ]
        st.session_state.turmas = turmas
        
        # Atualizado: salvar TUDO mantendo dados existentes
        salvar_tudo(
            turmas,
            st.session_state.get('professores', []),
            st.session_state.get('disciplinas', []),
            st.session_state.get('salas', [])
        )
        st.success(f"✅ {len(turmas)} turmas carregadas!")

with col2:
    if st.button("👨‍🏫 Carregar Professores Padrão", use_container_width=True):
        professores = [            Professor("João Silva", ["Português", "Literatura"]),
            Professor("Maria Santos", ["Matemática"]),
            Professor("Carlos Oliveira", ["Ciências", "Biologia"]),
            Professor("Ana Costa", ["História", "Geografia"]),
            Professor("Pedro Ferreira", ["Educação Física"]),
        ]
        st.session_state.professores = professores
        
        # Atualizado: salvar TUDO mantendo dados existentes
        salvar_tudo(
            st.session_state.get('turmas', []),
            professores,
            st.session_state.get('disciplinas', []),
            st.session_state.get('salas', [])
        )
        st.success(f"✅ {len(professores)} professores carregados!")

col1, col2 = st.columns(2)

with col1:
    if st.button("📖 Carregar Disciplinas Padrão", use_container_width=True):
        disciplinas = [            Disciplina("Português", 4, "media", ["6", "7", "8"], "#D35400", "#FFFFFF"),
            Disciplina("Matemática", 4, "media", ["6", "7", "8"], "#4A90E2", "#FFFFFF"),
            Disciplina("Ciências", 3, "media", ["6", "7", "8"], "#1ABC9C", "#000000"),
            Disciplina("História", 3, "media", ["6", "7", "8"], "#C0392B", "#FFFFFF"),
            Disciplina("Geografia", 2, "media", ["6", "7", "8"], "#F39C12", "#000000"),
            Disciplina("Educação Física", 2, "media", ["6", "7", "8"], "#2ECC71", "#000000"),
            Disciplina("Literatura", 2, "media", ["7", "8"], "#9B59B6", "#FFFFFF"),
            Disciplina("Biologia", 3, "media", ["8"], "#27AE60", "#FFFFFF"),
        ]
        st.session_state.disciplinas = disciplinas
        
        # Atualizado: salvar TUDO mantendo dados existentes
        salvar_tudo(
            st.session_state.get('turmas', []),
            st.session_state.get('professores', []),
            disciplinas,
            st.session_state.get('salas', [])
        )
        st.success(f"✅ {len(disciplinas)} disciplinas carregadas!")

with col2:
    if st.button("🚪 Carregar Salas Padrão", use_container_width=True):
        salas = [            Sala("Sala 1", 30, "normal"),
            Sala("Sala 2", 30, "normal"),
            Sala("Sala 3", 30, "normal"),
            Sala("Laboratório", 25, "laboratorio"),
            Sala("Auditório", 60, "auditorio"),
        ]
        st.session_state.salas = salas
        
        # Atualizado: salvar TUDO mantendo dados existentes
        salvar_tudo(
            st.session_state.get('turmas', []),
            st.session_state.get('professores', []),
            st.session_state.get('disciplinas', []),
            salas
        )
        st.success(f"✅ {len(salas)} salas carregadas!")

st.divider()

if st.button("🚀 Carregar TUDO de Uma Vez", use_container_width=True, type="primary"):
    turmas = [        Turma("6anoA", "6", "matutino"),
        Turma("6anoB", "6", "matutino"),
        Turma("7anoA", "7", "matutino"),
        Turma("7anoB", "7", "matutino"),
        Turma("8anoA", "8", "matutino"),
        Turma("8anoB", "8", "matutino"),
    ]
    
    professores = [        Professor("João Silva", ["Português", "Literatura"]),
        Professor("Maria Santos", ["Matemática"]),
        Professor("Carlos Oliveira", ["Ciências", "Biologia"]),
        Professor("Ana Costa", ["História", "Geografia"]),
        Professor("Pedro Ferreira", ["Educação Física"]),
    ]
    
    disciplinas = [        Disciplina("Português", 4, "media", ["6", "7", "8"], "#D35400", "#FFFFFF"),
        Disciplina("Matemática", 4, "media", ["6", "7", "8"], "#4A90E2", "#FFFFFF"),
        Disciplina("Ciências", 3, "media", ["6", "7", "8"], "#1ABC9C", "#000000"),
        Disciplina("História", 3, "media", ["6", "7", "8"], "#C0392B", "#FFFFFF"),
        Disciplina("Geografia", 2, "media", ["6", "7", "8"], "#F39C12", "#000000"),
        Disciplina("Educação Física", 2, "media", ["6", "7", "8"], "#2ECC71", "#000000"),
        Disciplina("Literatura", 2, "media", ["7", "8"], "#9B59B6", "#FFFFFF"),
        Disciplina("Biologia", 3, "media", ["8"], "#27AE60", "#FFFFFF"),
    ]
    
    salas = [        Sala("Sala 1", 30, "normal"),
        Sala("Sala 2", 30, "normal"),
        Sala("Sala 3", 30, "normal"),
        Sala("Laboratório", 25, "laboratorio"),
        Sala("Auditório", 60, "auditorio"),
    ]
    
    st.session_state.turmas = turmas
    st.session_state.professores = professores
    st.session_state.disciplinas = disciplinas
    st.session_state.salas = salas
    
    # Atualizado: usar salvar_tudo() uma única vez
    salvar_tudo(turmas, professores, disciplinas, salas)
    
    st.success("✅ Sistema carregado com dados de teste!")
    st.balloons()
