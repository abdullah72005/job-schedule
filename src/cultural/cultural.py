import sys
import os
import random
import copy
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from src.helperFunctions.readFromCSV import read_dataset

goal = read_dataset('large')
pop_count = 1000
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
        self.normative['machine_load_distribution'] = {}
        for ind in top_performers:
            for machine, tasks in ind.timeline.items():
                total_load = sum(sum(task_dict.values()) for task_dict in tasks)
                if machine not in self.normative['machine_load_distribution']:
                    self.normative['machine_load_distribution'][machine] = []
                self.normative['machine_load_distribution'][machine].append(total_load)
        
        # Calculate average load per machine from top performers
        for machine in self.normative['machine_load_distribution']:
            loads = self.normative['machine_load_distribution'][machine]
            self.normative['machine_load_distribution'][machine] = sum(loads) / len(loads)
        
        # Learn job-to-machine affinity from top performers
        self.normative['job_affinity'] = {}
        for ind in top_performers:
            for machine, tasks in ind.timeline.items():
                for task_dict in tasks:
                    for (job_id, task_id), exec_time in task_dict.items():
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
        """Apply cultural influence to improve solution based on belief space"""
        # Get learned patterns
        job_affinity = belief_space.normative.get('job_affinity', {})
        machine_loads = belief_space.normative.get('machine_load_distribution', {})
        best_fitness = belief_space.normative.get('best_fitness', float('inf'))
        
        # Only apply influence if current individual is worse than best found
        if self.fitness > best_fitness * 1.1:  # 10% worse than best
            # Step 1: Identify overloaded machines
            current_loads = {}
            for machine, tasks in self.timeline.items():
                current_loads[machine] = sum(sum(task_dict.values()) for task_dict in tasks)
            
            # Step 2: Try to rebalance by moving tasks from overloaded to underloaded machines
            sorted_machines = sorted(current_loads.items(), key=lambda x: x[1], reverse=True)
            
            if len(sorted_machines) > 1:
                overloaded = sorted_machines[0][0]
                underloaded = sorted_machines[-1][0]
                
                # Try moving a task from overloaded to underloaded
                if overloaded in self.timeline and self.timeline[overloaded]:
                    # Pick a task that prefers the underloaded machine based on affinity
                    best_task_idx = 0
                    if job_affinity:
                        for idx, task_dict in enumerate(self.timeline[overloaded]):
                            for (job_id, _), _ in task_dict.items():
                                if job_id in job_affinity:
                                    if underloaded in job_affinity[job_id]:
                                        best_task_idx = idx
                                        break
                    
                    # Move the task
                    task_to_move = self.timeline[overloaded].pop(best_task_idx)
                    if underloaded not in self.timeline:
                        self.timeline[underloaded] = []
                    self.timeline[underloaded].append(task_to_move)
                    
                    # Clean up empty machines
                    if not self.timeline[overloaded]:
                        del self.timeline[overloaded]
                    
                    # Recalculate fitness
                    self.fitness = self.calc_fitness()
        
        

def main():
    population=[]
    for i in range(pop_count):
        population.append(individual.initialize_individual())

    belief = belief_space()
    belief.update_situational(min(population, key=lambda ind: ind.fitness))
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