import sys
import os
import random
import copy
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from src.helperFunctions.readFromCSV import read_dataset

goal = None
pop_count = 1000
generations = 100

class belief_space(object):
    def __init__(self):
        self.situational = None
        self.normative = None
    
    def update_situational(self, individual):
        self.situational = copy.deepcopy(individual)
    
    def update_normative(self, population):
        fitness_values = [ind.fitness for ind in population]
        avg_machine_time = 0
        for ind in population:
            timeline = ind.timeline
            total_time = {k: 0 for k in timeline}  

            for key in timeline:  
                for task_dict in timeline[key]:
                    total_machine_time , total_execution_time = list(timeline[key][-1].values())[0]
                    total_time[key] = total_execution_time + total_machine_time
            avg_machine_time += sum(total_time.values()) / len(total_time)
        avg_machine_time /= len(population)
        self.normative = {
            'best_fitness': min(fitness_values),
            'worst_fitness': max(fitness_values),
            'avg_fitness': sum(fitness_values) / len(fitness_values),
            'population_size': len(population),
            'avg_machine_time':avg_machine_time
        }
    
    def get_belief_influence(self):
        return {
            'best_solution': self.situational,
            'normative_info': self.normative
        }

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
        idle_time = 0
        makespan = 0
        for machine, tasks in timeline.items(): 
            pastValue = 0
            machine_end_time = pastValue
            idle_time += makespan - machine_end_time
            last_task = tasks[-1]
            # Idle time between tasks
            for task_dict in tasks:
                for task in task_dict.values():
                    start , duration = task
                    idle_time += start - pastValue
                    pastValue = start + duration
                    total_machine_time , total_execution_time_machine = task_dict
                    machine_completion_time = total_machine_time + total_execution_time_machine
                    if machine_completion_time > makespan:
                        makespan = machine_completion_time
            

        return fitness

    def influence_from_belief_space(self, belief_space):
        """Apply influence from belief space to modify individual's solution"""
        # Get belief influences
        beliefs = belief_space.get_belief_influence()
        best_solution = beliefs['best_solution']
        normative_info = beliefs['normative_info']


        if self.fitness > normative_info['avg_fitness']:
            # If individual is worse than average, move toward best solution
            influence_factor = random.uniform(0.1, 0.5)
            
            # Apply influence by mixing current solution with best solution
            self.timeline = self._apply_influence(self.timeline, best_solution.timeline, influence_factor)
            self.fitness = self.calc_fitness()
        
        return self.fitness
    
    def _apply_influence(self, current_timeline, best_timeline, factor):
        
        # Extract all tasks from current timeline with their execution times
        all_tasks = []
        for machine in current_timeline:
            for task_dict in current_timeline[machine]:
                for (jobId, task_id), (start_time, exec_time) in task_dict.items():
                    all_tasks.append({
                        'jobId': jobId,
                        'task_id': task_id,
                        'exec_time': exec_time,
                        'current_machine': machine
                    })
        
        # Sort tasks by job and task_id to process in order
        all_tasks.sort(key=lambda x: (x['jobId'], x['task_id']))
        
        # Build new timeline respecting all constraints
        influenced_timeline = {}
        job_task_completion_times = {}  # Track when each (jobId, task_id) finishes
        machine_end_times = {}  # Track when each machine becomes free
        
        for task_info in all_tasks:
            jobId = task_info['jobId']
            task_id = task_info['task_id']
            exec_time = task_info['exec_time']
            task_key = (jobId, task_id)
            
            # Probabilistically adopt machine from best solution
            new_machine = task_info['current_machine']
            if random.random() < factor:
                # Find this task in best solution and use its machine
                for machine in best_timeline:
                    for task_dict in best_timeline[machine]:
                        if task_key in task_dict:
                            new_machine = machine
                            break
            
            # Calculate earliest start time respecting constraints
            earliest_start = 0
            
            # Constraint 1: Task must start after its prerequisite (task_id - 1) completes
            if task_id > 1:
                prerequisite_key = (jobId, task_id - 1)
                if prerequisite_key in job_task_completion_times:
                    earliest_start = max(earliest_start, job_task_completion_times[prerequisite_key])
            
            # Constraint 2: Task must start after machine is free
            if new_machine in machine_end_times:
                earliest_start = max(earliest_start, machine_end_times[new_machine])
            
            # Schedule task on the chosen machine
            if new_machine not in influenced_timeline:
                influenced_timeline[new_machine] = []
            
            start_time = earliest_start
            end_time = start_time + exec_time
            
            influenced_timeline[new_machine].append({task_key: (start_time, exec_time)})
            job_task_completion_times[task_key] = end_time
            machine_end_times[new_machine] = end_time
        
        return influenced_timeline
    
    def _apply_influence(self, current_timeline, best_timeline, factor):
        
        # Extract all tasks from current timeline with their execution times
        all_tasks = []
        for machine in current_timeline:
            for task_dict in current_timeline[machine]:
                for (jobId, task_id), (start_time, exec_time) in task_dict.items():
                    all_tasks.append({
                        'jobId': jobId,
                        'task_id': task_id,
                        'exec_time': exec_time,
                        'current_machine': machine
                    })
        
        # Sort tasks by job and task_id to process in order
        all_tasks.sort(key=lambda x: (x['jobId'], x['task_id']))
        
        # Build new timeline respecting all constraints
        influenced_timeline = {}
        job_task_completion_times = {}  # Track when each (jobId, task_id) finishes
        machine_end_times = {}  # Track when each machine becomes free
        
        for task_info in all_tasks:
            jobId = task_info['jobId']
            task_id = task_info['task_id']
            exec_time = task_info['exec_time']
            task_key = (jobId, task_id)
            
            # Probabilistically adopt machine from best solution
            new_machine = task_info['current_machine']
            if random.random() < factor:
                # Find this task in best solution and use its machine
                for machine in best_timeline:
                    for task_dict in best_timeline[machine]:
                        if task_key in task_dict:
                            new_machine = machine
                            break
            
            # Calculate earliest start time respecting constraints
            earliest_start = 0
            
            # Constraint 1: Task must start after its prerequisite (task_id - 1) completes
            if task_id > 1:
                prerequisite_key = (jobId, task_id - 1)
                if prerequisite_key in job_task_completion_times:
                    earliest_start = max(earliest_start, job_task_completion_times[prerequisite_key])
            
            # Constraint 2: Task must start after machine is free
            if new_machine in machine_end_times:
                earliest_start = max(earliest_start, machine_end_times[new_machine])
            
            # Schedule task on the chosen machine
            if new_machine not in influenced_timeline:
                influenced_timeline[new_machine] = []
            
            start_time = earliest_start
            end_time = start_time + exec_time
            
            influenced_timeline[new_machine].append({task_key: (start_time, exec_time)})
            job_task_completion_times[task_key] = end_time
            machine_end_times[new_machine] = end_time
        
        return influenced_timeline

def _cultural_algorithm(generation_callback=None):
    population=[]
    for i in range(pop_count):
        population.append(individual.initialize_individual())

    belief = belief_space()
    belief.update_situational(min(population, key=lambda ind: ind.fitness))
    belief.update_normative(population)
    fitness_history = []
    for i in range(generations):
        for ind in population:
            ind.influence_from_belief_space(belief)
        belief.update_situational(min(population, key=lambda ind: ind.fitness))
        belief.update_normative(population)
        fitness_history.append(belief.situational.fitness)
        
        # Call the callback if provided (for GUI updates)
        if generation_callback:
            generation_callback(i + 1, belief.situational.fitness)
        else:
            print(f"Generation {i+1}: Best Fitness = {belief.situational.fitness}")
    print("Best timeline:", belief.situational.timeline)
    
    return belief.situational.timeline, belief.situational.fitness, fitness_history


def cultural_algorithm(res, generation_callback=None):
    global goal
    goal = res

    return _cultural_algorithm(generation_callback=generation_callback)

def get_metrics(timeline, exec_time):
    metrics = {}
    makespan = 0
    idle_time = 0
    total_execution_time = 0

    # First pass: find makespan and total execution time
    for machine, tasks in timeline.items(): 
        if tasks:
            last_task = tasks[-1]
            for task_dict in last_task.values():
                total_machine_time , total_execution_time_machine = task_dict
                machine_completion_time = total_machine_time + total_execution_time_machine
                if machine_completion_time > makespan:
                    makespan = machine_completion_time
            
            for task_dict in tasks:
                for task in task_dict.values():
                    start , duration = task
                    total_execution_time += duration  # Add all execution times

    # Second pass: calculate idle time (between tasks and at the end of machines)
    for machine, tasks in timeline.items(): 
        if tasks:
            pastValue = 0
            # Idle time between tasks
            for task_dict in tasks:
                for task in task_dict.values():
                    start , duration = task
                    idle_time += start - pastValue
                    pastValue = start + duration
            
            # Idle time at the end of machine execution
            machine_end_time = pastValue
            idle_time += makespan - machine_end_time

    # Calculate utilization
    total_available_time = makespan * len(timeline)
    utilization = (total_execution_time / total_available_time * 100) if total_available_time > 0 else 0

    metrics["makespan"] = str(makespan) + " ms"
    metrics['idle_time'] = str(idle_time) + " ms"
    metrics['utilization'] = round(utilization, 2)
    metrics["execTime"] = str(round(exec_time, 2)) + ' s'


    return metrics

    


# def main():
#     res = read_dataset('large')

#     start_time = time.time()
#     bestTimeline, bestFitness, fitnessHistory = cultural_algorithm(res)
#     end_time = time.time()

#     exectime = end_time - start_time
#     # print("Best Fitness:", bestFitness)
#     # print("Best Timeline:", bestTimeline)
#     # print("Fitness History:", fitnessHistory)
#     metrics = get_metrics(bestTimeline, exectime)

#     print("makespan:   " + str(metrics['makespan']))
#     print("idle_time:   " + str(metrics['idle_time']))
#     print("utilization:   " + str(metrics['utilization']) + "%")
#     print("exectime:     " + str(metrics["execTime"]))
# main()
