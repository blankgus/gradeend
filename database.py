"""
database.py - Gerenciamento de persistência de dados
"""

import json
from pathlib import Path
from typing import List, Tuple

from models import (
    Turma, Professor, Disciplina, Sala,
    turma_para_dict, dict_para_turma,
    professor_para_dict, dict_para_professor,
    disciplina_para_dict, dict_para_disciplina,
    sala_para_dict, dict_para_sala
)

# ============================================================================
# CONFIGURAÇÃO DE CAMINHOS
# ============================================================================

DATA_DIR = Path(__file__).parent / "data"
DATA_FILE = DATA_DIR / "escola_data.json"

DATA_DIR.mkdir(exist_ok=True)

# ============================================================================
# FUNÇÃO 1: SALVAR TUDO (EXPORTADA - OBRIGATÓRIA)
# ============================================================================

def salvar_tudo(turmas: List[Turma], 
                professores: List[Professor], 
                disciplinas: List[Disciplina], 
                salas: List[Sala]) -> bool:
    """
    Salva TODOS os dados em um único arquivo JSON
    
    Args:
        turmas: Lista de Turma
        professores: Lista de Professor
        disciplinas: Lista de Disciplina
        salas: Lista de Sala
        
    Returns:
        bool: True se salvou com sucesso, False caso contrário
    """
    try:
        dados = {
            "turmas": [turma_para_dict(t) for t in turmas],
            "professores": [professor_para_dict(p) for p in professores],
            "disciplinas": [disciplina_para_dict(d) for d in disciplinas],
            "salas": [sala_para_dict(s) for s in salas]
        }
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
            
        return True
    except Exception as e:
        print(f"Erro ao salvar dados: {e}")
        return False


# ============================================================================
# FUNÇÃO 2: CARREGAR TUDO (EXPORTADA - OBRIGATÓRIA)
# ============================================================================

def carregar_tudo() -> Tuple[List[Turma], List[Professor], List[Disciplina], List[Sala]]:
    """
    Carrega TODOS os dados do arquivo JSON
    
    Returns:
        Tuple com (turmas, professores, disciplinas, salas)
    """
    try:
        if not DATA_FILE.exists():
            return [], [], [], []
            
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            
        turmas = [dict_para_turma(t) for t in dados.get("turmas", [])]
        professores = [dict_para_professor(p) for p in dados.get("professores", [])]
        disciplinas = [dict_para_disciplina(d) for d in dados.get("disciplinas", [])]
        salas = [dict_para_sala(s) for s in dados.get("salas", [])]
        
        return turmas, professores, disciplinas, salas
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return [], [], [], []


# ============================================================================
# FUNÇÃO 3: LIMPAR BANCO (EXPORTADA - OBRIGATÓRIA)
# ============================================================================

def limpar_banco() -> bool:
    """
    Remove o arquivo de dados do banco
    
    Returns:
        bool: True se limpou com sucesso
    """
    try:
        if DATA_FILE.exists():
            DATA_FILE.unlink()
        return True
    except Exception as e:
        print(f"Erro ao limpar banco: {e}")
        return False
