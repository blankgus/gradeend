"""
models.py - Modelos de dados
VERSÃO FINAL - Classes bem estruturadas
"""

import uuid
from typing import List

DIAS_SEMANA = ['segunda', 'terca', 'quarta', 'quinta', 'sexta']
HORARIOS_REAIS = {0: '08:00-10:00', 1: '10:30-12:30'}

# ============================================================================
# CLASSE: Turma
# ============================================================================

class Turma:
    def __init__(self, nome: str, semestre: int, curso: str, quantidade_alunos: int):
        self.id = str(uuid.uuid4())[:8]
        self.nome = nome
        self.semestre = semestre
        self.curso = curso
        self.quantidade_alunos = quantidade_alunos
    
    def __repr__(self):
        return f"Turma({self.nome}, {self.semestre}º, {self.curso})"

# ============================================================================
# CLASSE: Professor
# ============================================================================

class Professor:
    def __init__(self, nome: str, disciplinas: List[str] = None):
        self.id = str(uuid.uuid4())[:8]
        self.nome = nome
        self.disciplinas = disciplinas if disciplinas else []
    
    def __repr__(self):
        return f"Professor({self.nome})"

# ============================================================================
# CLASSE: Disciplina
# ============================================================================

class Disciplina:
    def __init__(self, nome: str, carga_semanal: int, turmas: List[str] = None):
        self.id = str(uuid.uuid4())[:8]
        self.nome = nome
        self.carga_semanal = carga_semanal
        self.turmas = turmas if turmas else []
    
    def __repr__(self):
        return f"Disciplina({self.nome}, {self.carga_semanal}h)"

# ============================================================================
# CLASSE: Sala
# ============================================================================

class Sala:
    def __init__(self, nome: str, capacidade: int, predio: str, andar: int):
        self.id = str(uuid.uuid4())[:8]
        self.nome = nome
        self.capacidade = capacidade
        self.predio = predio
        self.andar = andar
    
    def __repr__(self):
        return f"Sala({self.nome}, {self.predio} - Andar {self.andar})"

# ============================================================================
# CLASSE: Aula
# ============================================================================

class Aula:
    def __init__(self, disciplina: str, professor: str, sala: str, dia: str, horario: int, turma: str):
        self.id = str(uuid.uuid4())[:8]
        self.disciplina = disciplina
        self.professor = professor
        self.sala = sala
        self.dia = dia
        self.horario = horario
        self.turma = turma
    
    def __repr__(self):
        return f"Aula({self.disciplina}, {self.professor}, {self.sala})"

# ============================================================================
# CLASSE: GradeHoraria
# ============================================================================

class GradeHoraria:
    def __init__(self, aulas: List[Aula] = None):
        self.id = str(uuid.uuid4())[:8]
        self.aulas = aulas if aulas else []
    
    def adicionar_aula(self, aula: Aula):
        self.aulas.append(aula)
    
    def __repr__(self):
        return f"GradeHoraria({len(self.aulas)} aulas)"
