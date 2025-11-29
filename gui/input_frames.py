"""
Input frames for the Job Schedule Application GUI.
Handles user input for machine count, job count, and task details.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from .constants import MAX_MACHINES, MAX_JOBS, MAX_TOTAL_TASKS, MAX_TASKS_PER_JOB


class BasicInputFrame(tk.Frame):
    """Frame for inputting machine count and job count."""

    def __init__(self, parent, on_submit_callback=None):
        super().__init__(parent)
        self.on_submit_callback = on_submit_callback
        self.machine_count_var = tk.IntVar(value=1)
        self.job_count_var = tk.IntVar(value=1)
        
        self.create_widgets()

    def create_widgets(self):
        """Create and layout widgets for basic inputs."""
        # Center the grid within the frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(3, weight=1)
        
        # Title
        title_label = tk.Label(
            self, 
            text="Job Scheduling Configuration", 
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=1, column=1, columnspan=2, pady=10)

        # Machine Count
        machine_label = tk.Label(self, text="Number of Machines:", font=("Arial", 11))
        machine_label.grid(row=2, column=1, sticky="e", padx=10, pady=5)
        
        machine_spinbox = tk.Spinbox(
            self,
            from_=1,
            to=MAX_MACHINES,
            textvariable=self.machine_count_var,
            width=10,
            font=("Arial", 11)
        )
        machine_spinbox.grid(row=2, column=2, sticky="w", padx=5, pady=5)
        
        machine_limit_label = tk.Label(
            self,
            text=f"(Max: {MAX_MACHINES})",
            font=("Arial", 9),
            fg="gray"
        )
        machine_limit_label.grid(row=2, column=3, sticky="w", padx=5, pady=5)

        # Job Count
        job_label = tk.Label(self, text="Number of Jobs:", font=("Arial", 11))
        job_label.grid(row=3, column=1, sticky="e", padx=10, pady=5)
        
        job_spinbox = tk.Spinbox(
            self,
            from_=1,
            to=MAX_JOBS,
            textvariable=self.job_count_var,
            width=10,
            font=("Arial", 11)
        )
        job_spinbox.grid(row=3, column=2, sticky="w", padx=5, pady=5)
        
        job_limit_label = tk.Label(
            self,
            text=f"(Max: {MAX_JOBS})",
            font=("Arial", 9),
            fg="gray"
        )
        job_limit_label.grid(row=3, column=3, sticky="w", padx=5, pady=5)

        # Submit Button
        submit_button = tk.Button(
            self,
            text="Configure Jobs",
            command=self.on_submit,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=5
        )
        submit_button.grid(row=4, column=1, columnspan=2, pady=15)

    def on_submit(self):
        """Handle submission of basic inputs."""
        machine_count = self.machine_count_var.get()
        job_count = self.job_count_var.get()
        
        if machine_count < 1:
            messagebox.showerror("Invalid Input", "Number of machines must be at least 1")
            return
        
        if machine_count > MAX_MACHINES:
            messagebox.showerror("Invalid Input", f"Number of machines cannot exceed {MAX_MACHINES}")
            return
        
        if job_count < 1:
            messagebox.showerror("Invalid Input", "Number of jobs must be at least 1")
            return
        
        if job_count > MAX_JOBS:
            messagebox.showerror("Invalid Input", f"Number of jobs cannot exceed {MAX_JOBS}")
            return
        
        if self.on_submit_callback:
            self.on_submit_callback(machine_count, job_count)

    def get_values(self):
        """Get current values."""
        return self.machine_count_var.get(), self.job_count_var.get()


class TaskInputFrame(tk.Frame):
    """Frame for inputting task details in a table format."""

    def __init__(self, parent, machine_count, job_count, on_submit_callback=None):
        super().__init__(parent)
        self.machine_count = machine_count
        self.job_count = job_count
        self.on_submit_callback = on_submit_callback
        self.task_entries = {}  # Dictionary to store entry widgets
        self.task_count_vars = {}  # Dictionary to store task count spinbox variables
        
        self.create_widgets()

    def create_widgets(self):
        """Create task input table."""
        # Title
        title_label = tk.Label(
            self,
            text=f"Task Configuration ({self.job_count} Jobs)",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        info_label = tk.Label(
            self,
            text=f"Machines: {self.machine_count} | Jobs: {self.job_count} | Max Total Tasks: {MAX_TOTAL_TASKS}",
            font=("Arial", 10),
            fg="gray"
        )
        info_label.pack(pady=5)

        # Create scrollable frame for tasks
        canvas_frame = tk.Frame(self)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(canvas_frame, height=400)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create task input rows
        for job_idx in range(self.job_count):
            self.create_job_section(scrollable_frame, job_idx)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Buttons frame
        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, padx=15, pady=15)
        
        submit_button = tk.Button(
            button_frame,
            text="Submit All Tasks",
            command=self.on_submit,
            bg="#2196F3",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=8
        )
        submit_button.pack(side="left", padx=5)
        
        reset_button = tk.Button(
            button_frame,
            text="Reset",
            command=self.reset_values,
            bg="#f44336",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=8
        )
        reset_button.pack(side="left", padx=5)

    def create_job_section(self, parent, job_idx):
        """Create input section for a single job."""
        # Job header
        job_header = tk.Label(
            parent,
            text=f"Job {job_idx + 1}",
            font=("Arial", 11, "bold"),
            bg="#E8F5E9",
            padx=10,
            pady=5
        )
        job_header.grid(row=job_idx * 3, column=0, columnspan=3, sticky="ew", pady=(10, 5))
        
        # Task count spinbox
        task_label = tk.Label(parent, text="Number of Tasks:", font=("Arial", 10))
        task_label.grid(row=job_idx * 3 + 1, column=0, sticky="w", padx=20, pady=5)
        
        task_count_var = tk.IntVar(value=1)
        self.task_count_vars[job_idx] = task_count_var  # Store for later reset
        task_spinbox = tk.Spinbox(
            parent,
            from_=1,
            to=MAX_TASKS_PER_JOB,
            textvariable=task_count_var,
            width=5,
            font=("Arial", 10)
        )
        task_spinbox.grid(row=job_idx * 3 + 1, column=1, sticky="w", padx=10, pady=5)
        
        task_limit_label = tk.Label(
            parent,
            text=f"(Max: {MAX_TASKS_PER_JOB})",
            font=("Arial", 9),
            fg="gray"
        )
        task_limit_label.grid(row=job_idx * 3 + 1, column=2, sticky="w", padx=5, pady=5)
        
        # Create tasks table for this job
        tasks_frame = tk.Frame(parent)
        tasks_frame.grid(row=job_idx * 3 + 2, column=0, columnspan=3, sticky="ew", padx=20, pady=5)
        
        # Table headers
        headers = ["Task #", "Execution Time (ms)"]
        for col, header in enumerate(headers):
            header_label = tk.Label(
                tasks_frame,
                text=header,
                font=("Arial", 9, "bold"),
                bg="#BDBDBD",
                padx=10,
                pady=5,
                relief="solid",
                borderwidth=1
            )
            header_label.grid(row=0, column=col, sticky="ew", padx=2, pady=2)
        
        # Store all widgets for this job (labels and entries)
        self.task_entries[job_idx] = {'entries': [], 'labels': [], 'frame': tasks_frame}
        self.update_task_entries(tasks_frame, job_idx, task_count_var, initial=True)
        
        # Bind spinbox to update tasks
        def on_task_count_change(*args):
            try:
                self.update_task_entries(tasks_frame, job_idx, task_count_var)
            except tk.TclError:
                # Ignore errors when spinbox is being edited
                pass
        
        task_count_var.trace("w", on_task_count_change)

    def update_task_entries(self, tasks_frame, job_idx, task_count_var, initial=False):
        """Update task entry fields based on task count."""
        try:
            new_task_count = task_count_var.get()
        except tk.TclError:
            # Handle case where spinbox value is invalid/empty
            return
        
        # Clear existing entries and labels if not initial
        if not initial and job_idx in self.task_entries:
            # Destroy all entry widgets
            for entry in self.task_entries[job_idx]['entries']:
                entry.destroy()
            # Destroy all label widgets
            for label in self.task_entries[job_idx]['labels']:
                label.destroy()
            # Reset the lists
            self.task_entries[job_idx]['entries'] = []
            self.task_entries[job_idx]['labels'] = []
        
        # Create new entry fields
        for task_idx in range(new_task_count):
            # Task number label
            task_num_label = tk.Label(
                tasks_frame,
                text=f"Task {task_idx + 1}",
                font=("Arial", 9),
                padx=10,
                pady=5,
                relief="solid",
                borderwidth=1
            )
            task_num_label.grid(row=task_idx + 1, column=0, sticky="ew", padx=2, pady=2)
            
            # Execution time entry
            time_entry = tk.Entry(
                tasks_frame,
                width=15,
                font=("Arial", 9)
            )
            time_entry.insert(0, "0")
            time_entry.grid(row=task_idx + 1, column=1, sticky="ew", padx=2, pady=2)
            
            self.task_entries[job_idx]['entries'].append(time_entry)
            self.task_entries[job_idx]['labels'].append(task_num_label)

    def get_all_tasks(self):
        """Retrieve all task data from the table."""
        jobs_data = []
        total_tasks = 0
        
        for job_idx in range(self.job_count):
            tasks = []
            for task_idx, entry in enumerate(self.task_entries[job_idx]['entries']):
                try:
                    exec_time = int(entry.get())
                    if exec_time <= 0:
                        raise ValueError("Execution time must be greater than 0")
                    tasks.append(exec_time)
                except ValueError as e:
                    messagebox.showerror(
                        "Invalid Input",
                        f"Job {job_idx + 1}, Task {task_idx + 1}: Please enter a valid execution time (must be > 0)"
                    )
                    return None
            
            # Check per-job task limit
            if len(tasks) > MAX_TASKS_PER_JOB:
                messagebox.showerror(
                    "Input Limit Exceeded",
                    f"Job {job_idx + 1} has {len(tasks)} tasks, which exceeds the limit of {MAX_TASKS_PER_JOB} tasks per job."
                )
                return None
            
            total_tasks += len(tasks)
            jobs_data.append({"job_id": job_idx + 1, "tasks": tasks})
        
        # Check total tasks limit
        if total_tasks > MAX_TOTAL_TASKS:
            messagebox.showerror(
                "Input Limit Exceeded",
                f"Total number of tasks ({total_tasks}) cannot exceed {MAX_TOTAL_TASKS}.\n\n"
                f"Please reduce the number of tasks across your jobs."
            )
            return None
        
        return jobs_data

    def on_submit(self):
        """Handle submission of all tasks."""
        jobs_data = self.get_all_tasks()
        if jobs_data and self.on_submit_callback:
            self.on_submit_callback(self.machine_count, self.job_count, jobs_data)

    def reset_values(self):
        """Reset all entries and task counts to default values."""
        for job_idx in self.task_count_vars:
            # Reset task count spinbox to 1
            self.task_count_vars[job_idx].set(1)
            
            # Also reset all entry values to 0
            if job_idx in self.task_entries:
                for entry in self.task_entries[job_idx]['entries']:
                    entry.delete(0, tk.END)
                    entry.insert(0, "0")
