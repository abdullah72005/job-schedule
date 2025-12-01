import sys
import os
import copy
import time
import math
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from src.helperFunctions.readFromCSV import read_dataset
data = read_dataset('small')

class backTracking2:
    def __init__(self):
        self.machines_count = data['machines_count']
        self.jobs = data['jobs']
        self.total_tasks = data['total_tasks']
        self.total_jobs = data['total_jobs']
        self.timeline = {}               # machine_id -> list of scheduled tasks
        self.best_timeline = None
        self.best_makespan = float('inf')

        # Analysis counters
        self.total_idle_time = 0
        self.machine_utilization = 0
        self.execution_time = 0

        # Job-level search state
        self.job_next_task = [0] * self.total_jobs

        # Caches
        self.earliest_start_cache = {}   # (job_id, task_id, machine) -> earliest_start_time
        self.machine_order_cache = None  # cached machine ordering
        self.last_timeline_hash = None   # to detect when to update machine cache

        # Time bookkeeping & control
        self.start_time = None
        self.time_expired = False
        
        # Search statistics
        self.nodes_visited = 0
        self.nodes_pruned = 0

    # -------------------------
    # Constraint & utility code
    # -------------------------
    def _checkConstraints(self, task, machine, start_time):
        """
        Check if a task can be scheduled on a machine at a given start time.
        (unchanged logic)
        """
        job_id = task['job_id']
        task_id = task['task_id']
        execution_time = task['execution_time']
        end_time = start_time + execution_time

        # Initialize machine timeline if it doesn't exist
        if machine not in self.timeline:
            self.timeline[machine] = []

        # Check if machine is available during the time window
        # (timeline contains non-overlapping tasks)
        for scheduled_task in self.timeline[machine]:
            scheduled_start = scheduled_task['start_time']
            scheduled_end = scheduled_task['end_time']

            # Check for time overlap
            if not (end_time <= scheduled_start or start_time >= scheduled_end):
                return False

        # Check job dependency (task must start after previous task in same job)
        if task_id > 1:  # If not the first task in the job
            previous_task_end_time = self._find_previous_task_end_time(job_id, task_id - 1)
            if previous_task_end_time > 0 and start_time < previous_task_end_time:
                return False

        return True

    # -------------------------
    # Scheduling orchestration
    # -------------------------
    def schedule_tasks(self, time_limit=None):
        """
        Entry point to find optimal schedule using job-level backtracking
        with correct lower bounds for parallel machines + precedence.
        time_limit: optional seconds to stop search early (keeps best found).
        Returns True if found any feasible schedule (optimal or best-so-far).
        """
        # Reset for fresh scheduling attempt
        self.timeline = {}
        self.best_timeline = None
        self.best_makespan = float('inf')
        self.job_next_task = [0] * self.total_jobs
        self.earliest_start_cache.clear()
        self.time_expired = False
        
        # Reset search statistics
        self.nodes_visited = 0
        self.nodes_pruned = 0

        # Reset analysis counters
        self.start_time = time.time()

        print("Starting job-level Branch & Bound search...")
        print(f"Problem size: {self.total_tasks} tasks, {self.total_jobs} jobs, {self.machines_count} machines")

        # Sort jobs (heuristic) — keep tasks order inside jobs
        self._sort_jobs()
        print("Jobs sorted by total job time (longest-first heuristic).")

        # Build a strong initial upper bound via greedy list-scheduling
        greedy_makespan = self._greedy_initial_solution()
        print(f"Greedy initial makespan (upper bound): {greedy_makespan}")
        if greedy_makespan < self.best_makespan:
            self.best_makespan = greedy_makespan
            self.best_timeline = copy.deepcopy(self.timeline)

        # Start recursive job-level search (branch & bound)
        try:
            self._backtrack_job_level(time_limit)
        except KeyboardInterrupt:
            print("Interrupted by user - returning best found solution so far.")
            self.time_expired = True

        # If solution found, set timeline and compute metrics
        if self.best_timeline is not None:
            self.timeline = self.best_timeline
            metrics = self.get_metrics()
            print("Best metrics:", metrics)
            # compute final lower bound to estimate gap
            final_lb = self._compute_global_lower_bound()
            gap = None
            if final_lb > 0:
                gap = (self.best_makespan - final_lb) / final_lb
            print(f"Final lower bound: {final_lb}, optimality gap: {gap}")
            print(f"Search statistics: {self.nodes_visited} nodes visited, {self.nodes_pruned} nodes pruned")
            return True
        else:
            print("No valid schedule found.")
            print(f"Search statistics: {self.nodes_visited} nodes visited, {self.nodes_pruned} nodes pruned")
            return False

    # -------------------------
    # Job-level backtracking (B&B)
    # -------------------------
    def _backtrack_job_level(self, time_limit=None):
        """
        Backtracking that schedules exactly one task (the next task) of a job at each step.
        This is branch-and-bound: compute admissible lower bounds and prune.
        """
        # Increment node counter and print progress
        self.nodes_visited += 1
        if self.nodes_visited % 10000 == 0:
            print(f"Search progress: {self.nodes_visited} nodes visited, {self.nodes_pruned} nodes pruned")
        
        # Enforce time limit if set
        if time_limit is not None and (time.time() - self.start_time) > time_limit:
            self.time_expired = True
            return

        # Base case: all jobs finished
        if all(self.job_next_task[j] >= len(self.jobs[j]['tasks']) for j in range(self.total_jobs)):
            current_makespan = self._calculate_makespan()
            if current_makespan < self.best_makespan:
                self.best_makespan = current_makespan
                self.best_timeline = copy.deepcopy(self.timeline)
                print(f"New best solution found! Makespan: {current_makespan}")
            return

        # Compute admissible lower bound for this partial schedule
        lb = self._compute_global_lower_bound()
        # Fail-fast: if LB already >= current best, prune this subtree
        if lb >= self.best_makespan:
            self.nodes_pruned += 1
            return

        # Candidate jobs (those with remaining tasks)
        candidate_jobs = [j for j in range(self.total_jobs) if self.job_next_task[j] < len(self.jobs[j]['tasks'])]

        # Heuristic ordering: prefer jobs with small (ready_time + remaining_time)
        candidate_jobs.sort(key=self._job_priority_key)

        # Try each candidate job: schedule its next task
        for job in candidate_jobs:
            # Respect time limit at top of loop as well
            if time_limit is not None and (time.time() - self.start_time) > time_limit:
                self.time_expired = True
                return

            task_idx = self.job_next_task[job]
            task_data = self.jobs[job]['tasks'][task_idx]
            current_task = {
                'job_id': self.jobs[job]['job_id'],
                'task_id': task_data['task_id'],
                'execution_time': task_data['execution_time']
            }

            # Machines ordered by earliest finish time (better fit)
            ordered_machines = self._get_machines_by_earliest_finish()

            for machine in ordered_machines:
                cache_key = (current_task['job_id'], current_task['task_id'], machine)
                if cache_key in self.earliest_start_cache:
                    earliest_start = self.earliest_start_cache[cache_key]
                else:
                    earliest_start = self._find_earliest_start_time(current_task, machine)
                    self.earliest_start_cache[cache_key] = earliest_start

                # Fail-fast: if earliest start already >= best_makespan, skip
                # if earliest_start >= self.best_makespan:
                #     continue

                # estimated_end = earliest_start + current_task['execution_time']
                # Quick prune: if estimated_end alone >= best known makespan
                # if estimated_end >= self.best_makespan:
                #     continue

                # Dominance check (lightweight): prefer not to place tasks that create obviously worse order
                # if not self._dominance_quick_check(machine, current_task, earliest_start):
                #     continue

                # Final constraint check and assign
                if self._checkConstraints(current_task, machine, earliest_start):
                    # commit assignment
                    self._assign_task(current_task, machine, earliest_start)
                    self.job_next_task[job] += 1

                    # timeline changed => earliest start cache invalidated
                    self.earliest_start_cache.clear()

                    # Recurse
                    self._backtrack_job_level(time_limit)

                    # Backtrack
                    self.job_next_task[job] -= 1
                    self._remove_task(current_task, machine)
                    self.earliest_start_cache.clear()

                    # If time expired during deeper search, bubble up immediately
                    if self.time_expired:
                        return

    # -------------------------
    # Lower bounds & heuristics
    # -------------------------
    def _compute_global_lower_bound(self):
        """
        Admissible lower bound for P_m | prec | Cmax (parallel machines, precedence constraints).
        Combines:
          - current_makespan (makespan_so_far)
          - total_remaining_work / m
          - longest remaining job completion (ready_time + remaining_job_time)
          - max machine ready time (no machine can finish earlier than its current busy time)
        Returns numeric LB.
        """
        # current makespan from scheduled tasks
        makespan_so_far = self._calculate_makespan()

        # Remaining total work and remaining per-job
        remaining_total = 0
        remaining_by_job = [0] * self.total_jobs
        for j in range(self.total_jobs):
            next_idx = self.job_next_task[j]
            rem = sum(t['execution_time'] for t in self.jobs[j]['tasks'][next_idx:])
            remaining_total += rem
            remaining_by_job[j] = rem

        # LB2: total remaining work spread across machines
        lb_total = math.ceil(remaining_total / self.machines_count) if self.machines_count > 0 else 0

        # LB3: longest remaining job (critical-path-like, but jobs are chains)
        job_ready_times = []
        for j in range(self.total_jobs):
            if self.job_next_task[j] == 0:
                ready = 0
            else:
                prev_task_id = self.jobs[j]['tasks'][self.job_next_task[j] - 1]['task_id']
                ready = self._find_previous_task_end_time(self.jobs[j]['job_id'], prev_task_id)
            job_ready_times.append(ready)
        lb_job = max((job_ready_times[j] + remaining_by_job[j]) for j in range(self.total_jobs)) if self.total_jobs > 0 else 0

        # LB4: max machine ready time (no machine can complete earlier than its current busy time)
        lb_machine_ready = 0
        for m in range(self.machines_count):
            if m in self.timeline and self.timeline[m]:
                machine_ready = max(t['end_time'] for t in self.timeline[m])
            else:
                machine_ready = 0
            # Since tasks can be processed on any machine, we cannot assign specific remaining work to machines.
            # But no machine can finish earlier than its current ready time, so that's a valid lower bound component.
            lb_machine_ready = max(lb_machine_ready, machine_ready)

        # Combine all lower bounds
        lb = max(makespan_so_far, lb_total, lb_job, lb_machine_ready)
        return lb

    def _job_priority_key(self, job):
        """
        Heuristic used to order candidate jobs when branching:
        prioritize jobs with (ready_time + remaining_job_time) small first.
        """
        next_idx = self.job_next_task[job]
        remaining_job_time = sum(t['execution_time'] for t in self.jobs[job]['tasks'][next_idx:])
        if next_idx == 0:
            ready = 0
        else:
            prev_task_id = self.jobs[job]['tasks'][next_idx - 1]['task_id']
            ready = self._find_previous_task_end_time(self.jobs[job]['job_id'], prev_task_id)
        return ready + remaining_job_time

    # -------------------------
    # Simple dominance heuristic
    # -------------------------
    # def _dominance_quick_check(self, machine, task, start_time):
    #     """
    #     Lightweight dominance check to prune obviously bad local orders.
    #     It's conservative (only prunes when clearly dominated).
    #     """
    #     # If machine empty -> nothing to dominate
    #     if machine not in self.timeline or not self.timeline[machine]:
    #         return True

    #     # If placing current task before already scheduled tasks that finish earlier
    #     # but the current task has a **longer** remaining job chain than that earlier task,
    #     # then placing it earlier may be dominated. This is conservative and cheap.
    #     cur_job_index = self._find_job_index_by_job_id(task['job_id'])
    #     cur_task_idx = self.job_next_task[cur_job_index]
    #     cur_remaining = sum(t['execution_time'] for t in self.jobs[cur_job_index]['tasks'][cur_task_idx:])

    #     # check tasks that end before start_time on this machine
    #     for scheduled in self.timeline[machine]:
    #         if scheduled['end_time'] <= start_time:
    #             other_job_index = scheduled['job_id'] - 1
    #             other_task_idx = scheduled['task_id'] - 1  # scheduled task id is 1-based
    #             # remaining for other job after this scheduled task:
    #             other_remaining = 0
    #             if other_job_index is not None:
    #                 next_idx = self.job_next_task[other_job_index]
    #                 # If other task is already scheduled, its next index may have advanced; approximate remaining:
    #                 other_remaining = sum(t['execution_time'] for t in self.jobs[other_job_index]['tasks'][next_idx:])
    #             # If our task has much larger remaining and would be placed before smaller remaining, skip
    #             if cur_remaining > other_remaining + 0:  # tweak threshold if needed
    #                 return False
    #     return True

    # -------------------------
    # Assign / remove / find helpers
    # -------------------------
    def _assign_task(self, task, machine, start_time):
        """Add task to machine's timeline (commit)."""
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
            # remove the matching task (job_id and task_id) - remove the most recent matching
            for i in range(len(self.timeline[machine]) - 1, -1, -1):
                t = self.timeline[machine][i]
                if t['job_id'] == task['job_id'] and t['task_id'] == task['task_id']:
                    del self.timeline[machine][i]
                    break

            # If machine becomes empty, optional: remove key to keep timelines compact
            if not self.timeline[machine]:
                del self.timeline[machine]

    def _find_previous_task_end_time(self, job_id, task_id):
        """
        Find the end time of a task (job_id, task_id) if scheduled.
        Returns 0 if not found (i.e., previous not scheduled yet).
        """
        previous_task_end_time = 0
        for machine_timeline in self.timeline.values():
            for scheduled_task in machine_timeline:
                if (scheduled_task['job_id'] == job_id and
                    scheduled_task['task_id'] == task_id):
                    previous_task_end_time = max(previous_task_end_time, scheduled_task['end_time'])
        return previous_task_end_time

    def _sort_jobs(self):
        """
        Sort jobs by total execution time (longest first) to improve scheduling efficiency.
        Keep tasks within jobs in original order.
        """
        def job_total_time(job):
            return sum(task['execution_time'] for task in job['tasks'])

        # Sort jobs by total execution time (longest first)
        self.jobs.sort(key=lambda job: -job_total_time(job))

    def _get_machines_by_utilization(self):
        """
        Get machines ordered by current utilization (least busy first).
        """
        machine_loads = []
        for machine in range(self.machines_count):
            current_load = sum(t['execution_time'] for t in self.timeline.get(machine, []))
            machine_loads.append((current_load, machine))

        return [machine for load, machine in sorted(machine_loads)]

    def _get_machines_by_earliest_finish(self):
        """
        Machines ordered by earliest finish time (the earliest time the machine would be free).
        Uses caching to avoid repeated computation.
        """
        # Simple hash of timeline to detect changes
        current_hash = len([task for machine_tasks in self.timeline.values() for task in machine_tasks])
        
        if self.machine_order_cache is None or self.last_timeline_hash != current_hash:
            machine_finish = []
            for machine in range(self.machines_count):
                if machine in self.timeline and self.timeline[machine]:
                    finish = max(t['end_time'] for t in self.timeline[machine])
                else:
                    finish = 0
                machine_finish.append((finish, machine))
            
            self.machine_order_cache = [m for finish, m in sorted(machine_finish)]
            self.last_timeline_hash = current_hash
        
        return self.machine_order_cache

    def _find_earliest_start_time(self, task, machine):
        """
        Find the earliest possible start time for a task on a machine.
        Considers both machine availability and job dependencies.
        """
        job_id = task['job_id']
        task_id = task['task_id']

        # Start with time 0
        earliest_start = 0

        # Job dependency: must start after previous task in same job
        if task_id > 1:
            previous_task_end_time = self._find_previous_task_end_time(job_id, task_id - 1)
            earliest_start = max(earliest_start, previous_task_end_time)

        # Machine availability
        if machine in self.timeline:
            machine_tasks = sorted(self.timeline[machine], key=lambda t: t['start_time'])
            for scheduled_task in machine_tasks:
                # Try to fit before this scheduled task
                if earliest_start + task['execution_time'] <= scheduled_task['start_time']:
                    return earliest_start
                earliest_start = max(earliest_start, scheduled_task['end_time'])

        return earliest_start

    def _calculate_makespan(self):
        """Calculate current makespan (maximum end time across all machines)."""
        makespan = 0
        for machine_timeline in self.timeline.values():
            for task in machine_timeline:
                makespan = max(makespan, task['end_time'])
        return makespan

    # -------------------------
    # Greedy initial solution (list scheduling) for a strong upper bound
    # -------------------------
    def _greedy_initial_solution(self):
        """
        Construct a feasible schedule quickly using list-scheduling:
        repeatedly schedule earliest-ready tasks on the machine that allows the earliest finish.
        This gives a valid initial upper bound (self.best_makespan) and self.best_timeline.
        """
        # local schedule state
        sim_timeline = {}  # machine -> list of scheduled tasks
        job_next = [0] * self.total_jobs
        finished_tasks = 0

        # Helper to find earliest start on sim_timeline
        def sim_earliest_start(job_id, task_id, duration, sim_timeline):
            earliest = 0
            # job dependency
            if task_id > 1:
                # search sim_timeline for previous task end
                prev_end = 0
                for m_tasks in sim_timeline.values():
                    for t in m_tasks:
                        if t['job_id'] == job_id and t['task_id'] == task_id - 1:
                            prev_end = max(prev_end, t['end_time'])
                earliest = max(earliest, prev_end)
            # machine availability not considered here; we compute per machine below
            return earliest

        # Repeat until all tasks scheduled
        while finished_tasks < self.total_tasks:
            # collect ready tasks (jobs whose next task is ready)
            ready_tasks = []
            for j in range(self.total_jobs):
                idx = job_next[j]
                if idx < len(self.jobs[j]['tasks']):
                    # check if previous task is scheduled in sim (if idx>0)
                    if idx == 0:
                        ready = True
                    else:
                        prev_id = self.jobs[j]['tasks'][idx - 1]['task_id']
                        prev_scheduled = False
                        for m in sim_timeline.values():
                            for t in m:
                                if t['job_id'] == self.jobs[j]['job_id'] and t['task_id'] == prev_id:
                                    prev_scheduled = True
                                    break
                            if prev_scheduled:
                                break
                        ready = prev_scheduled
                    if ready:
                        tdata = self.jobs[j]['tasks'][idx]
                        ready_tasks.append((j, tdata))

            if not ready_tasks:
                # no ready tasks found (shouldn't happen) -> break to avoid infinite loop
                break

            # For each ready task, find the best machine and earliest finish
            best_choice = None
            best_finish = float('inf')
            best_start = None
            best_machine = None
            for (j, tdata) in ready_tasks:
                duration = tdata['execution_time']
                job_id = self.jobs[j]['job_id']
                task_id = tdata['task_id']
                base_ready = sim_earliest_start(job_id, task_id, duration, sim_timeline)
                # try all machines
                for m in range(self.machines_count):
                    # compute machine earliest available
                    if m in sim_timeline and sim_timeline[m]:
                        machine_ready = max(t['end_time'] for t in sim_timeline[m])
                    else:
                        machine_ready = 0
                    start = max(base_ready, machine_ready)
                    finish = start + duration
                    if finish < best_finish:
                        best_finish = finish
                        best_choice = (j, tdata)
                        best_start = start
                        best_machine = m

            # commit best_choice
            j, tdata = best_choice
            if best_machine not in sim_timeline:
                sim_timeline[best_machine] = []
            sim_timeline[best_machine].append({
                'job_id': self.jobs[j]['job_id'],
                'task_id': tdata['task_id'],
                'execution_time': tdata['execution_time'],
                'start_time': best_start,
                'end_time': best_finish,
                'machine': best_machine
            })
            job_next[j] += 1
            finished_tasks += 1

        # compute makespan
        makespan = 0
        for m_tasks in sim_timeline.values():
            for t in m_tasks:
                makespan = max(makespan, t['end_time'])

        # store greedy as current best_timeline (but do not overwrite main timeline used by search)
        self.best_timeline = copy.deepcopy(sim_timeline)
        # Also set timeline to best_timeline briefly so get_metrics uses it if needed later
        # But we do not want search to start from this timeline; search starts from empty timeline.
        return makespan

    # -------------------------
    # Metrics & printing
    # -------------------------
    def get_metrics(self):
        """Calculate makespan, total idle time, machine utilization and execution time."""
        if self.best_timeline is None and not self.timeline:
            return {}

        # Use current timeline (which is either best_timeline or current timeline)
        timeline_to_use = self.timeline if self.timeline else self.best_timeline
        makespan = 0
        for m_tasks in timeline_to_use.values():
            for t in m_tasks:
                makespan = max(makespan, t['end_time'])

        total_machine_utilization = 0
        total_idle_time = 0

        for machine in range(self.machines_count):
            machine_timeline = timeline_to_use.get(machine, [])
            if machine_timeline:
                # Sort tasks by start time
                sorted_tasks = sorted(machine_timeline, key=lambda t: t['start_time'])

                machine_end_time = max(task['end_time'] for task in machine_timeline)
                machine_utilization = (machine_end_time / makespan) if makespan > 0 else 0
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
                if makespan > machine_end_time:
                    total_idle_time += (makespan - machine_end_time)
            else:
                # machine has no tasks, idle for whole makespan
                total_idle_time += makespan

        self.machine_utilization = (total_machine_utilization / self.machines_count) if self.machines_count > 0 else 0
        self.total_idle_time = total_idle_time
        self.execution_time = time.time() - self.start_time if self.start_time else 0

        return {
            'makespan': makespan,
            'total_idle_time': total_idle_time,
            'machine_utilization': self.machine_utilization,
            'execution_time': self.execution_time
        }

    def print_schedule(self):
        """Print the current schedule in a readable format."""
        if not self.timeline:
            if self.best_timeline:
                timeline_to_print = self.best_timeline
            else:
                print("No schedule found.")
                return
        else:
            timeline_to_print = self.timeline

        print("\n=== SCHEDULE ===")
        for machine in sorted(range(self.machines_count)):
            print(f"\nMachine {machine}:")
            machine_timeline = timeline_to_print.get(machine, [])
            if not machine_timeline:
                print("  No tasks assigned")
                continue

            # Sort tasks by start time for readability
            sorted_tasks = sorted(machine_timeline, key=lambda t: t['start_time'])
            machine_end_time = 0

            for task in sorted_tasks:
                print(f"  Job {task['job_id']}, Task {task['task_id']}: "
                      f"Time {task['start_time']}-{task['end_time']} "
                      f"(Duration: {task['execution_time']})")
                machine_end_time = max(machine_end_time, task['end_time'])

            print(f"  Machine total busy time: {machine_end_time} time units")