import sys
import os
import random
import copy
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from src.helperFunctions.readFromCSV import read_dataset

goal = read_dataset('small')
pop_count = 100

class individual(object):
    def __init__(self,timeline):
        self.timeline = timeline
        self.fitness = self.calc_fitness()
        self.situational = None  
        self.normative = {}  
    # the normative belief space  belief space will include with jobs are viable at the current order
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
        print(timeline)     
        return individual(timeline)
    


def main():
    population=[]
    for i in range(pop_count):
        population.append(individual.initialize_individual())
        print(population[i].timeline)
main()