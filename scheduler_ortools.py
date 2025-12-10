"""
scheduler_ortools.py - Gerador de grade horária com OR-Tools
"""

import streamlit as st
from models import Aula, GradeHoraria, DIAS_SEMANA
from typing import List, Dict

try:
    from ortools.sat.python import cp_model
    ORTOOLS_DISPONIVEL = True
except ImportError:
    ORTOOLS_DISPONIVEL = False


class GradeHorariaORTools:
    """Gerador de grade horária com otimização via OR-Tools"""
    
    def __init__(self):
        self.grade = GradeHoraria()
        self.erros = []
        
        if not ORTOOLS_DISPONIVEL:
            st.warning("⚠️ OR-Tools não instalado. Use: pip install ortools")
    
    def gerar(self, turmas, professores, disciplinas, salas) -> GradeHoraria:
        """
        Gera a grade horária usando OR-Tools
        
        Args:
            turmas: Lista de Turma
            professores: Lista de Professor
            disciplinas: Lista de Disciplina
            salas: Lista de Sala
            
        Returns:
            GradeHoraria: Grade horária gerada
        """
        if not ORTOOLS_DISPONIVEL:
            st.error("❌ OR-Tools não disponível. Instale com: pip install ortools")
            return self.grade
        
        try:
            st.info("⏳ Gerando grade com OR-Tools...")
            
            # Criar modelo
            model = cp_model.CpModel()
            
            # Variáveis de decisão: (turma, disc, prof, sala, dia, hora)
            aulas_vars = {}
            
            for turma in turmas:
                for disciplina in disciplinas:
                    if turma.nome not in disciplina.turmas:
                        continue
                    
                    for professor in professores:
                        if disciplina.nome not in professor.disciplinas:
                            continue
                        
                        for sala in salas:
                            for dia_idx, dia in enumerate(DIAS_SEMANA):
                                if not professor.disponibilidade.get(dia, True):
                                    continue
                                
                                for horario in range(6):
                                    var_key = (turma.nome, disciplina.nome, professor.nome, sala.nome, dia, horario)
                                    aulas_vars[var_key] = model.NewBoolVar(f'aula_{len(aulas_vars)}')
            
            # Restrições: cada disciplina deve ter suas aulas atribuídas
            for turma in turmas:
                for disciplina in disciplinas:
                    if turma.nome in disciplina.turmas:
                        vars_disc = [v for k, v in aulas_vars.items() 
                                    if k == turma.nome and k[1] == disciplina.nome]
                        
                        if vars_disc:
                            model.Add(sum(vars_disc) == disciplina.carga_semanal)
            
            # Restrição: professor não pode estar em dois lugares ao mesmo tempo
            for professor in professores:
                for dia in DIAS_SEMANA:
                    for horario in range(6):
                        vars_prof = [v for k, v in aulas_vars.items()
                                    if k[2] == professor.nome and k[4] == dia and k[5] == horario]
                        
                        if vars_prof:
                            model.Add(sum(vars_prof) <= 1)
            
            # Restrição: sala não pode ter duas aulas ao mesmo tempo
            for sala in salas:
                for dia in DIAS_SEMANA:
                    for horario in range(6):
                        vars_sala = [v for k, v in aulas_vars.items()
                                    if k[3] == sala.nome and k[4] == dia and k[5] == horario]
                        
                        if vars_sala:
                            model.Add(sum(vars_sala) <= 1)
            
            # Resolver
            solver = cp_model.CpSolver()
            status = solver.Solve(model)
            
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                # Extrair solução
                for (turma, disc, prof, sala, dia, hora), var in aulas_vars.items():
                    if solver.Value(var):
                        aula = Aula(
                            turma=turma,
                            disciplina=disc,
                            professor=prof,
                            sala=sala,
                            dia=dia,
                            horario=hora
                        )
                        self.grade.aulas.append(aula)
                
                st.success(f"✅ Grade otimizada gerada com {len(self.grade.aulas)} aulas")
            else:
                st.warning("⚠️ Não foi possível gerar uma grade viável")
            
            return self.grade
        
        except Exception as e:
            st.error(f"❌ Erro ao gerar grade: {str(e)}")
            return self.grade
