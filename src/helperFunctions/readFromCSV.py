#!/usr/bin/env python3
"""
CSV Reader Helper Function

This module provides functionality to read job schedule datasets from CSV files
and convert them into dictionary format for easy processing.
"""

import csv
import os
from typing import Dict, List, Any


def read_dataset(size: str) -> Dict[str, Any]:
    """
    Read job schedule dataset from CSV file based on size.
    
    Args:
        size (str): Dataset size - 'small', 'medium', or 'large'
    
    Returns:
        Dict[str, Any]: Dictionary containing:
            - 'machines_count': Number of machines available
            - 'tasks': List of task dictionaries with job_id, task_id, and execution_time
            - 'jobs': Dictionary of jobs organized by job_id, each containing list of tasks
            - 'total_tasks': Total number of tasks
            - 'total_jobs': Total number of jobs
    
    Raises:
        ValueError: If size is not 'small', 'medium', or 'large'
        FileNotFoundError: If the CSV file doesn't exist
    """
    # Validate input
    size = size.lower()
    valid_sizes = ['small', 'medium', 'large']
    if size not in valid_sizes:
        raise ValueError(f"Size must be one of {valid_sizes}, got '{size}'")
    
    # Map size to filename
    filename_map = {
        'small': 'small_dataset.csv',
        'medium': 'medium_dataset.csv',
        'large': 'large_dataset.csv'
    }
    
    # Construct file path relative to project root
    csv_file_path = os.path.join('../../testingDataset/datasets', filename_map[size])
    
    # Check if file exists
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"Dataset file not found: {csv_file_path}")
    
    # Read CSV data
    tasks_list = []
    machines_count = 0
    
    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Convert data types and clean up
                task = {
                    'job_id': int(row['job_id']),
                    'task_id': int(row['task_id']),
                    'execution_time': int(row['execution_time'])
                }
                tasks_list.append(task)
                
                # Get machines count
                if machines_count == 0:
                    machines_count = int(row['machines_count'])
    
    except Exception as e:
        raise RuntimeError(f"Error reading CSV file {csv_file_path}: {str(e)}")
    
    # Organize tasks by job
    jobs_dict = {}
    for task in tasks_list:
        job_id = task['job_id']
        if job_id not in jobs_dict:
            jobs_dict[job_id] = []
        jobs_dict[job_id].append(task)
    
    # Sort tasks within each job by task_id (tasks are numbered 1, 2, 3... within each job)
    for job_id in jobs_dict:
        jobs_dict[job_id].sort(key=lambda t: t['task_id'])
    
    # Create result dictionary
    result = {
        'machines_count': machines_count,
        'tasks': tasks_list,
        'jobs': jobs_dict,
        'total_tasks': len(tasks_list),
        'total_jobs': len(jobs_dict),
        'dataset_size': size,
        'source_file': filename_map[size]
    }
    
    return result