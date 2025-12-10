"""
simple_scheduler.py - Gerador de grade horária com algoritmo simples
"""

import streamlit as st
from models import Aula, GradeHoraria, DIAS_SEMANA
from typing import List, Dict, Tuple
import random


class SimpleGradeHoraria:
    """Gerador de grade horária com algoritmo simples e rápido"""
    
    def __init__(self):
        self.grade = GradeHoraria()
        self.erros = []
        self.avisos = []
    
    def gerar(self, turmas, professores, disciplinas, salas) -> GradeHoraria:
        """
        Gera a grade horária usando algoritmo simples
        
        Args:
            turmas: Lista de Turma
            professores: Lista de Professor
            disciplinas: Lista de Disciplina
            salas: Lista de Sala
            
        Returns:
            GradeHoraria: Grade horária gerada
        """
        try:
            st.info("⏳ Gerando grade com algoritmo simples...")
            
            for turma in turmas:
                self._atribuir_aulas_turma(turma, professores, disciplinas, salas)
            
            st.success(f"✅ Grade gerada com {len(self.grade.aulas)} aulas")
            
            if self.avisos:
                for aviso in self.avisos:
                    st.warning(aviso)
            
            return self.grade
        
        except Exception as e:
            st.error(f"❌ Erro ao gerar grade: {str(e)}")
            return self.grade
    
    def _atribuir_aulas_turma(self, turma, professores, disciplinas, salas):
        """Atribui aulas para uma turma específica"""
        dias_semana = DIAS_SEMANA
        horarios_utilizados = {}
        
        # Encontrar disciplinas para esta turma
        discs_turma = [d for d in disciplinas if turma.nome in d.turmas]
        
        for disciplina in discs_turma:
            # Encontrar professor que leciona essa disciplina
            prof = next((p for p in professores if disciplina.nome in p.disciplinas), None)
            
            if not prof:
                self.avisos.append(f"⚠️ Nenhum professor para {disciplina.nome}")
                continue
            
            # Atribuir as aulas da disciplina
            for _ in range(disciplina.carga_semanal):
                # Encontrar slot disponível
                dias_disponiveis = [d for d in DIAS_SEMANA if prof.disponibilidade.get(d, True)]
                
                if not dias_disponiveis:
                    self.avisos.append(f"⚠️ Professor {prof.nome} sem dias disponíveis")
                    continue
                
                dia = random.choice(dias_disponiveis)
                horario = self._encontrar_horario_disponivel(turma.nome, dia, horarios_utilizados)
                
                if horario is None:
                    self.avisos.append(f"⚠️ Sem horário disponível para {turma.nome} em {dia}")
                    continue
                
                # Encontrar sala disponível
                sala = self._encontrar_sala_disponivel(dia, horario, salas)
                
                if not sala:
                    self.avisos.append(f"⚠️ Sem sala disponível em {dia} às {horario}")
                    continue
                
                # Criar aula
                aula = Aula(
                    turma=turma.nome,
                    disciplina=disciplina.nome,
                    professor=prof.nome,
                    sala=sala.nome,
                    dia=dia,
                    horario=horario,
                    grupo=turma.grupo
                )
                
                if self.grade.adicionar_aula(aula):
                    # Marcar como utilizado
                    chave = (turma.nome, dia, horario)
                    horarios_utilizados[chave] = True
                else:
                    self.avisos.append(f"⚠️ Conflito ao adicionar aula {aula}")
    
    def _encontrar_horario_disponivel(self, turma_nome: str, dia: str, utilizados: Dict) -> int:
        """Encontra um horário disponível para a turma no dia especificado"""
        for horario in range(6):
            chave = (turma_nome, dia, horario)
            if chave not in utilizados:
                return horario
        return None
    
    def _encontrar_sala_disponivel(self, dia: str, horario: int, salas) -> object:
        """Encontra uma sala disponível"""
        salas_disponiveis = [s for s in salas]
        
        # Verificar quais salas estão ocupadas
        aulas_slot = [a for a in self.grade.aulas if a.dia == dia and a.horario == horario]
        salas_ocupadas = set(a.sala for a in aulas_slot)
        
        for sala in salas_disponiveis:
            if sala.nome not in salas_ocupadas:
                return sala
        
        return None
