"""
session_state.py - Gerenciamento do estado da sessão Streamlit
"""

import streamlit as st
import database
from models import Turma, Professor, Disciplina, Sala

def init_session_state():
    """Inicializa o estado da sessão com dados persistidos"""
    
    if 'turmas' not in st.session_state:
        st.session_state.turmas = database.carregar_turmas()
    
    if 'professores' not in st.session_state:
        st.session_state.professores = database.carregar_professores()
    
    if 'disciplinas' not in st.session_state:
        st.session_state.disciplinas = database.carregar_disciplinas()
    
    if 'salas' not in st.session_state:
        st.session_state.salas = database.carregar_salas()
    
    if 'grade_gerada' not in st.session_state:
        st.session_state.grade_gerada = False
    
    if 'timestamp_ultima_atualizacao' not in st.session_state:
        st.session_state.timestamp_ultima_atualizacao = None


def limpar_session_state():
    """Limpa o estado da sessão"""
    keys_para_limpar = ['turmas', 'professores', 'disciplinas', 'salas', 'grade_gerada']
    for key in keys_para_limpar:
        if key in st.session_state:
            del st.session_state[key]


def resetar_session_state():
    """Reseta para o estado inicial"""
    limpar_session_state()
    init_session_state()
