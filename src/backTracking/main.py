from backTracking import backTracking
from backTracking2 import backTracking2

def main():
    # Create scheduler instance
    scheduler = backTracking()
    
    print("Starting backtracking job scheduling...")
    print(f"Dataset: {scheduler.total_jobs} jobs, {scheduler.total_tasks} tasks, {scheduler.machines_count} machines\n")
    
    # Attempt to find a valid schedule
    if scheduler.schedule_tasks():
        scheduler.print_schedule()
    else:
        print("something went wrong")
    
    print("\nAnalysis Metrics:")
    metrics = scheduler.get_metrics()
    print(f" - Makespan: {metrics['makespan']}")
    print(f" - Total Idle Time: {metrics['total_idle_time']}")
    print(f" - Machine Utilization: {metrics['machine_utilization']*100:.2f}%")
    print(f" - Execution Time: {metrics['execution_time']:.4f} seconds")

if __name__ == "__main__":
    main()
