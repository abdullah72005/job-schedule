import sys
import os
import copy
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from src.helperFunctions.readFromCSV import read_dataset
data = read_dataset('small')
print(data)

class backTracking:
    def __init__(self):
        self.machines_count = data['machines_count']
        self.jobs = data['jobs']
        self.total_tasks = data['total_tasks']
        self.total_jobs = data['total_jobs']
        self.timeline = {}
        self.best_timeline = None
        self.best_makespan = float('inf')

        # Analysis counters
        self.total_idle_time = 0
        self.machine_utilization = 0
        self.execution_time = 0
        

    def _checkConstraints(self, task, machine, start_time):
        """
        Check if a task can be scheduled on a machine at a given start time.
        
        Args:
            task: Task dictionary with job_id, task_id, execution_time
            machine: Machine ID (0-based index)
            start_time: Proposed start time for the task
            
        Returns:
            bool: True if constraints are satisfied, False otherwise
        """
        job_id = task['job_id']
        task_id = task['task_id']
        execution_time = task['execution_time']
        end_time = start_time + execution_time
        
        # Initialize machine timeline if it doesn't exist
        if machine not in self.timeline:
            self.timeline[machine] = []
        
        # Check if machine is available during the time window
        for scheduled_task in self.timeline[machine]:
            scheduled_start = scheduled_task['start_time']
            scheduled_end = scheduled_task['end_time']
            
            # Check for time overlap
            if not (end_time <= scheduled_start or start_time >= scheduled_end):
                return False
        
        # Check job dependency (task must start after previous task in same job)
        if task_id > 1:  # If not the first task in the job
            previous_task_end_time = self._find_previous_task_end_time(job_id, task_id)
            
            # If previous task exists and current task starts before it ends
            if previous_task_end_time > 0 and start_time < previous_task_end_time:
                return False
        
        return True
    
    def schedule_tasks(self):
        """
        Find the optimal schedule that minimizes makespan.
        
        Returns:
            bool: True if a valid schedule is found, False otherwise
        """
        # Reset for fresh scheduling attempt
        self.timeline = {}
        self.best_timeline = None
        self.best_makespan = float('inf')
        
        # Reset analysis counters
        self.start_time = time.time()
        
        print("Starting backtracking search...")
        print(f"Problem size: {self.total_tasks} tasks, {self.total_jobs} jobs, {self.machines_count} machines")
        
        # Sort jobs intelligently
        self._sort_jobs()
        print(f"Job ordering optimized: longest jobs first")
        
        # Find all possible schedules and keep the best one
        self._backtrack_jobs(0, 0)
        
        # Set the best solution as current timeline and calculate analysis metrics
        if self.best_timeline is not None:
            self.timeline = self.best_timeline
            self.get_metrics()
            return True
        return False
    
    def _backtrack_jobs(self, job_index, task_index):
        """
        Recursive backtracking function to find optimal schedule.
        Explores all possible solutions to minimize makespan using job structure.
        
        Args:
            job_index: Index of current job in self.jobs
            task_index: Index of current task within the current job
        """
        # Base case: all jobs and tasks scheduled successfully
        if job_index >= len(self.jobs):
            # Calculate current makespan
            current_makespan = self._calculate_makespan()
            
            # If this is the best solution so far, save it
            if current_makespan < self.best_makespan:
                self.best_makespan = current_makespan
                self.best_timeline = copy.deepcopy(self.timeline)
                print(f"New best solution found! Makespan: {current_makespan}")
            return
        
        current_job = self.jobs[job_index]
        
        # Check if we've finished all tasks in current job
        if task_index >= len(current_job['tasks']):
            # Move to next job
            self._backtrack_jobs(job_index + 1, 0)
            return
        
        # Get current task from current job
        current_task_data = current_job['tasks'][task_index]
        current_task = {
            'job_id': current_job['job_id'],
            'task_id': current_task_data['task_id'],
            'execution_time': current_task_data['execution_time']
        }
        
        # Get machines ordered by current utilization (least busy first)
        ordered_machines = self._get_machines_by_utilization()
        
        # Try scheduling the current task on each machine (smart order)
        for machine in ordered_machines:
            # Find the earliest possible start time for this task on this machine
            earliest_start = self._find_earliest_start_time(current_task, machine)
            
            estimated_end = earliest_start + current_task['execution_time']
            
            # Pruning 1: If this assignment alone exceeds best makespan, skip
            if estimated_end >= self.best_makespan:
                continue
            
            # Pruning 2: If the rest of the tasks where divided evenely and it cannot still improve best makespan then prune branch
            # remaining_tasks = len(self.tasks) - task_index - 1
            # if remaining_tasks > 0:
            #     remaining_work = sum(t['execution_time'] for t in self.tasks[task_index + 1:])
            #     min_additional_time = remaining_work // self.machines_count
            #     if estimated_end + min_additional_time >= self.best_makespan:
            #         continue
                
            # Check if this assignment satisfies constraints
            if self._checkConstraints(current_task, machine, earliest_start):
                # Make the assignment
                self._assign_task(current_task, machine, earliest_start)
                
                # Recursively try to schedule next task
                self._backtrack_jobs(job_index, task_index + 1)
                
                # Backtrack: remove the assignment
                self._remove_task(current_task, machine)
    
    def _assign_task(self, task, machine, start_time):
        """Add task to machine's timeline."""
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
        """Remove task from machine's timeline (for backtracking)."""
        if machine in self.timeline:
            self.timeline[machine] = [
                t for t in self.timeline[machine] 
                if not (t['job_id'] == task['job_id'] and t['task_id'] == task['task_id'])
            ]
    
    def _find_previous_task_end_time(self, job_id, task_id):
        """
        Find the end time of the previous task in the same job.
        
        Args:
            job_id: Job ID to search for
            task_id: Current task ID (will search for task_id - 1)
            
        Returns:
            int: End time of previous task, or 0 if not found
        """
        previous_task_end_time = 0
        
        # Find when the previous task in the same job finishes
        for machine_timeline in self.timeline.values():
            for scheduled_task in machine_timeline:
                if (scheduled_task['job_id'] == job_id and 
                    scheduled_task['task_id'] == task_id - 1):
                    previous_task_end_time = scheduled_task['end_time']
                    break
        
        return previous_task_end_time
    
    def _sort_jobs(self):
        """
        Sort jobs by total execution time (longest first) to improve scheduling efficiency.
        Tasks within jobs maintain their original order to preserve dependencies.
        """
        def job_total_time(job):
            return sum(task['execution_time'] for task in job['tasks'])
        
        # Sort jobs by total execution time (longest first)
        self.jobs.sort(key=lambda job: -job_total_time(job))
    
    def _get_machines_by_utilization(self):
        """
        Get machines ordered by current utilization (least busy first).
        
        Returns:
            list: Machine IDs sorted by current load (ascending)
        """
        machine_loads = []
        for machine in range(self.machines_count):
            current_load = sum(t['execution_time'] for t in self.timeline.get(machine, []))
            machine_loads.append((current_load, machine))
        
        # Sort by current load and return machine IDs
        return [machine for load, machine in sorted(machine_loads)]

    def _find_earliest_start_time(self, task, machine):
        """
        Find the earliest possible start time for a task on a machine.
        Considers both machine availability and job dependencies.
        
        Args:
            task: Task dictionary
            machine: Machine ID
            
        Returns:
            int: Earliest valid start time
        """
        job_id = task['job_id']
        task_id = task['task_id']
        
        # Start with time 0
        earliest_start = 0
        
        # Check job dependency: must start after previous task in same job
        if task_id > 1:
            previous_task_end_time = self._find_previous_task_end_time(job_id, task_id)
            earliest_start = max(earliest_start, previous_task_end_time)
        
        # Check machine availability
        if machine in self.timeline:
            machine_tasks = sorted(self.timeline[machine], key=lambda t: t['start_time'])
            
            # Try to fit the task in the earliest available slot
            for i, scheduled_task in enumerate(machine_tasks):
                # Try to fit before this scheduled task
                if earliest_start + task['execution_time'] <= scheduled_task['start_time']:
                    return earliest_start
                
                # Update earliest start to after this task
                earliest_start = max(earliest_start, scheduled_task['end_time'])
        
        return earliest_start
    
    def _calculate_makespan(self):
        """Calculate current makespan (maximum end time across all machines)."""
        makespan = 0
        for machine_timeline in self.timeline.values():
            for task in machine_timeline:
                makespan = max(makespan, task['end_time'])
        return makespan
    
    def get_metrics(self):
        """Calculate the three analysis metrics from the current schedule."""
        if not self.timeline:
            return {}
        
        # Calculate actual makespan from current timeline (max of all end times)
        makespan = self._calculate_makespan()
        
        total_machine_utilization = 0
        total_idle_time = 0
        
        for machine_timeline in self.timeline.values():
            if machine_timeline:
                # Sort tasks by start time
                sorted_tasks = sorted(machine_timeline, key=lambda t: t['start_time'])
                
                # Calculate machine utilization (how long this machine was working)
                machine_end_time = max(task['end_time'] for task in machine_timeline)
                machine_utilization = machine_end_time / makespan
                total_machine_utilization += machine_utilization
                
                # Add gap before first task
                first_start = sorted_tasks[0]['start_time']
                total_idle_time += first_start
                
                # Add gaps between tasks
                for i in range(1, len(sorted_tasks)):
                    prev_end = sorted_tasks[i-1]['end_time']
                    current_start = sorted_tasks[i]['start_time']
                    if current_start > prev_end:
                        total_idle_time += (current_start - prev_end)
                
                # Add waiting time after machine finishes until makespan
                machine_end_time = max(task['end_time'] for task in machine_timeline)
                if makespan > machine_end_time:
                    total_idle_time += (makespan - machine_end_time)
        
        # Average machine utilization across all machines
        self.machine_utilization = (total_machine_utilization / self.machines_count)
        self.total_idle_time = total_idle_time
        
        # Calculate execution time (actual algorithm runtime)
        self.execution_time = time.time() - self.start_time
        
        return {
            'makespan': makespan,
            'total_idle_time': self.total_idle_time,
            'machine_utilization': self.machine_utilization,
            'execution_time': self.execution_time
        }
    
    def print_schedule(self):
        """Print the current schedule in a readable format."""
        if not self.timeline:
            print("No schedule found.")
            return
        
        print("\n=== OPTIMAL SCHEDULE ===")
        total_machine_time = 0
        
        for machine in sorted(self.timeline.keys()):
            print(f"\nMachine {machine}:")
            if not self.timeline[machine]:
                print("  No tasks assigned")
                continue
                
            # Sort tasks by start time for readability
            sorted_tasks = sorted(self.timeline[machine], key=lambda t: t['start_time'])
            machine_end_time = 0
            
            for task in sorted_tasks:
                print(f"  Job {task['job_id']}, Task {task['task_id']}: "
                      f"Time {task['start_time']}-{task['end_time']} "
                      f"(Duration: {task['execution_time']})")
                machine_end_time = max(machine_end_time, task['end_time'])
            
            total_machine_time += machine_end_time
            print(f"  Machine utilization: {machine_end_time} time units")