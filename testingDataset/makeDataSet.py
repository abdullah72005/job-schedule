#!/usr/bin/env python3
"""
Job Schedule Dataset Generator

Generates 3 CSV files with different sizes:
- small_dataset.csv: Small dataset for quick testing
- medium_dataset.csv: Medium dataset for moderate testing
- large_dataset.csv: Large dataset for performance testing

Each dataset contains:
- Number of machines
- Jobs with execution times and optional dependencies (uncommon)
"""

import csv
import random
import os
from typing import List, Dict, Tuple


class JobScheduleDatasetGenerator:
    def __init__(self):
        # Dataset configurations with ranges
        self.datasets = {
            'small': {
                'machines_range': (2, 5),   # 2-5 machines
                'jobs_range': (3, 5),       # 3-8 jobs
                'tasks_per_job_range': (2, 5),  # 2-5 tasks per job
                'filename': 'small_dataset.csv'
            },
            'medium': {
                'machines_range': (5, 12),  # 5-12 machines
                'jobs_range': (8, 20),      # 8-20 jobs  
                'tasks_per_job_range': (2, 8),  # 3-8 tasks per job
                'filename': 'medium_dataset.csv'
            },
            'large': {
                'machines_range': (10, 20), # 10-20 machines
                'jobs_range': (20, 50),     # 20-50 jobs
                'tasks_per_job_range': (2, 10), # 4-10 tasks per job
                'filename': 'large_dataset.csv'
            }
        }
        
        # Time range for task execution (in minutes)
        self.min_execution_time = 5
        self.max_execution_time = 60
        
        # Ensure output directory exists
        self.output_dir = r'D:\code\python\mlAiDs\Aiproject\testingDataset\datasets'
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_task_execution_time(self) -> int:
        """Generate a random execution time for a task."""
        return random.randint(self.min_execution_time, self.max_execution_time)
    

    
    def generate_dataset(self, size: str) -> List[Dict]:
        """Generate a dataset with jobs containing sequential tasks."""
        config = self.datasets[size]
        tasks = []  # All tasks (flattened from all jobs)
        
        # Generate random counts within specified ranges
        machines_count = random.randint(*config['machines_range'])
        jobs_count = random.randint(*config['jobs_range'])
        
        for job_id in range(1, jobs_count + 1):
            # Generate number of tasks for this job
            tasks_in_job = random.randint(*config['tasks_per_job_range'])
            
            # Generate tasks for this job (task_id starts from 1 for each job)
            for task_id in range(1, tasks_in_job + 1):
                task_execution_time = self.generate_task_execution_time()
                
                task = {
                    'job_id': job_id,
                    'task_id': task_id,
                    'execution_time': task_execution_time,
                    'machines_count': machines_count
                }
                
                tasks.append(task)
        
        return tasks
    
    def write_csv(self, tasks: List[Dict], filename: str):
        """Write tasks data to CSV file."""
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['job_id', 'task_id', 'execution_time', 'machines_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write task data
            for task in tasks:
                # Create simplified task row
                task_row = {
                    'job_id': task['job_id'],
                    'task_id': task['task_id'],
                    'execution_time': task['execution_time'],
                    'machines_count': task['machines_count']
                }
                writer.writerow(task_row)
        
    def generate_all_datasets(self):
        """Generate all three datasets (small, medium, large)."""
        for size in ['small', 'medium', 'large']:
            tasks = self.generate_dataset(size)
            self.write_csv(tasks, self.datasets[size]['filename'])
        
        # Generate a summary file
        self.generate_summary()
        
        print("Dataset generation completed successfully!")
    
    def generate_summary(self):
        """Generate a summary of all datasets."""
        summary_path = os.path.join(self.output_dir, 'dataset_summary.txt')
        
        with open(summary_path, 'w') as f:
            f.write("Job Schedule Datasets Summary (Jobs with Sequential Tasks)\n")
            f.write("=" * 60 + "\n\n")
            
            for size, config in self.datasets.items():
                f.write(f"{size.upper()} Dataset ({config['filename']}):\n")
                f.write(f"- Machines: {config['machines_range'][0]}-{config['machines_range'][1]} (random)\n")
                f.write(f"- Jobs: {config['jobs_range'][0]}-{config['jobs_range'][1]} (random)\n")
                f.write(f"- Tasks per job: {config['tasks_per_job_range'][0]}-{config['tasks_per_job_range'][1]} (random)\n")
                f.write(f"- Task execution time range: {self.min_execution_time}-{self.max_execution_time} minutes\n\n")
            
            f.write("CSV Format:\n")
            f.write("- job_id: Identifier of the job this task belongs to\n")
            f.write("- task_id: Unique identifier for each task\n")
            f.write("- execution_time: Time required to complete the task (minutes)\n")
            f.write("- machines_count: Total number of machines available\n\n")
            f.write("Task Dependencies:\n")
            f.write("- Tasks within a job are sequentially dependent (implied by task_id ordering)\n")
            f.write("- First task of each job has no dependencies (independent)\n")
            f.write("- Jobs are independent of each other\n")
        

def main():
    """Main function to generate all datasets."""
    generator = JobScheduleDatasetGenerator()
    generator.generate_all_datasets()


if __name__ == "__main__":
    main()