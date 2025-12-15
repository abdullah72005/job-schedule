#!/usr/bin/env python3

import csv
import random
import os
from typing import List, Dict, Tuple


class JobScheduleDatasetGenerator:
    def __init__(self):
        self.datasets = {
            'small': {
                'machines_range': (2, 5),   
                'jobs_range': (3, 5),      
                'tasks_per_job_range': (2, 5),  
                'filename': 'small_dataset.csv'
            },
            'medium': {
                'machines_range': (5, 12),  
                'jobs_range': (8, 20),       
                'tasks_per_job_range': (2, 8),  
                'filename': 'medium_dataset.csv'
            },
            'large': {
                'machines_range': (10, 20), 
                'jobs_range': (20, 50),    
                'tasks_per_job_range': (2, 10), 
                'filename': 'large_dataset.csv'
            }
        }
        
        self.min_execution_time = 5
        self.max_execution_time = 60
        
        self.output_dir = r'D:\code\python\mlAiDs\Aiproject\testingDataset\datasets'
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_task_execution_time(self) -> int:
        return random.randint(self.min_execution_time, self.max_execution_time)
    

    
    def generate_dataset(self, size: str) -> List[Dict]:
        config = self.datasets[size]
        tasks = [] 
        
        machines_count = random.randint(*config['machines_range'])
        jobs_count = random.randint(*config['jobs_range'])
        
        for job_id in range(1, jobs_count + 1):
            tasks_in_job = random.randint(*config['tasks_per_job_range'])
            
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
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['job_id', 'task_id', 'execution_time', 'machines_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            for task in tasks:
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
        
        self.generate_summary()
        
        print("Dataset generation completed successfully!")
    
    def generate_summary(self):
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