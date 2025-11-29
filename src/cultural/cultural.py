import sys
import os
import random
import copy
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from src.helperFunctions.readFromCSV import read_dataset

goal = read_dataset('small')
pop_count = 100
generations = 50

class belief_space(object):
    def __init__(self):
        self.situational = None  
        self.normative = {
            'best_fitness': float('inf'),
            'avg_fitness': 0,
            'machine_load_distribution': {},
            'job_affinity': {}  # Track which jobs perform well on which machines
        }
    
    def update_situational(self, individual):
        """Track the best solution found so far"""
        if self.situational is None or individual.fitness < self.situational.fitness:
            self.situational = copy.deepcopy(individual)
            self.normative['best_fitness'] = individual.fitness
    
    def update_normative(self, population):
        """Learn patterns from top performers"""
        # Sort by fitness (lower is better)
        sorted_pop = sorted(population, key=lambda x: x.fitness)
        top_performers = sorted_pop[:max(1, len(sorted_pop) // 4)]  # Top 25%
        
        # Update average fitness
        fitness_values = [ind.fitness for ind in population]
        self.normative['avg_fitness'] = sum(fitness_values) / len(fitness_values)
        
        # Learn machine load patterns from top performers
        # Each task value may be (start, exec) or exec; sum exec times
        def machine_total_load(tasks):
            total = 0
            for task_dict in tasks:
                for v in task_dict.values():
                    total += v[1] if isinstance(v, tuple) else v
            return total

        self.normative['machine_load_distribution'] = {}
        for ind in top_performers:
            for machine, tasks in ind.timeline.items():
                total_load = machine_total_load(tasks)
                if machine not in self.normative['machine_load_distribution']:
                    self.normative['machine_load_distribution'][machine] = []
                self.normative['machine_load_distribution'][machine].append(total_load)

        # Calculate average load per machine from top performers
        for machine in list(self.normative['machine_load_distribution'].keys()):
            loads = self.normative['machine_load_distribution'][machine]
            self.normative['machine_load_distribution'][machine] = sum(loads) / len(loads)
        
        # Learn job-to-machine affinity from top performers
        self.normative['job_affinity'] = {}
        for ind in top_performers:
            for machine, tasks in ind.timeline.items():
                for task_dict in tasks:
                    for (job_id, task_id), val in task_dict.items():
                        # count occurrences of job on machines (val may be tuple)
                        if job_id not in self.normative['job_affinity']:
                            self.normative['job_affinity'][job_id] = {}
                        if machine not in self.normative['job_affinity'][job_id]:
                            self.normative['job_affinity'][job_id][machine] = 0
                        self.normative['job_affinity'][job_id][machine] += 1



class individual(object):
    def __init__(self,timeline):
        self.timeline = timeline
        self.fitness = self.calc_fitness()


    @classmethod
    def initialize_individual(self):
        global goal
        clone = copy.deepcopy(goal)
        timeline = {}
        
        for _ in range(clone['total_tasks']):
            job = random.randint(0,clone['total_jobs'] - 1)
            task = clone['jobs'][job]['tasks'].pop(0)
            jobId = clone['jobs'][job]['job_id']

            if not clone['jobs'][job]['tasks']:
                clone['jobs'].pop(job)
                clone['total_jobs'] -= 1


            wait_time = 0
            machine = random.randint(1,clone['machines_count'])


            if task['task_id'] != 1:
                last_task_start, last_task_exec = 0,0
                for machine, lst in timeline.items():
                    for d in lst:
                        if (jobId,task['task_id'] - 1) in d:
                            last_task_start, last_task_exec = d[(jobId,task['task_id'] - 1)]
                            break
                prev_start,prev_exec = list(timeline[machine][-1].values())[0]
                wait_time = (last_task_start + last_task_exec) - (prev_start + prev_exec)
                if (wait_time < 0): 
                    wait_time = 0
            
            if machine not in timeline:
                timeline[machine] = []
                timeline[machine].append({ (jobId,task['task_id']) : (0 + wait_time, task['execution_time'])  })   
            else:
                prev_start,prev_exec = list(timeline[machine][-1].values())[0]
                timeline[machine].append({ (jobId,task['task_id']) : (prev_start + prev_exec + wait_time, task['execution_time'])  })
        
        return individual(timeline)
    
    
    def calc_fitness(self):
        timeline = self.timeline
        total_time = {k: 0 for k in timeline}  

        for key in timeline:  
            for task_dict in timeline[key]:
                total_machine_time , total_execution_time = list(timeline[key][-1].values())[0]
                total_time[key] = total_execution_time + total_machine_time
        fitness = max(total_time.values())
        for i in total_time:
            fitness += max(total_time.values()) - total_time[i]
        return fitness

    def influence_from_belief_space(self, belief_space):        
    

def main():
    population=[]
    for i in range(pop_count):
        population.append(individual.initialize_individual())

    belief = belief_space()
    belief.update_situational(min(population, key=lambda ind: ind.fitness))
    print(belief.situational.timeline)
    belief.update_normative(population)
    for i in range(generations):
        for ind in population:
            ind.influence_from_belief_space(belief)
        belief.update_situational(min(population, key=lambda ind: ind.fitness))
        belief.update_normative(population)
        print("gen:", i, ":", belief.situational.fitness)
    print("Best fitness after influence:", belief.situational.fitness)
    print("Best timeline after influence:", belief.situational.timeline)
main()
