from backTracking import backTracking

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

if __name__ == "__main__":
    main()
