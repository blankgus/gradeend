"""
database.py - Gerenciamento de persistência de dados
VERSÃO FINAL - Tratamento robusto com validação completa
"""

import json
from pathlib import Path
from typing import List, Tuple, Dict, Any

from models import Turma, Professor, Disciplina, Sala

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

DB_DIR = Path("data")
DB_DIR.mkdir(exist_ok=True)

TURMAS_FILE = DB_DIR / "turmas.json"
PROFESSORES_FILE = DB_DIR / "professores.json"
DISCIPLINAS_FILE = DB_DIR / "disciplinas.json"
SALAS_FILE = DB_DIR / "salas.json"

# ============================================================================
# CONVERSÃO: OBJETO → DICT
# ============================================================================

def turma_para_dict(turma: Turma) -> Dict[str, Any]:
    """Converte Turma para Dict"""
    if not isinstance(turma, Turma):
        return None
    return {
        'id': turma.id,
        'nome': turma.nome,
        'semestre': turma.semestre,
        'curso': turma.curso,
        'quantidade_alunos': turma.quantidade_alunos
    }

def professor_para_dict(professor: Professor) -> Dict[str, Any]:
    """Converte Professor para Dict"""
    if not isinstance(professor, Professor):
        return None
    return {
        'id': professor.id,
        'nome': professor.nome,
        'disciplinas': professor.disciplinas if isinstance(professor.disciplinas, list) else []
    }

def disciplina_para_dict(disciplina: Disciplina) -> Dict[str, Any]:
    """Converte Disciplina para Dict"""
    if not isinstance(disciplina, Disciplina):
        return None
    return {
        'id': disciplina.id,
        'nome': disciplina.nome,
        'carga_semanal': disciplina.carga_semanal,
        'turmas': disciplina.turmas if isinstance(disciplina.turmas, list) else []
    }

def sala_para_dict(sala: Sala) -> Dict[str, Any]:
    """Converte Sala para Dict"""
    if not isinstance(sala, Sala):
        return None
    return {
        'id': sala.id,
        'nome': sala.nome,
        'capacidade': sala.capacidade,
        'predio': sala.predio,
        'andar': sala.andar
    }

# ============================================================================
# RECONVERSÃO: DICT → OBJETO
# ============================================================================

def dict_para_turma(data: Dict) -> Turma:
    """Reconverte Dict para Turma"""
    try:
        if not isinstance(data, dict):
            return None
        return Turma(
            nome=str(data.get('nome', 'Turma Sem Nome')),
            semestre=int(data.get('semestre', 1)),
            curso=str(data.get('curso', 'Curso Padrão')),
            quantidade_alunos=int(data.get('quantidade_alunos', 0))
        )
    except Exception as e:
        print(f"❌ Erro reconverter Turma: {e}")
        return None

def dict_para_professor(data: Dict) -> Professor:
    """Reconverte Dict para Professor"""
    try:
        if not isinstance(data, dict):
            return None
        disciplinas = data.get('disciplinas', [])
        if not isinstance(disciplinas, list):
            disciplinas = []
        return Professor(
            nome=str(data.get('nome', 'Professor Sem Nome')),
            disciplinas=disciplinas
        )
    except Exception as e:
        print(f"❌ Erro reconverter Professor: {e}")
        return None

def dict_para_disciplina(data: Dict) -> Disciplina:
    """Reconverte Dict para Disciplina"""
    try:
        if not isinstance(data, dict):
            return None
        turmas = data.get('turmas', [])
        if not isinstance(turmas, list):
            turmas = []
        return Disciplina(
            nome=str(data.get('nome', 'Disciplina Sem Nome')),
            carga_semanal=int(data.get('carga_semanal', 0)),
            turmas=turmas
        )
    except Exception as e:
        print(f"❌ Erro reconverter Disciplina: {e}")
        return None

def dict_para_sala(data: Dict) -> Sala:
    """Reconverte Dict para Sala"""
    try:
        if not isinstance(data, dict):
            return None
        return Sala(
            nome=str(data.get('nome', 'Sala Sem Nome')),
            capacidade=int(data.get('capacidade', 0)),
            predio=str(data.get('predio', 'Prédio Padrão')),
            andar=int(data.get('andar', 0))
        )
    except Exception as e:
        print(f"❌ Erro reconverter Sala: {e}")
        return None

# ============================================================================
# SALVAMENTO
# ============================================================================

def salvar_turmas(turmas: List[Turma]) -> bool:
    """Salva turmas em JSON"""
    try:
        dados = []
        for t in turmas:
            if isinstance(t, Turma):
                d = turma_para_dict(t)
                if d:
                    dados.append(d)
        
        with open(TURMAS_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Erro salvar turmas: {e}")
        return False

def salvar_professores(professores: List[Professor]) -> bool:
    """Salva professores em JSON"""
    try:
        dados = []
        for p in professores:
            if isinstance(p, Professor):
                d = professor_para_dict(p)
                if d:
                    dados.append(d)
        
        with open(PROFESSORES_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Erro salvar professores: {e}")
        return False

def salvar_disciplinas(disciplinas: List[Disciplina]) -> bool:
    """Salva disciplinas em JSON"""
    try:
        dados = []
        for d in disciplinas:
            if isinstance(d, Disciplina):
                dat = disciplina_para_dict(d)
                if dat:
                    dados.append(dat)
        
        with open(DISCIPLINAS_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Erro salvar disciplinas: {e}")
        return False

def salvar_salas(salas: List[Sala]) -> bool:
    """Salva salas em JSON"""
    try:
        dados = []
        for s in salas:
            if isinstance(s, Sala):
                d = sala_para_dict(s)
                if d:
                    dados.append(d)
        
        with open(SALAS_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Erro salvar salas: {e}")
        return False

def salvar_tudo(turmas: List, professores: List, disciplinas: List, salas: List) -> bool:
    """Salva todos os dados"""
    return (
        salvar_turmas(turmas) and
        salvar_professores(professores) and
        salvar_disciplinas(disciplinas) and
        salvar_salas(salas)
    )

# ============================================================================
# CARREGAMENTO
# ============================================================================

def carregar_turmas() -> List[Dict]:
    """Carrega turmas de JSON"""
    try:
        if not TURMAS_FILE.exists():
            return []
        with open(TURMAS_FILE, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            return dados if isinstance(dados, list) else []
    except Exception as e:
        print(f"❌ Erro carregar turmas: {e}")
        return []

def carregar_professores() -> List[Dict]:
    """Carrega professores de JSON"""
    try:
        if not PROFESSORES_FILE.exists():
            return []
        with open(PROFESSORES_FILE, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            return dados if isinstance(dados, list) else []
    except Exception as e:
        print(f"❌ Erro carregar professores: {e}")
        return []

def carregar_disciplinas() -> List[Dict]:
    """Carrega disciplinas de JSON"""
    try:
        if not DISCIPLINAS_FILE.exists():
            return []
        with open(DISCIPLINAS_FILE, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            return dados if isinstance(dados, list) else []
    except Exception as e:
        print(f"❌ Erro carregar disciplinas: {e}")
        return []

def carregar_salas() -> List[Dict]:
    """Carrega salas de JSON"""
    try:
        if not SALAS_FILE.exists():
            return []
        with open(SALAS_FILE, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            return dados if isinstance(dados, list) else []
    except Exception as e:
        print(f"❌ Erro carregar salas: {e}")
        return []

def carregar_tudo() -> Tuple[List[Dict], List[Dict], List[Dict], List[Dict]]:
    """Carrega todos os dados"""
    return (
        carregar_turmas(),
        carregar_professores(),
        carregar_disciplinas(),
        carregar_salas()
    )

# ============================================================================
# LIMPEZA
# ============================================================================

def limpar_banco() -> bool:
    """Limpa todos os arquivos do banco"""
    try:
        for arquivo in [TURMAS_FILE, PROFESSORES_FILE, DISCIPLINAS_FILE, SALAS_FILE]:
            if arquivo.exists():
                arquivo.unlink()
        return True
    except Exception as e:
        print(f"❌ Erro limpar banco: {e}")
        return False
