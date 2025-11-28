import sys
import os
import random
import copy
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from src.helperFunctions.readFromCSV import read_dataset

goal = read_dataset('large')
pop_count = 100
generations = 50

class belief_space(object):
    def __init__(self):
        self.situational = None  
        self.normative = {}
    def update_situational(self, individual):
        if self.situational is None or individual.fitness < self.situational.fitness:
            self.situational = copy.deepcopy(individual)
    def update_normative(self, population):
        fitness_values = [ind.fitness for ind in population]
        avg_fitness = sum(fitness_values) / len(fitness_values)
        viable_jobs = set()
        for ind in population:
            if ind.fitness <= avg_fitness:
                for machine, tasks in ind.timeline.items():
                    for task_dict in tasks:
                        for job_task in task_dict.keys():
                            viable_jobs.add(job_task[0])  
        self.normative['viable_jobs'] = viable_jobs



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
            if not clone['jobs'][job]['tasks']:
                clone['jobs'].pop(job)
                clone['total_jobs'] -= 1
            machine = random.randint(1,clone['machines_count'])
            if machine not in timeline:
                timeline[machine] = []
            timeline[machine].append({ (job,task['task_id']) : task['execution_time'] })   
        return individual(timeline)
    
    
    def calc_fitness(self):
        timeline = self.timeline
        total_time = {k: 0 for k in timeline}  

        for key in timeline:  
            for task_dict in timeline[key]:
                for time in task_dict.values():
                    total_time[key] += time
        fitness = max(total_time.values())
        for i in total_time:
            fitness += max(total_time.values()) - total_time[i]
        return fitness
    
    def influence_from_belief_space(self, belief_space):
        viable_jobs = belief_space.normative.get('viable_jobs', set())
        new_timeline = {}
        for machine, tasks in self.timeline.items():
            new_tasks = []
            for task_dict in tasks:
                for job_task in task_dict.keys():
                    if job_task[0] in viable_jobs:
                        new_tasks.append(task_dict)
            if new_tasks:
                new_timeline[machine] = new_tasks
        if new_timeline:
            self.timeline = new_timeline
            self.fitness = self.calc_fitness()
        
    

def main():
    population=[]
    for i in range(pop_count):
        population.append(individual.initialize_individual())

    belief = belief_space()
    belief.update_situational(min(population, key=lambda ind: ind.fitness))
    belief.update_normative(population)
    for _ in range(generations):
        for ind in population:
            ind.influence_from_belief_space(belief)
        belief.update_situational(min(population, key=lambda ind: ind.fitness))
        belief.update_normative(population)
    print("Best fitness after influence:", belief.situational.fitness)
    print("Best timeline after influence:", belief.situational.timeline)
main()