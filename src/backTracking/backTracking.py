from ast import Lambda
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
        self.tasks = data['tasks']
        self.jobs = data['jobs']
        self.total_tasks = data['total_tasks']
        self.total_jobs = data['total_jobs']
        self.timeline = {}
        self.best_timeline = None
        self.best_makespan = float('inf')
        
        # Debug counters
        self.nodes_explored = 0
        self.backtrack_count = 0
        self.constraint_checks = 0
        self.pruned_branches = 0
        self.solutions_found = 0
        self.start_time = None

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
        self.constraint_checks += 1
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
        
        # Reset debug counters
        self.nodes_explored = 0
        self.backtrack_count = 0
        self.constraint_checks = 0
        self.pruned_branches = 0
        self.solutions_found = 0
        self.start_time = time.time()
        
        print("Starting backtracking search...")
        print(f"Problem size: {self.total_tasks} tasks, {self.total_jobs} jobs, {self.machines_count} machines")
        
        # Sort tasks intelligently
        self._sort_tasks()
        print(f"Task ordering optimized: longest jobs first")
        
        # Find all possible schedules and keep the best one
        self._backtrack(0)
        
        # Print performance metrics
        elapsed_time = time.time() - self.start_time
        self._print_debug_stats(elapsed_time)
        
        # Set the best solution as current timeline
        if self.best_timeline is not None:
            self.timeline = self.best_timeline
            return True
        return False
    
    def _backtrack(self, task_index):
        """
        Recursive backtracking function to find optimal schedule.
        Explores all possible solutions to minimize makespan.
        
        Args:
            task_index: Index of current task to schedule in self.tasks
        """
        self.nodes_explored += 1
        
        # Progress reporting every 10000 nodes
        if self.nodes_explored % 10000 == 0:
            elapsed = time.time() - self.start_time
            pruning_pct = (self.pruned_branches/self.nodes_explored)*100 if self.nodes_explored > 0 else 0
            print(f"Progress: {self.nodes_explored:,} nodes explored, {self.solutions_found} solutions found, "
                  f"best makespan: {self.best_makespan}, time: {elapsed:.1f}s, "
                  f"pruning: {pruning_pct:.1f}%")
        
        # Base case: all tasks scheduled successfully
        if task_index >= len(self.tasks):
            # Calculate current makespan
            current_makespan = self._calculate_makespan()
            self.solutions_found += 1
            
            # If this is the best solution so far, save it
            if current_makespan < self.best_makespan:
                self.best_makespan = current_makespan
                self.best_timeline = copy.deepcopy(self.timeline)
                print(f"New best solution found! Makespan: {current_makespan} (Solution #{self.solutions_found})")
            return
        
        current_task = self.tasks[task_index]
        
        # Get machines ordered by current utilization (least busy first)
        ordered_machines = self._get_machines_by_utilization()
        
        # Try scheduling the current task on each machine (smart order)
        for machine in ordered_machines:
            # Find the earliest possible start time for this task on this machine
            earliest_start = self._find_earliest_start_time(current_task, machine)
            
            estimated_end = earliest_start + current_task['execution_time']
            
            # Pruning 1: If this assignment alone exceeds best makespan, skip
            if estimated_end >= self.best_makespan:
                self.pruned_branches += 1
                continue
            
            # Pruning 2: If the rest of the tasks where divided evenely and it cannot still improve best makespan then prune branch
            remaining_tasks = len(self.tasks) - task_index - 1
            if remaining_tasks > 0:
                remaining_work = sum(t['execution_time'] for t in self.tasks[task_index + 1:])
                min_additional_time = remaining_work // self.machines_count
                if estimated_end + min_additional_time >= self.best_makespan:
                    self.pruned_branches += 1
                    continue
                
            # Check if this assignment satisfies constraints
            if self._checkConstraints(current_task, machine, earliest_start):
                # Make the assignment
                self._assign_task(current_task, machine, earliest_start)
                
                # Recursively try to schedule remaining tasks
                self._backtrack(task_index + 1)
                
                # Backtrack: remove the assignment
                self._remove_task(current_task, machine)
                self.backtrack_count += 1
    
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
    
    def _sort_tasks(self):
        """
        1. Group by jobs to maintain dependencies
        2. Within jobs, keep task order (task_id)  
        3. Prioritize jobs with longer total execution time first
        """
        job_totals = {}
        for task in self.tasks:
            job_id = task['job_id']
            if job_id not in job_totals:
                job_totals[job_id] = 0
            job_totals[job_id] += task['execution_time']
        
        # Sort jobs by total execution time (longest first), then tasks by task_id within each job
        self.tasks.sort(key=lambda t: (-job_totals[t['job_id']], t['job_id'], t['task_id']))
    
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
    
    def _print_debug_stats(self, elapsed_time):
        """Print debugging statistics about the search process."""
        print(f"\n=== ALGORITHM PERFORMANCE ===")
        print(f"Total nodes explored: {self.nodes_explored:,}")
        print(f"Backtracking operations: {self.backtrack_count:,}")
        print(f"Constraint checks: {self.constraint_checks:,}")
        print(f"Pruned branches: {self.pruned_branches:,}")
        print(f"Complete solutions found: {self.solutions_found:,}")
        print(f"Search time: {elapsed_time:.2f} seconds")
        
        if self.nodes_explored > 0:
            print(f"Nodes per second: {self.nodes_explored/elapsed_time:.0f}")
            print(f"Pruning efficiency: {(self.pruned_branches/self.nodes_explored)*100:.1f}%")
        
        if self.best_makespan != float('inf'):
            print(f"Best makespan found: {self.best_makespan}")
        else:
            print("No valid solution found")
    
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
        
        # Calculate metrics
        makespan = self._calculate_makespan()
        avg_machine_utilization = total_machine_time / self.machines_count if self.machines_count > 0 else 0
        
        print(f"\n=== OPTIMIZATION METRICS ===")
        print(f"Makespan (total completion time): {makespan} time units")
        print(f"Average machine utilization: {avg_machine_utilization:.1f} time units")
        print(f"Resource efficiency: {(avg_machine_utilization/makespan*100):.1f}%" if makespan > 0 else "N/A")
