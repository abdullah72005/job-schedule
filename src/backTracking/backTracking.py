import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from src.helperFunctions.readFromCSV import read_dataset
data = read_dataset('small')
print(data['jobs'])

class backTracking:
    def __init__(self):
        self.machines_count = data['machines_count']
        self.tasks = data['tasks']
        self.jobs = data['jobs']
        self.total_tasks = data['total_tasks']
        self.total_jobs = data['total_jobs']
        self.timeline = {}

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
        
        # Constraint 1: Check if machine is available during the time window
        for scheduled_task in self.timeline[machine]:
            scheduled_start = scheduled_task['start_time']
            scheduled_end = scheduled_task['end_time']
            
            # Check for time overlap
            if not (end_time <= scheduled_start or start_time >= scheduled_end):
                return False
        
        # Constraint 2: Check job dependency (task must start after previous task in same job)
        if task_id > 1:  # If not the first task in the job
            previous_task_found = False
            previous_task_end_time = 0
            
            # Find the previous task in the same job across all machines
            for machine_timeline in self.timeline.values():
                for scheduled_task in machine_timeline:
                    if (scheduled_task['job_id'] == job_id and 
                        scheduled_task['task_id'] == task_id - 1):
                        previous_task_found = True
                        previous_task_end_time = scheduled_task['end_time']
                        break
            
            # If previous task exists and current task starts before it ends
            if previous_task_found and start_time < previous_task_end_time:
                return False
        
        return True
    
    def schedule_tasks(self):
        # Implement backtracking scheduling logic 
        
        pass