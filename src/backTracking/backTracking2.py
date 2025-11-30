import sys
import os
import copy
import time
import heapq
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from src.helperFunctions.readFromCSV import read_dataset
data = read_dataset('small')

class backTracking2:
    def __init__(self):
        # Problem data (from your read_dataset)
        self.machines_count = data['machines_count']
        self.jobs = data['jobs']
        self.total_tasks = data['total_tasks']
        self.total_jobs = data['total_jobs']

        # Internal optimized state
        self.timeline = {m: [] for m in range(self.machines_count)}  # per-machine schedule (append/pop only)

        # Best solution
        self.best_timeline = None
        self.best_makespan = float('inf')

        # O(1) tracking arrays for search state
        self.machine_end = [0] * self.machines_count   # finish time of last scheduled task on machine m
        self.job_end = {}                              # finish time of last scheduled task for job j
        self.job_next_index = {}                       # next task index (1-based task_id) to schedule for each job
        self.job_remaining_work = {}                   # remaining total execution time for each job
        self.total_remaining_work = 0                  # total remaining work across all jobs

        # Build job_tasks mapping job_id -> list of task dicts (sorted by task_id)
        self.job_tasks = {}
        for job in self.jobs:
            jid = job['job_id']
            # ensure each task dict includes execution_time and task_id
            tlist = job.get('tasks', [])
            tlist_sorted = sorted(tlist, key=lambda x: x['task_id'])
            self.job_tasks[jid] = tlist_sorted

        # Initialize trackers per job
        for jid, tlist in self.job_tasks.items():
            self.job_next_index[jid] = 1
            self.job_end[jid] = 0
            rem = sum(tt['execution_time'] for tt in tlist)
            self.job_remaining_work[jid] = rem
            self.total_remaining_work += rem

        # Counters + debug stats
        self.nodes_explored = 0
        self.bounds_calculated = 0
        self.constraint_checks = 0
        self.pruned_branches = 0
        self.solutions_found = 0
        self.branch_attempts = 0
        self.priority_queue_size = 0  # kept for compatibility
        self.utilization_pruning = 0
        
        # Utilization targets
        self.target_utilization = 0.90  # Target 90% utilization
        self.min_acceptable_utilization = 0.80  # Minimum 80% utilization
        
        # State caching for redundant exploration detection
        self.state_cache = set()  # Stores state hashes to avoid redundant explorations

        # Timing
        self.start_time = None
        self.execution_time = 0

    # ------------------------------
    # Greedy initial solution (UB)
    # ------------------------------
    def _get_greedy_solution(self):
        """
        Greedy: schedule jobs in descending total work order.
        Places each task at machine_end (no gap-fitting).
        """
        temp_machine_end = [0] * self.machines_count
        temp_job_end = {j: 0 for j in self.job_tasks}
        temp_timeline = {m: [] for m in range(self.machines_count)}

        # Order jobs by total work descending
        job_order = sorted(self.job_tasks.keys(), key=lambda j: -sum(t['execution_time'] for t in self.job_tasks[j]))

        for j in job_order:
            for task in self.job_tasks[j]:
                # choose machine greedily by earliest start
                best_m = 0
                best_start = float('inf')
                for m in range(self.machines_count):
                    start = max(temp_job_end[j], temp_machine_end[m])
                    if start < best_start:
                        best_start = start
                        best_m = m
                exec_t = task['execution_time']
                finish = best_start + exec_t
                temp_timeline[best_m].append({
                    'job_id': j,
                    'task_id': task['task_id'],
                    'start_time': best_start,
                    'end_time': finish,
                    'execution_time': exec_t,
                    'machine': best_m
                })
                temp_machine_end[best_m] = finish
                temp_job_end[j] = finish

        greedy_makespan = max(temp_machine_end) if temp_machine_end else 0
        if greedy_makespan < self.best_makespan:
            self.best_makespan = greedy_makespan
            self.best_timeline = copy.deepcopy(temp_timeline)
        return greedy_makespan

    # ------------------------------
    # Lower bound 
    # ------------------------------
    def _calculate_advanced_lower_bound(self):
        """
        Enhanced lower bound with improved critical path analysis and utilization consideration.
        """
        self.bounds_calculated += 1
        
        # Standard bounds
        current_max_machine = max(self.machine_end) if self.machine_end else 0
        
        # Calculate remaining work more precisely
        total_remaining = 0
        job_critical_paths = []
        
        # Use the same iteration pattern as the rest of the code
        for job_id, task_list in self.job_tasks.items():
            if self.job_next_index[job_id] <= len(task_list):
                # Calculate remaining execution time for this job
                remaining_time = 0
                for task_idx in range(self.job_next_index[job_id] - 1, len(task_list)):
                    remaining_time += task_list[task_idx]['execution_time']
                
                total_remaining += remaining_time
                # Job critical path: current job end + remaining work
                job_critical_paths.append(self.job_end[job_id] + remaining_time)
        
        # Load balancing lower bound
        avg_remaining = total_remaining / self.machines_count if self.machines_count > 0 else 0
        load_balance_lb = current_max_machine + avg_remaining / 2  # Conservative
        
        # Job-based critical path
        job_critical_lb = max(job_critical_paths) if job_critical_paths else current_max_machine
        
        # Machine workload distribution bound
        machine_loads = []
        remaining_per_machine = total_remaining / self.machines_count if self.machines_count > 0 else 0
        for machine in range(self.machines_count):
            machine_loads.append(self.machine_end[machine] + remaining_per_machine * 0.8)  # Conservative
        
        machine_load_lb = max(machine_loads) if machine_loads else current_max_machine
        
        # Utilization-based lower bound
        total_work_done = sum(self.machine_end)
        if total_work_done > 0 and current_max_machine > 0:
            current_utilization = total_work_done / (current_max_machine * self.machines_count)
            if current_utilization < self.min_acceptable_utilization:
                # If utilization is too low, we need to compress the schedule
                utilization_lb = total_work_done / (self.min_acceptable_utilization * self.machines_count)
            else:
                utilization_lb = current_max_machine
        else:
            utilization_lb = current_max_machine
        
        # Return the tightest reasonable bound
        bounds = [current_max_machine, load_balance_lb, job_critical_lb, machine_load_lb, utilization_lb]
        return max(bounds)
    
    def _calculate_job_machine_interaction_bound(self):
        """
        Calculate lower bound based on job-machine interactions and dependencies.
        """
        max_interaction_bound = 0
        
        # For each pair of jobs that might share machines
        job_list = list(self.job_tasks.keys())
        for i, job_a in enumerate(job_list):
            for job_b in job_list[i+1:]:
                # Calculate minimal time if these jobs share any machine
                interaction_bound = self._calculate_job_pair_bound(job_a, job_b)
                max_interaction_bound = max(max_interaction_bound, interaction_bound)
        
        return max_interaction_bound
    
    def _calculate_job_pair_bound(self, job_a, job_b):
        """
        Calculate lower bound for a pair of jobs considering machine sharing.
        """
        # Get remaining work for each job
        work_a = self.job_remaining_work[job_a]
        work_b = self.job_remaining_work[job_b]
        
        # Earliest start times
        start_a = self.job_end[job_a]
        start_b = self.job_end[job_b]
        
        # If jobs can run in parallel on different machines
        parallel_bound = max(start_a + work_a, start_b + work_b)
        
        # If jobs must share machines (worst case: sequential)
        sequential_bound = max(start_a, start_b) + work_a + work_b
        
        # Conservative estimate: weighted average based on machine availability
        machine_sharing_factor = min(1.0, (work_a + work_b) / (self.machines_count * 10))
        
        return parallel_bound + machine_sharing_factor * (sequential_bound - parallel_bound)
    
    def _choose_critical_job(self):
        """
        Enhanced job selection using critical path analysis and utilization optimization.
        """
        best_job = None
        best_priority = -1
        
        current_utilization = self._calculate_current_utilization()
        
        for j in self.job_tasks:
            nxt_idx = self.job_next_index[j] - 1
            if nxt_idx < len(self.job_tasks[j]):
                # Calculate priority based on multiple factors
                remaining_work = self.job_remaining_work[j]
                job_urgency = self.job_end[j]  # Earlier jobs are more urgent
                
                # Critical path factor: jobs with more remaining work on critical path
                critical_path_factor = remaining_work
                
                # Machine availability factor
                next_task = self.job_tasks[j][nxt_idx]
                min_machine_available = min(self.machine_end)
                availability_factor = -min_machine_available  # Prefer jobs that can start earlier
                
                # Utilization improvement factor
                utilization_factor = 0
                if current_utilization < self.target_utilization:
                    # Prefer jobs that can start on idle machines
                    idle_machines = [m for m in range(self.machines_count) 
                                   if self.machine_end[m] == min_machine_available]
                    if len(idle_machines) > 1:
                        utilization_factor = remaining_work * 2  # Boost priority for balancing
                
                # Combined priority (higher is better)
                priority = critical_path_factor + availability_factor - job_urgency * 0.1 + utilization_factor
                
                if priority > best_priority:
                    best_priority = priority
                    best_job = j
        
        return best_job

    # ------------------------------
    # DFS-based branch-and-bound
    # ------------------------------
    def _advanced_dfs_search(self):
        """Advanced DFS with dominance rules and critical path bounds."""
        # Completion check - ALL jobs completely finished
        if all(self.job_next_index[j] > len(self.job_tasks[j]) for j in self.job_tasks):
            self.nodes_explored += 1
            self.solutions_found += 1
            current_makespan = max(self.machine_end) if self.machine_end else 0
            current_utilization = self._calculate_current_utilization()
            
            if self.nodes_explored % 10000 == 0 or current_makespan < self.best_makespan:
                print(f"✅ SOLUTION FOUND: Makespan {current_makespan}, Utilization {current_utilization:.3f}, Node #{self.nodes_explored}")
            
            if current_makespan < self.best_makespan:
                self.best_makespan = current_makespan
                # deep copy timeline
                self.best_timeline = {m: [dict(t) for t in tasks] for m, tasks in self.timeline.items()}
                print(f"🎯 NEW BEST: Makespan {current_makespan}, Utilization {current_utilization:.3f} (Previous best: {self.best_makespan if self.best_makespan != float('inf') else 'None'})")
            return

        self.nodes_explored += 1
        
        # State caching: check if we've seen this state before
        state_hash = self._compute_state_hash()
        if state_hash in self.state_cache:
            if self.nodes_explored % 10000 == 0:
                print(f"♻️  CACHED STATE: Node #{self.nodes_explored}, avoiding redundant exploration")
            return
        self.state_cache.add(state_hash)
        
        # Progress reporting
        if self.nodes_explored % 10000 == 0:
            elapsed = time.time() - self.start_time
            pruning_rate = (self.pruned_branches / max(1, self.nodes_explored)) * 100
            cache_size = len(self.state_cache)
            if(self.nodes_explored % 100000 == 0):
                print(f"📊 Nodes: {self.nodes_explored:,}, Pruned: {self.pruned_branches:,} ({pruning_rate:.1f}%), Cache: {cache_size:,}, Best: {self.best_makespan}, Time: {elapsed:.3f}s")

        # Advanced lower bound check
        lb = self._calculate_advanced_lower_bound()
        if lb >= self.best_makespan:
            self.pruned_branches += 1
            if(self.nodes_explored % 100000 == 0):
                print(f"✂️  PRUNED by LB: Node #{self.nodes_explored}, LB={lb:.1f} >= Best={self.best_makespan}")
                return
        
        # Utilization pruning - if utilization is too poor, prune
        current_utilization = self._calculate_current_utilization()
        if current_utilization < self.min_acceptable_utilization and max(self.machine_end) > 50:
            # Only prune if we're deep enough in the search
            remaining_ratio = self.total_remaining_work / sum(t['execution_time'] for tasks in self.job_tasks.values() for t in tasks)
            if remaining_ratio < 0.5:  # More than half work is done
                self.utilization_pruning += 1
                if self.nodes_explored % 10000 == 0:
                    print(f"✂️  PRUNED by UTILIZATION: Node #{self.nodes_explored}, Util={current_utilization:.2f} < {self.min_acceptable_utilization}")
                return
        
        # Disable state caching for now to allow full exploration
        # state_key = self._get_state_key()
        # if state_key in self.state_cache:
        #     if self.state_cache[state_key] >= self.best_makespan:
        #         print(f"♻️  PRUNED by CACHE: Node #{self.nodes_explored}, cached bound >= {self.best_makespan}")
        #         return
        # self.state_cache[state_key] = self.best_makespan

        # DOMINANCE RULE #1: Forced moves (immediate improvements)
        forced_assignment = self._find_forced_assignment()
        if forced_assignment:
            job_id, task, machine = forced_assignment
            self.forced_moves += 1
            if(self.nodes_explored % 100000 == 0):
                print(f"⚡ FORCED MOVE: Node #{self.nodes_explored}, Job {job_id} Task {task['task_id']} → Machine {machine}")
            self._execute_assignment(job_id, task, machine)
            self._advanced_dfs_search()
            self._undo_assignment(job_id, task, machine)
            return

        # Choose job to branch on with advanced heuristics
        job_id = self._choose_critical_job()
        if job_id is None:
            if self.nodes_explored % 10000 == 0:
                print(f"🚫 NO JOBS: Node #{self.nodes_explored}, no available jobs to schedule")
            return

        # Next task for that job
        nxt_idx = self.job_next_index[job_id] - 1
        task = self.job_tasks[job_id][nxt_idx]
        exec_time = task['execution_time']

        # Get valid machines with dominance ordering
        valid_assignments = self._get_valid_assignments_with_dominance(job_id, task)
        if self.nodes_explored % 10000 == 0:
            print(f"🌿 BRANCHING: Node #{self.nodes_explored}, Job {job_id} Task {task['task_id']} → {len(valid_assignments)} machines")
        
        for i, (machine, start_time) in enumerate(valid_assignments):
            finish_time = start_time + exec_time

            # Early pruning: if this single task would exceed current best, skip
            if finish_time >= self.best_makespan:
                self.pruned_branches += 1
                print(f"✂️  EARLY PRUNE: Task finish {finish_time} >= best {self.best_makespan}")
                continue

            if self.nodes_explored % 10000 == 0:
                print(f"🔍 EXPLORING: Branch {i+1}/{len(valid_assignments)}, Job {job_id} Task {task['task_id']} → Machine {machine} at {start_time}")
            
            # Apply assignment
            self._execute_assignment(job_id, task, machine)
            
            # Enhanced pruning with advanced bounds
            advanced_lb = self._calculate_advanced_lower_bound()
            if advanced_lb < self.best_makespan:
                if self.nodes_explored % 10000 == 0:
                    print(f"➡️  RECURSE: LB={advanced_lb:.1f} < Best={self.best_makespan}, going deeper...")
                # Recurse
                self._advanced_dfs_search()
            else:
                self.pruned_branches += 1
                if self.nodes_explored % 10000 == 0:
                    print(f"✂️  PRUNED by advanced LB: LB={advanced_lb:.1f} >= Best={self.best_makespan}")

            # Undo assignment
            self._undo_assignment(job_id, task, machine)
            if self.nodes_explored % 10000 == 0:
                print(f"⬅️  BACKTRACK: Undid Job {job_id} Task {task['task_id']} from Machine {machine}")
        
        self.execution_time = time.time() - self.start_time
    
    def _find_forced_assignment(self):
        """DOMINANCE RULE #1: Conservative forced assignment.
        Currently disabled since all machines can handle all tasks in this dataset."""
        # For this dataset, all machines can handle all tasks,
        # so forced assignment won't help. Keep disabled for now.
        return None
    
    def _can_assign_task(self, job_id, task, machine_id):
        """Check if a task can be assigned to a machine (precedence constraints)."""
        # Check if all dependencies are satisfied
        for dep in task['dependencies']:
            if not self.state.is_task_completed(job_id, dep):
                return False
        return True
    
    def _compute_state_hash(self):
        """Compute a hash representing the current scheduling state."""
        # Create a representation that captures the essential state:
        # - Which tasks have been scheduled for each job
        # - Machine availability times (rounded for stability)
        state_parts = []
        
        # Job progress: which task each job is on
        for job_id in sorted(self.job_tasks.keys()):
            next_task = self.job_next_index.get(job_id, 1)
            state_parts.append(f"J{job_id}:{next_task}")
        
        # Machine availability (rounded to avoid floating point precision issues)
        machine_times = []
        for m in range(self.machines_count):
            # Round to 1 decimal place for stable hashing
            rounded_time = round(self.machine_end[m], 1)
            machine_times.append(f"M{m}:{rounded_time}")
        
        state_parts.extend(machine_times)
        
        # Create hash from sorted representation
        state_str = "|".join(sorted(state_parts))
        return hash(state_str)
    
    def _calculate_current_utilization(self):
        """Calculate current machine utilization."""
        if not self.machine_end or max(self.machine_end) == 0:
            return 0.0
        
        total_work_time = sum(self.machine_end)
        total_possible_time = max(self.machine_end) * self.machines_count
        return total_work_time / total_possible_time if total_possible_time > 0 else 0.0
    
    def _get_valid_assignments_with_dominance(self, job_id, task):
        """Get valid assignments with utilization-aware dominance ordering."""
        valid = []
        current_utilization = self._calculate_current_utilization()
        
        # Get all valid machines with their start times
        machine_times = []
        for machine in range(self.machines_count):
            start_time = max(self.job_end[job_id], self.machine_end[machine])
            machine_times.append((machine, start_time))
        
        # Sort by utilization-aware priority
        if current_utilization < self.target_utilization:
            # Prioritize machines that improve utilization (idle machines first)
            min_end_time = min(self.machine_end)
            machine_times.sort(key=lambda x: (0 if self.machine_end[x[0]] == min_end_time else 1, x[1]))
        else:
            # Standard sorting by availability time
            machine_times.sort(key=lambda x: x[1])
        
        # Return sorted assignments
        return machine_times
    
    def _execute_assignment(self, job_id, task, machine):
        """Execute a task assignment."""
        start_time = max(self.job_end[job_id], self.machine_end[machine])
        finish_time = start_time + task['execution_time']
        
        # Update tracking
        prev_machine_end = self.machine_end[machine]
        prev_job_end = self.job_end[job_id]
        prev_job_rem = self.job_remaining_work[job_id]
        prev_total_rem = self.total_remaining_work
        
        self.machine_end[machine] = finish_time
        self.job_end[job_id] = finish_time
        self.job_remaining_work[job_id] -= task['execution_time']
        self.total_remaining_work -= task['execution_time']
        
        # Update timeline
        self.timeline[machine].append({
            'job_id': job_id,
            'task_id': task['task_id'],
            'start_time': start_time,
            'end_time': finish_time,
            'execution_time': task['execution_time'],
            'machine': machine,
            '_prev_state': (prev_machine_end, prev_job_end, prev_job_rem, prev_total_rem)
        })
        
        # Advance job pointer
        self.job_next_index[job_id] += 1
    
    def _undo_assignment(self, job_id, task, machine):
        """Undo a task assignment."""
        # Remove from timeline and restore state
        assignment = self.timeline[machine].pop()
        prev_machine_end, prev_job_end, prev_job_rem, prev_total_rem = assignment['_prev_state']
        
        self.machine_end[machine] = prev_machine_end
        self.job_end[job_id] = prev_job_end
        self.job_remaining_work[job_id] = prev_job_rem
        self.total_remaining_work = prev_total_rem
        
        # Restore job pointer
        self.job_next_index[job_id] -= 1
    
    def _get_state_key(self):
        """Generate a compact state key for caching."""
        # Use job progress and machine states as key
        job_states = tuple(sorted((j, self.job_next_index[j], self.job_end[j]) for j in self.job_tasks))
        machine_states = tuple(self.machine_end)
        return (job_states, machine_states)

    def _get_all_tasks_ordered(self):
        """Get all tasks ordered by job dependency and work remaining."""
        all_tasks = []
        for job_id, tasks in self.job_tasks.items():
            for task in tasks:
                all_tasks.append((job_id, task))
        
        # Sort by job total work (descending), then task_id
        job_totals = {j: sum(t['execution_time'] for t in tasks) for j, tasks in self.job_tasks.items()}
        all_tasks.sort(key=lambda x: (-job_totals[x[0]], x[1]['task_id']))
        return all_tasks
    
    def _select_critical_task(self, state):
        """Select the most critical task to schedule next."""
        remaining = state['remaining_tasks']
        if not remaining:
            return None
            
        # Find tasks that are ready to schedule (no dependency violations)
        ready_tasks = []
        scheduled_tasks = {(t[0], t[1]): True for t in state['scheduled_tasks']}
        
        for job_id, task in remaining:
            task_id = task['task_id']
            # Check if previous task in job is scheduled
            if task_id == 1 or (job_id, task_id - 1) in scheduled_tasks:
                ready_tasks.append((job_id, task))
        
        if not ready_tasks:
            return remaining[0]  # Fallback
        
        # Choose task with earliest deadline pressure
        best_task = None
        best_pressure = float('inf')
        
        for job_id, task in ready_tasks:
            # Calculate pressure: remaining job work / remaining tasks in job
            remaining_in_job = len([t for jid, t in remaining if jid == job_id])
            if remaining_in_job > 0:
                job_work = sum(t['execution_time'] for jid, t in remaining if jid == job_id)
                pressure = job_work / remaining_in_job + state['job_end'][job_id]
                
                if pressure < best_pressure:
                    best_pressure = pressure
                    best_task = (job_id, task)
        
        return best_task or ready_tasks[0]
    
    def _get_best_machines(self, task_job, state, max_machines=2):
        """Get best machines for a task, limited to max_machines."""
        job_id, task = task_job
        machine_scores = []
        
        for machine in range(self.machines_count):
            # Calculate earliest start time
            job_ready = state['job_end'][job_id]
            machine_ready = state['machine_end'][machine]
            start_time = max(job_ready, machine_ready)
            
            # Score: start time + small penalty for machine load
            machine_load = state['machine_end'][machine]
            score = start_time + machine_load * 0.01
            machine_scores.append((score, machine))
        
        # Return top machines
        machine_scores.sort()
        return [machine for _, machine in machine_scores[:max_machines]]
    
    def _create_successor_state(self, state, task_job, machine):
        """Create new state by scheduling task on machine."""
        job_id, task = task_job
        task_id = task['task_id']
        exec_time = task['execution_time']
        
        # Calculate start time
        job_ready = state['job_end'][job_id]
        machine_ready = state['machine_end'][machine]
        start_time = max(job_ready, machine_ready)
        end_time = start_time + exec_time
        
        # Create new state
        new_scheduled = state['scheduled_tasks'] + [(job_id, task_id, machine, start_time)]
        new_machine_end = state['machine_end'].copy()
        new_machine_end[machine] = end_time
        new_job_end = state['job_end'].copy()
        new_job_end[job_id] = end_time
        
        # Remove task from remaining
        new_remaining = [(j, t) for j, t in state['remaining_tasks'] if not (j == job_id and t['task_id'] == task_id)]
        
        return {
            'scheduled_tasks': new_scheduled,
            'machine_end': new_machine_end,
            'job_end': new_job_end,
            'remaining_tasks': new_remaining
        }
    
    def _calculate_tight_lower_bound(self, state):
        """Calculate tight lower bound for state."""
        if not state['remaining_tasks']:
            return max(state['machine_end']) if state['machine_end'] else 0
        
        # Current makespan
        current_makespan = max(state['machine_end'])
        
        # Load balancing bound
        remaining_work = sum(task['execution_time'] for _, task in state['remaining_tasks'])
        min_machine_end = min(state['machine_end'])
        load_bound = min_machine_end + remaining_work / self.machines_count
        
        # Job critical path bounds
        job_bounds = []
        remaining_by_job = {}
        for job_id, task in state['remaining_tasks']:
            if job_id not in remaining_by_job:
                remaining_by_job[job_id] = 0
            remaining_by_job[job_id] += task['execution_time']
        
        for job_id, remaining_work in remaining_by_job.items():
            job_bound = state['job_end'][job_id] + remaining_work
            job_bounds.append(job_bound)
        
        critical_bound = max(job_bounds) if job_bounds else 0
        
        return max(current_makespan, load_bound, critical_bound)
    
    def _reconstruct_timeline(self, scheduled_tasks):
        """Reconstruct timeline from scheduled tasks list."""
        timeline = {m: [] for m in range(self.machines_count)}
        
        for job_id, task_id, machine, start_time in scheduled_tasks:
            # Find the task details
            task_info = None
            for task in self.job_tasks[job_id]:
                if task['task_id'] == task_id:
                    task_info = task
                    break
            
            if task_info:
                exec_time = task_info['execution_time']
                timeline[machine].append({
                    'job_id': job_id,
                    'task_id': task_id,
                    'start_time': start_time,
                    'end_time': start_time + exec_time,
                    'execution_time': exec_time,
                    'machine': machine
                })
        
        return timeline



    def schedule_tasks(self):
        """
        Find the optimal schedule using advanced branch-and-bound with dominance rules.
        """
        # Reset dynamic state
        self.timeline = {m: [] for m in range(self.machines_count)}
        self.machine_end = [0] * self.machines_count
        for j in self.job_tasks:
            self.job_next_index[j] = 1
            self.job_end[j] = 0
            self.job_remaining_work[j] = sum(t['execution_time'] for t in self.job_tasks[j])
        self.total_remaining_work = sum(self.job_remaining_work.values())

        # reset best
        self.best_timeline = None
        self.best_makespan = float('inf')

        # reset counters
        self.nodes_explored = 0
        self.bounds_calculated = 0
        self.constraint_checks = 0
        self.pruned_branches = 0
        self.solutions_found = 0
        self.branch_attempts = 0
        self.priority_queue_size = 0
        
        # State cache for avoiding revisits
        self.state_cache = set()
        self.forced_moves = 0
        self.dominance_pruning = 0

        self.start_time = time.time()

        print("Starting advanced branch-and-bound with dominance rules...")
        print(f"Problem size: {self.total_tasks} tasks, {self.total_jobs} jobs, {self.machines_count} machines")

        # No initial upper bound - explore full search space
        print("No initial upper bound set - exploring full search space")
        
        # start advanced DFS b&b
        self._advanced_dfs_search()
        
        # Print final statistics
        elapsed = time.time() - self.start_time
        total_decisions = self.nodes_explored + self.pruned_branches + self.forced_moves
        pruning_efficiency = (self.pruned_branches / max(1, total_decisions)) * 100
        
        print(f"\n🏁 SEARCH COMPLETED!")
        print(f"📊 Total nodes explored: {self.nodes_explored:,}")
        print(f"✂️  Total branches pruned: {self.pruned_branches:,}")
        print(f"⚡ Total forced moves: {self.forced_moves:,}")
        print(f"📉 Utilization pruning: {self.utilization_pruning:,}")
        print(f"📈 Pruning efficiency: {pruning_efficiency:.1f}%")
        print(f"🎯 Solutions found: {self.solutions_found:,}")
        print(f"⏱️  Total time: {elapsed:.6f} seconds")
        print(f"🚀 Speed: {self.nodes_explored/max(elapsed, 0.000001):.0f} nodes/second")

        if self.best_timeline is not None:
            self.timeline = self.best_timeline
            self.get_metrics()
            return True
        elif hasattr(self, 'greedy_timeline') and self.greedy_timeline is not None:
            # Fallback to greedy solution if no better solution found
            print(f"Using greedy solution as best result: {self.greedy_makespan}")
            self.timeline = self.greedy_timeline
            self.best_makespan = self.greedy_makespan
            self.get_metrics()
            return True
        else:
            return False

    # ------------------------------
    # Metrics & printing
    # ------------------------------
    def _calculate_makespan(self):
        makespan = 0
        for machine_timeline in self.timeline.values():
            for task in machine_timeline:
                makespan = max(makespan, task['end_time'])
        return makespan

    def get_metrics(self):
        if not self.timeline:
            return {}

        makespan = self._calculate_makespan()

        total_machine_utilization = 0.0
        total_idle_time = 0

        for m in range(self.machines_count):
            machine_timeline = self.timeline.get(m, [])
            if machine_timeline:
                sorted_tasks = sorted(machine_timeline, key=lambda t: t['start_time'])
                machine_end_time = max(task['end_time'] for task in sorted_tasks)
                machine_work_time = sum(task['execution_time'] for task in sorted_tasks)
                machine_utilization = (machine_work_time / makespan) if makespan > 0 else 0
                total_machine_utilization += machine_utilization

                first_start = sorted_tasks[0]['start_time']
                total_idle_time += first_start
                for i in range(1, len(sorted_tasks)):
                    prev_end = sorted_tasks[i-1]['end_time']
                    cur_start = sorted_tasks[i]['start_time']
                    if cur_start > prev_end:
                        total_idle_time += (cur_start - prev_end)
                if makespan > machine_end_time:
                    total_idle_time += (makespan - machine_end_time)
            else:
                total_idle_time += makespan

        self.machine_utilization = (total_machine_utilization / self.machines_count) if self.machines_count else 0
        self.total_idle_time = total_idle_time
        self.execution_time = time.time() - (self.start_time if self.start_time else time.time())

        return {
            'makespan': makespan,
            'total_idle_time': self.total_idle_time,
            'machine_utilization': self.machine_utilization,
            'execution_time': self.execution_time
        }

    def _print_debug_stats(self, elapsed_time=None):
        if elapsed_time is None:
            elapsed_time = self.execution_time
        print(f"\n=== BRANCH AND BOUND PERFORMANCE ===")
        print(f"Total nodes explored: {self.nodes_explored:,}")
        print(f"Bounds calculated: {self.bounds_calculated:,}")
        print(f"Constraint checks: {self.constraint_checks:,}")
        print(f"Pruned branches: {self.pruned_branches:,}")
        print(f"Complete solutions found: {self.solutions_found:,}")
        print(f"Search time: {elapsed_time:.2f} seconds")
        print(f"Max queue size reached: {self.priority_queue_size:,}")
        if self.nodes_explored > 0 and elapsed_time > 0:
            print(f"Nodes per second: {self.nodes_explored/elapsed_time:.0f}")
            print(f"Bounds per second: {self.bounds_calculated/elapsed_time:.0f}")
            if self.branch_attempts > 0:
                print(f"Actual pruning efficiency: {(self.pruned_branches/self.branch_attempts)*100:.1f}%")
        if self.best_makespan != float('inf'):
            print(f"Best makespan found: {self.best_makespan}")
        else:
            print("No valid solution found")

    def print_schedule(self):
        if not self.timeline:
            print("No schedule found.")
            return

        print("\n=== OPTIMAL SCHEDULE ===")
        for machine in sorted(self.timeline.keys()):
            print(f"\nMachine {machine}:")
            mtasks = self.timeline[machine]
            if not mtasks:
                print("  No tasks assigned")
                continue
            sorted_tasks = sorted(mtasks, key=lambda t: t['start_time'])
            for task in sorted_tasks:
                print(f"  Job {task['job_id']}, Task {task['task_id']}: "
                      f"Time {task['start_time']}-{task['end_time']} "
                      f"(Duration: {task['execution_time']})")
        metrics = self.get_metrics()
        print("\n=== METRICS ===")
        print(f"Makespan: {metrics.get('makespan')}")
        print(f"Total idle time: {metrics.get('total_idle_time')}")
        print(f"Average machine utilization: {metrics.get('machine_utilization'):.3f}")
        print(f"Execution time (s): {metrics.get('execution_time'):.3f}")
