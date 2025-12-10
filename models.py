"""
models.py - Definição de todas as classes do sistema
Estrutura de dados para Turmas, Professores, Disciplinas, Salas e Aulas
"""

from dataclasses import dataclass, field
import uuid
from typing import List, Dict, Optional

# ============================================================================
# CONSTANTES
# ============================================================================

DIAS_SEMANA = ["segunda", "terça", "quarta", "quinta", "sexta"]

HORARIOS_EFII = {
    0: "07:50-08:40",
    1: "08:40-09:30",
    2: "09:30-09:50",  # Intervalo
    3: "09:50-10:40",
    4: "10:40-11:30",
    5: "11:30-12:20"
}

HORARIOS_EM = {
    0: "07:00-07:50",
    1: "07:50-08:40",
    2: "08:40-09:30",
    3: "09:30-09:50",  # Intervalo
    4: "09:50-10:40",
    5: "10:40-11:30",
    6: "11:30-12:20"
}

HORARIOS_REAIS = {
    "EF_II": HORARIOS_EFII,
    "EM": HORARIOS_EM
}

# ============================================================================
# CLASSES[1][3][4]
# ============================================================================

@dataclass
class Turma:
    """Representa uma turma escolar"""
    nome: str
    serie: str
    turno: str
    grupo: str = "A"
    segmento: str = "EF_II"
    capacidade: int = 25
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        if self.grupo not in ["A", "B"]:
            self.grupo = "A"
        if self.segmento not in ["EF_II", "EM"]:
            self.segmento = "EF_II"
        if self.capacidade < 1:
            self.capacidade = 25


@dataclass
class Professor:
    """Representa um professor"""
    nome: str
    disciplinas: List[str] = field(default_factory=list)
    disponibilidade: Dict[str, bool] = field(default_factory=lambda: {
        dia: True for dia in DIAS_SEMANA
    })
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        if not self.nome:
            raise ValueError("Nome do professor não pode estar vazio")
        for dia in DIAS_SEMANA:
            if dia not in self.disponibilidade:
                self.disponibilidade[dia] = True


@dataclass
class Disciplina:
    """Representa uma disciplina escolar"""
    nome: str
    carga_semanal: int = 3
    tipo: str = "media"
    turmas: List[str] = field(default_factory=list)
    grupo: str = "A"
    cor_fundo: str = "#4A90E2"
    cor_fonte: str = "#FFFFFF"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        if not self.nome:
            raise ValueError("Nome da disciplina não pode estar vazio")
        if self.carga_semanal < 1:
            self.carga_semanal = 1
        if self.carga_semanal > 10:
            self.carga_semanal = 10
        if self.tipo not in ["pesada", "media", "leve", "pratica"]:
            self.tipo = "media"
        if self.grupo not in ["A", "B"]:
            self.grupo = "A"


@dataclass
class Sala:
    """Representa uma sala de aula"""
    nome: str
    capacidade: int = 25
    tipo: str = "normal"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        if not self.nome:
            raise ValueError("Nome da sala não pode estar vazio")
        if self.capacidade < 1:
            self.capacidade = 25
        if self.tipo not in ["normal", "laboratorio", "auditorio"]:
            self.tipo = "normal"


@dataclass
class Aula:
    """Representa uma aula na grade horária"""
    turma: str
    disciplina: str
    professor: str
    sala: str
    dia: str
    horario: int
    grupo: str = "A"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        if self.dia not in DIAS_SEMANA:
            raise ValueError(f"Dia inválido: {self.dia}")
        if self.horario < 0:
            raise ValueError("Horário não pode ser negativo")
        if self.grupo not in ["A", "B"]:
            self.grupo = "A"
    
    def __repr__(self) -> str:
        return f"Aula({self.turma} - {self.disciplina} com {self.professor} na {self.sala})"


@dataclass
class GradeHoraria:
    """Representa a grade horária completa"""
    aulas: List[Aula] = field(default_factory=list)
    data_criacao: str = ""
    data_atualizacao: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def adicionar_aula(self, aula: Aula) -> bool:
        """Adiciona uma aula à grade"""
        if not self._validar_aula(aula):
            return False
        self.aulas.append(aula)
        return True
    
    def _validar_aula(self, aula: Aula) -> bool:
        """Valida se a aula pode ser adicionada"""
        for aula_existente in self.aulas:
            # Professor não pode estar em dois lugares ao mesmo tempo
            if (aula_existente.professor == aula.professor and
                aula_existente.dia == aula.dia and
                aula_existente.horario == aula.horario):
                return False
            
            # Sala não pode estar em dois lugares ao mesmo tempo
            if (aula_existente.sala == aula.sala and
                aula_existente.dia == aula.dia and
                aula_existente.horario == aula.horario):
                return False
        
        return True
    
    def remover_aula(self, aula_id: str) -> bool:
        """Remove uma aula da grade"""
        self.aulas = [a for a in self.aulas if a.id != aula_id]
        return True


# ============================================================================
# FUNÇÕES DE SERIALIZAÇÃO[1][2]
# ============================================================================

def turma_para_dict(turma: Turma) -> dict:
    return {
        'nome': turma.nome,
        'serie': turma.serie,
        'turno': turma.turno,
        'grupo': turma.grupo,
        'segmento': turma.segmento,
        'capacidade': turma.capacidade,
        'id': turma.id
    }


def dict_para_turma(data: dict) -> Turma:
    return Turma(
        nome=data.get('nome', 'Turma'),
        serie=data.get('serie', '6'),
        turno=data.get('turno', 'Matutino'),
        grupo=data.get('grupo', 'A'),
        segmento=data.get('segmento', 'EF_II'),
        capacidade=data.get('capacidade', 25),
        id=data.get('id', str(uuid.uuid4()))
    )


def professor_para_dict(prof: Professor) -> dict:
    return {
        'nome': prof.nome,
        'disciplinas': prof.disciplinas,
        'disponibilidade': prof.disponibilidade,
        'id': prof.id
    }


def dict_para_professor(data: dict) -> Professor:
    return Professor(
        nome=data.get('nome', 'Professor'),
        disciplinas=data.get('disciplinas', []),
        disponibilidade=data.get('disponibilidade', {dia: True for dia in DIAS_SEMANA}),
        id=data.get('id', str(uuid.uuid4()))
    )


def disciplina_para_dict(disc: Disciplina) -> dict:
    return {
        'nome': disc.nome,
        'carga_semanal': disc.carga_semanal,
        'tipo': disc.tipo,
        'turmas': disc.turmas,
        'grupo': disc.grupo,
        'cor_fundo': disc.cor_fundo,
        'cor_fonte': disc.cor_fonte,
        'id': disc.id
    }


def dict_para_disciplina(data: dict) -> Disciplina:
    return Disciplina(
        nome=data.get('nome', 'Disciplina'),
        carga_semanal=data.get('carga_semanal', 3),
        tipo=data.get('tipo', 'media'),
        turmas=data.get('turmas', []),
        grupo=data.get('grupo', 'A'),
        cor_fundo=data.get('cor_fundo', '#4A90E2'),
        cor_fonte=data.get('cor_fonte', '#FFFFFF'),
        id=data.get('id', str(uuid.uuid4()))
    )


def sala_para_dict(sala: Sala) -> dict:
    return {
        'nome': sala.nome,
        'capacidade': sala.capacidade,
        'tipo': sala.tipo,
        'id': sala.id
    }


def dict_para_sala(data: dict) -> Sala:
    return Sala(
        nome=data.get('nome', 'Sala'),
        capacidade=data.get('capacidade', 25),
        tipo=data.get('tipo', 'normal'),
        id=data.get('id', str(uuid.uuid4()))
    )
