"""
simple_scheduler.py - Gerador de grade horária com Google OR-Tools
VERSÃO FINAL - Otimização inteligente
"""

from typing import List, Dict, Set, Tuple
from ortools.sat.python import cp_model
from models import Turma, Professor, Disciplina, Sala, Aula, GradeHoraria, DIAS_SEMANA

class SimpleGradeHoraria:
    def __init__(self, turmas: List[Turma], professores: List[Professor], 
                 disciplinas: List[Disciplina], salas: List[Sala]):
        self.turmas = [t for t in turmas if isinstance(t, Turma)]
        self.professores = [p for p in professores if isinstance(p, Professor)]
        self.disciplinas = [d for d in disciplinas if isinstance(d, Disciplina)]
        self.salas = [s for s in salas if isinstance(s, Sala)]
    
    def gerar_grade(self) -> GradeHoraria:
        """Gera grade horária usando OR-Tools CP-SAT"""
        grade = GradeHoraria()
        
        # Validação
        if not all([self.turmas, self.professores, self.disciplinas, self.salas]):
            print("⚠️ Dados insuficientes")
            return grade
        
        # Criar modelo CP-SAT
        model = cp_model.CpModel()
        
        # Variáveis
        aulas_vars = {}  # (turma, disciplina, dia, horario, sala, prof) -> variável booleana
        
        # Dados
        dias_idx = list(range(len(DIAS_SEMANA)))
        horarios_idx = [0, 1]
        
        # ===== CRIAR VARIÁVEIS =====
        for turma in self.turmas:
            for disciplina in self.disciplinas:
                if turma.nome not in disciplina.turmas:
                    continue
                
                # Encontrar professor da disciplina
                prof = None
                for p in self.professores:
                    if disciplina.nome in p.disciplinas:
                        prof = p
                        break
                
                if not prof:
                    continue
                
                # Criar variáveis para cada combinação possível
                for dia_idx in dias_idx:
                    for hora_idx in horarios_idx:
                        for sala in self.salas:
                            var_name = f"{turma.nome}_{disciplina.nome}_{dia_idx}_{hora_idx}_{sala.nome}"
                            aulas_vars[(turma.nome, disciplina.nome, dia_idx, hora_idx, sala.nome, prof.nome)] = \
                                model.NewBoolVar(var_name)
        
        # ===== RESTRIÇÕES =====
        
        # 1. Cada turma não pode ter 2 aulas no mesmo horário
        for turma in self.turmas:
            for dia_idx in dias_idx:
                for hora_idx in horarios_idx:
                    vars_turma_hora = [
                        var for (t, d, di, h, s, p), var in aulas_vars.items()
                        if t == turma.nome and di == dia_idx and h == hora_idx
                    ]
                    if vars_turma_hora:
                        model.Add(sum(vars_turma_hora) <= 1)
        
        # 2. Cada professor não pode ensinar 2 aulas no mesmo horário
        for professor in self.professores:
            for dia_idx in dias_idx:
                for hora_idx in horarios_idx:
                    vars_prof_hora = [
                        var for (t, d, di, h, s, p), var in aulas_vars.items()
                        if p == professor.nome and di == dia_idx and h == hora_idx
                    ]
                    if vars_prof_hora:
                        model.Add(sum(vars_prof_hora) <= 1)
        
        # 3. Cada sala não pode ter 2 aulas no mesmo horário
        for sala in self.salas:
            for dia_idx in dias_idx:
                for hora_idx in horarios_idx:
                    vars_sala_hora = [
                        var for (t, d, di, h, s, p), var in aulas_vars.items()
                        if s == sala.nome and di == dia_idx and h == hora_idx
                    ]
                    if vars_sala_hora:
                        model.Add(sum(vars_sala_hora) <= 1)
        
        # 4. Cumprir carga horária de cada disciplina
        for turma in self.turmas:
            for disciplina in self.disciplinas:
                if turma.nome not in disciplina.turmas:
                    continue
                
                vars_disciplina = [
                    var for (t, d, di, h, s, p), var in aulas_vars.items()
                    if t == turma.nome and d == disciplina.nome
                ]
                
                if vars_disciplina:
                    model.Add(sum(vars_disciplina) == disciplina.carga_semanal)
        
        # ===== OBJECTIVE: Minimizar conflitos =====
        model.Minimize(0)  # Sem função objetivo específica, apenas viabilidade
        
        # ===== RESOLVER =====
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10
        status = solver.Solve(model)
        
        # ===== EXTRAIR SOLUÇÃO =====
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            for (turma_nome, disc_nome, dia_idx, hora_idx, sala_nome, prof_nome), var in aulas_vars.items():
                if solver.Value(var) == 1:
                    aula = Aula(
                        disciplina=disc_nome,
                        professor=prof_nome,
                        sala=sala_nome,
                        dia=DIAS_SEMANA[dia_idx],
                        horario=hora_idx,
                        turma=turma_nome
                    )
                    grade.adicionar_aula(aula)
        else:
            print("⚠️ Nenhuma solução viável encontrada. Gerando grade simples...")
            grade = self._gerar_grade_simples()
        
        return grade
    
    def _gerar_grade_simples(self) -> GradeHoraria:
        """Fallback: gera grade simples sem OR-Tools"""
        import random
        
        grade = GradeHoraria()
        slots_ocupados = set()
        
        for disciplina in self.disciplinas:
            if not isinstance(disciplina, Disciplina):
                continue
            
            for turma_nome in disciplina.turmas:
                turma = self._buscar_turma(turma_nome)
                if not turma:
                    continue
                
                professor = self._buscar_professor_disciplina(disciplina.nome)
                if not professor:
                    continue
                
                for _ in range(disciplina.carga_semanal):
                    aula_criada = False
                    tentativas = 0
                    
                    while not aula_criada and tentativas < 20:
                        dia = random.choice(DIAS_SEMANA)
                        horario = random.choice([0, 1])
                        sala = random.choice(self.salas)
                        
                        slot = (turma.nome, dia, horario)
                        
                        if slot not in slots_ocupados:
                            slots_ocupados.add(slot)
                            
                            aula = Aula(
                                disciplina=disciplina.nome,
                                professor=professor.nome,
                                sala=sala.nome,
                                dia=dia,
                                horario=horario,
                                turma=turma.nome
                            )
                            grade.adicionar_aula(aula)
                            aula_criada = True
                        
                        tentativas += 1
        
        return grade
    
    def _buscar_turma(self, nome: str) -> Turma:
        """Busca turma por nome"""
        for t in self.turmas:
            if isinstance(t, Turma) and t.nome == nome:
                return t
        return None
    
    def _buscar_professor_disciplina(self, disciplina: str) -> Professor:
        """Busca professor que ensina a disciplina"""
        for p in self.professores:
            if isinstance(p, Professor) and disciplina in p.disciplinas:
                return p
        return None
