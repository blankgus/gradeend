"""
auto_save.py - Função de auto-salvamento
"""

import database
import streamlit as st
from datetime import datetime


def salvar_tudo() -> bool:
    """
    Salva todos os dados da sessão no banco de dados
    Retorna True se bem-sucedido, False caso contrário
    """
    try:
        # Salvar cada tipo de dado
        sucesso = True
        
        sucesso = sucesso and database.salvar_turmas(st.session_state.turmas)
        sucesso = sucesso and database.salvar_professores(st.session_state.professores)
        sucesso = sucesso and database.salvar_disciplinas(st.session_state.disciplinas)
        sucesso = sucesso and database.salvar_salas(st.session_state.salas)
        
        if sucesso:
            st.session_state.timestamp_ultima_atualizacao = datetime.now()
        
        return sucesso
    
    except Exception as e:
        st.error(f"❌ Erro ao salvar: {str(e)}")
        return False


def carregar_tudo() -> bool:
    """Carrega todos os dados do banco de dados"""
    try:
        st.session_state.turmas = database.carregar_turmas()
        st.session_state.professores = database.carregar_professores()
        st.session_state.disciplinas = database.carregar_disciplinas()
        st.session_state.salas = database.carregar_salas()
        return True
    except Exception as e:
        st.error(f"❌ Erro ao carregar: {str(e)}")
        return False
