import sys
import os
import copy
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from src.helperFunctions.readFromCSV import read_dataset
data = read_dataset('small')
class backTracking:
    def __init__(self):
        self.machines_count = data['machines_count']
        self.jobs = data['jobs']
        self.total_tasks = data['total_tasks']
        self.total_jobs = data['total_jobs']
        self.timeline = {}
        self.best_timeline = None
        self.best_makespan = float('inf')

        self.total_idle_time = 0
        self.machine_utilization = 0
        self.execution_time = 0
        
        self.nodes_visited = 0
        self.nodes_pruned = 0
        
    def _assign_task(self, task, machine, start_time):
        if machine not in self.timeline:
            self.timeline[machine] = []
        
        scheduled_task = {
            'job_id': task['job_id'],
            'task_id': task['task_id'],
            'execution_time': task['execution_time'],
            'start_time': start_time,
            'end_time': start_time + task['execution_time'],
            'machine': machine 
        }
        
        self.timeline[machine].append(scheduled_task)
    
    def _remove_task(self, task, machine):
        if machine in self.timeline:
            self.timeline[machine] = [
                t for t in self.timeline[machine] 
                if not (t['job_id'] == task['job_id'] and t['task_id'] == task['task_id'])
            ]
    
    def _find_previous_task_end_time(self, job_id, task_id):
        previous_task_end_time = 0
        
        for machine_timeline in self.timeline.values():
            for scheduled_task in machine_timeline:
                if (scheduled_task['job_id'] == job_id and 
                    scheduled_task['task_id'] == task_id - 1):
                    previous_task_end_time = scheduled_task['end_time']
                    break
        
        return previous_task_end_time
    
    def _sort_jobs(self):
        def job_total_time(job):
            return sum(task['execution_time'] for task in job['tasks'])
        
        self.jobs.sort(key=lambda job: -job_total_time(job))
    
    def _sort_machines(self):
        machine_loads = []
        for machine in range(self.machines_count):
            current_load = sum(t['execution_time'] for t in self.timeline.get(machine, []))
            machine_loads.append((current_load, machine))
        
        return [machine for load, machine in sorted(machine_loads)]

    def _find_earliest_start_time(self, task, machine):
        job_id = task['job_id']
        task_id = task['task_id']
        execution_time = task['execution_time']
        
        earliest_start = 0
        
        if task_id > 1:
            previous_task_end_time = self._find_previous_task_end_time(job_id, task_id)
            earliest_start = max(earliest_start, previous_task_end_time)
        
        if machine in self.timeline:
            machine_tasks = sorted(self.timeline[machine], key=lambda t: t['start_time'])
            
            for scheduled_task in machine_tasks:
                if earliest_start + execution_time <= scheduled_task['start_time']:
                    break
                
                earliest_start = max(earliest_start, scheduled_task['end_time'])
        
        return earliest_start
    
    def _calculate_makespan(self):
        makespan = 0
        for machine_timeline in self.timeline.values():
            for task in machine_timeline:
                makespan = max(makespan, task['end_time'])
        return makespan

    def _checkConstraints(self, task, machine, start_time):
        job_id = task['job_id']
        task_id = task['task_id']
        execution_time = task['execution_time']
        end_time = start_time + execution_time
        
        if machine not in self.timeline:
            self.timeline[machine] = []
        
        for scheduled_task in self.timeline[machine]:
            scheduled_start = scheduled_task['start_time']
            scheduled_end = scheduled_task['end_time']
            
            if not (end_time <= scheduled_start or start_time >= scheduled_end):
                return False
        
        if task_id > 1:
            previous_task_end_time = self._find_previous_task_end_time(job_id, task_id)
            
            if previous_task_end_time > 0 and start_time < previous_task_end_time:
                return False
        
        return True
    
    def schedule_tasks(self, time_limit=None):
        self.timeline = {}
        self.best_timeline = None
        self.best_makespan = float('inf')
        
        self.nodes_visited = 0
        self.nodes_pruned = 0
        
        self.start_time = time.time()
        self.time_limit = time_limit
        self.time_expired = False
        
        print("Starting backtracking search...")
        print(f"Problem size: {self.total_tasks} tasks, {self.total_jobs} jobs, {self.machines_count} machines")
        
        self._sort_jobs()
        
        try:
            self._backtrack(0, 0)
        except KeyboardInterrupt:
            print("\n*** Search interrupted by user ***")
            self.time_expired = True
        
        if self.best_timeline is not None:
            self.timeline = self.best_timeline
            self.get_metrics()
            return True
        else:
            return False
    
    def _backtrack(self, job_index, task_index):
        self.nodes_visited += 1
        if self.nodes_visited % 10000 == 0:
            print(f"Search progress: {self.nodes_visited} nodes visited, {self.nodes_pruned} nodes pruned")
        
        if self.time_limit and (time.time() - self.start_time) > self.time_limit:
            self.time_expired = True
            return
        
        if job_index >= len(self.jobs):
            current_makespan = self._calculate_makespan()
            
            if current_makespan < self.best_makespan:
                self.best_makespan = current_makespan
                self.best_timeline = copy.deepcopy(self.timeline)
                print(f"New best solution found! Makespan: {current_makespan}")
            return
        
        current_job = self.jobs[job_index]
        
        if task_index >= len(current_job['tasks']):
            self._backtrack(job_index + 1, 0)
            return
        
        current_task_data = current_job['tasks'][task_index]
        current_task = {
            'job_id': current_job['job_id'],
            'task_id': current_task_data['task_id'],
            'execution_time': current_task_data['execution_time']
        }
        
        ordered_machines = self._sort_machines()
        
        for machine in ordered_machines:
            earliest_start = self._find_earliest_start_time(current_task, machine)
            
            estimated_end = earliest_start + current_task['execution_time']
            
            if estimated_end >= self.best_makespan:
                self.nodes_pruned += 1
                continue
            
  
            if self._checkConstraints(current_task, machine, earliest_start):
                self._assign_task(current_task, machine, earliest_start)
                
                self._backtrack(job_index, task_index + 1)
                
                if hasattr(self, 'time_expired') and self.time_expired:
                    return
                
                self._remove_task(current_task, machine)
    
        
    def get_metrics(self):
        if not self.timeline:
            return {}

        makespan = self._calculate_makespan()

        total_busy_time = 0
        total_idle_time = 0

        for machine in range(self.machines_count):
            machine_timeline = self.timeline.get(machine, [])

            sorted_tasks = sorted(machine_timeline, key=lambda t: t['start_time'])

            busy_time = sum(task['execution_time'] for task in machine_timeline)
            total_busy_time += busy_time

            total_idle_time += sorted_tasks[0]['start_time']

            for i in range(1, len(sorted_tasks)):
                total_idle_time += sorted_tasks[i]['start_time'] - sorted_tasks[i-1]['end_time']

            last_end = sorted_tasks[-1]['end_time']
            if last_end < makespan:
                total_idle_time += (makespan - last_end)

        machine_utilization = total_busy_time / (makespan * self.machines_count)

        self.total_idle_time = total_idle_time
        self.machine_utilization = machine_utilization
        self.execution_time = time.time() - self.start_time

        return {
            "makespan": str(makespan) + ' ms',
            "idle_time": str(total_idle_time) + ' ms',
            "utilization": round(machine_utilization * 100, 2),
            "execTime": str(round(self.execution_time, 2)) + " s"
        }
 
    def print_schedule(self):
        if not self.timeline:
            print("No schedule found.")
            return
        
        print("\n=== OPTIMAL SCHEDULE ===")
        total_machine_time = 0
        
        for machine in sorted(self.timeline.keys()):
            print(f"\nMachine {machine + 1}:")
            if not self.timeline[machine]:
                print("  No tasks assigned")
                continue
                
            sorted_tasks = sorted(self.timeline[machine], key=lambda t: t['start_time'])
            machine_end_time = 0
            
            for task in sorted_tasks:
                print(f"  Job {task['job_id']}, Task {task['task_id']}: "
                      f"Time {task['start_time']}-{task['end_time']} "
                      f"(Duration: {task['execution_time']})")
                machine_end_time = max(machine_end_time, task['end_time'])
            
            total_machine_time += machine_end_time
            print(f"Machine utilization: {machine_end_time} time units")


def backtracking_algorithm(problem_data, generation_callback=None):
    bt = backTracking()
    bt.machines_count = problem_data['machines_count']
    bt.total_jobs = problem_data['total_jobs']
    bt.total_tasks = problem_data['total_tasks']
    bt.jobs = problem_data['jobs']
    
    step_count = [0]  
    
    original_backtrack = bt._backtrack
    step_history = []
    
    def wrapped_backtrack(job_index, task_index):
        step_count[0] += 1
        
        if generation_callback and step_count[0] % 1000 == 0:
            current_best = bt.best_makespan if bt.best_makespan != float('inf') else 'N/A'
            generation_callback(step_count[0], {
                'nodes_visited': bt.nodes_visited,
                'best_makespan': current_best
            })
            step_history.append((step_count[0], current_best))
        
        return original_backtrack(job_index, task_index)
    
    bt._backtrack = wrapped_backtrack
    
    start_time = time.time()
    bt.schedule_tasks(time_limit= 60 * 1)  
    exec_time = time.time() - start_time
    
    converted_timeline = {}
    for machine, tasks in bt.timeline.items():
        machine += 1  
        converted_timeline[machine] = []
        for task in tasks:
            task_key = (task['job_id'], task['task_id'])
            converted_timeline[machine].append({
                task_key: (task['start_time'], task['execution_time'])
            })
    
    metrics = bt.get_metrics()
    print("timeline:", converted_timeline)
    
    return converted_timeline, metrics, step_history
