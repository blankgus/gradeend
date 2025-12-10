from ortools.sat.python import cp_model
from models import Aula

class GradeHorariaSolver:
    """Solver profissional usando Google OR-Tools[1][6]"""
    
    def __init__(self, turmas, professores, disciplinas, salas):
        self.turmas = turmas
        self.professores = professores
        self.disciplinas = disciplinas
        self.salas = salas
        self.aulas = []
        self.erros = []
    
    def gerar(self):
        """Gera grade sem conflitos[1][6]"""
        try:
            model = cp_model.CpModel()
            
            dias = ["seg", "ter", "qua", "qui", "sex"]
            horarios = [1, 2, 4, 5, 6]
            
            # Variáveis de decisão
            aulas_vars = []
            
            for turma in self.turmas:
                for disc in self.disciplinas:
                    if turma.serie in disc.turmas:
                        # Encontrar professor
                        prof = next((p for p in self.professores if disc.nome in p.disciplinas), None)
                        if not prof:
                            continue
                        
                        # Cada aula semanal
                        for _ in range(disc.carga_semanal):
                            for dia in dias:
                                for horario in horarios:
                                    for sala in self.salas:
                                        var = model.NewBoolVar(f'{turma.nome}_{disc.nome}_{prof.nome}_{dia}_{horario}_{sala.nome}')
                                        aulas_vars.append((var, turma, disc, prof, dia, horario, sala))
            
            # Restrição 1: Cada aula agendada exatamente 1 vez
            aulas_por_grupo = {}
            for var, turma, disc, prof, dia, horario, sala in aulas_vars:
                chave = (turma.nome, disc.nome, prof.nome)
                if chave not in aulas_por_grupo:
                    aulas_por_grupo[chave] = []
                aulas_por_grupo[chave].append(var)
            
            for vars_grupo in aulas_por_grupo.values():
                model.Add(sum(vars_grupo) == 1)
            
            # Restrição 2: Professor não pode estar em 2 turmas ao mesmo tempo[1]
            for dia in dias:
                for horario in horarios:
                    for prof in self.professores:
                        prof_vars = [var for var, t, d, p, di, h, s in aulas_vars 
                                    if p.nome == prof.nome and di == dia and h == horario]
                        if prof_vars:
                            model.Add(sum(prof_vars) <= 1)
            
            # Restrição 3: Sala não pode ter 2 turmas ao mesmo tempo[1]
            for dia in dias:
                for horario in horarios:
                    for sala in self.salas:
                        sala_vars = [var for var, t, d, p, di, h, s in aulas_vars 
                                    if s.nome == sala.nome and di == dia and h == horario]
                        if sala_vars:
                            model.Add(sum(sala_vars) <= 1)
            
            # Restrição 4: Turma não pode ter 2 aulas ao mesmo tempo[1]
            for turma in self.turmas:
                for dia in dias:
                    for horario in horarios:
                        turma_vars = [var for var, t, d, p, di, h, s in aulas_vars 
                                     if t.nome == turma.nome and di == dia and h == horario]
                        if turma_vars:
                            model.Add(sum(turma_vars) <= 1)
            
            # Resolver[1]
            solver = cp_model.CpSolver()
            status = solver.Solve(model)
            
            if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
                for var, turma, disc, prof, dia, horario, sala in aulas_vars:
                    if solver.Value(var):
                        self.aulas.append(Aula(
                            turma=turma.nome,
                            disciplina=disc.nome,
                            professor=prof.nome,
                            dia=dia,
                            horario=horario,
                            sala=sala.nome
                        ))
                return True
            else:
                self.erros.append("⚠️ Não há solução viável com as restrições atuais")
                return False
        
        except Exception as e:
            self.erros.append(f"❌ Erro: {str(e)}")
            return False
    
    def obter_aulas(self):
        return self.aulas
    
    def obter_erros(self):
        return self.erros
