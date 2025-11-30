"""
Input frames for the Job Schedule Application GUI.
Handles user input for machine count, job count, and task details.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from .constants import MAX_MACHINES, MAX_JOBS, MAX_TOTAL_TASKS, MAX_TASKS_PER_JOB, COLORS, FONTS, PADDING


class BasicInputFrame(tk.Frame):
    """Frame for inputting machine count and job count."""

    def __init__(self, parent, on_submit_callback=None):
        super().__init__(parent, bg=COLORS['light_bg'])
        self.on_submit_callback = on_submit_callback
        self.machine_count_var = tk.IntVar(value=2)
        self.job_count_var = tk.IntVar(value=3)

        self.create_widgets()

    def create_widgets(self):
        """Create and layout widgets for basic inputs."""
        # Main container with better spacing
        main_container = tk.Frame(self, bg=COLORS['light_bg'], padx=PADDING['xlarge'], pady=PADDING['xlarge'])
        main_container.pack(expand=True, fill=tk.BOTH)

        # Title section
        title_frame = tk.Frame(main_container, bg=COLORS['light_bg'])
        title_frame.pack(pady=(0, PADDING['xlarge']))

        title_label = tk.Label(
            title_frame,
            text="Job Scheduling Configuration",
            font=FONTS['title'],
            bg=COLORS['light_bg'],
            fg=COLORS['primary_dark']
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text="Configure the basic parameters for your scheduling problem",
            font=FONTS['small'],
            bg=COLORS['light_bg'],
            fg=COLORS['text_light']
        )
        subtitle_label.pack(pady=(5, 0))

        # Input container with card-like appearance
        input_card = tk.Frame(
            main_container,
            bg='white',
            relief='solid',
            borderwidth=1,
            padx=PADDING['large'],
            pady=PADDING['large']
        )
        input_card.pack(fill=tk.X, pady=PADDING['medium'])

        # Machine Count
        machine_frame = tk.Frame(input_card, bg='white')
        machine_frame.pack(fill=tk.X, pady=PADDING['medium'])

        machine_label = tk.Label(
            machine_frame,
            text="Number of Machines:",
            font=FONTS['subheader'],
            bg='white',
            fg=COLORS['text_dark']
        )
        machine_label.pack(side=tk.LEFT, padx=(0, PADDING['medium']))

        machine_spinbox = tk.Spinbox(
            machine_frame,
            from_=1,
            to=MAX_MACHINES,
            textvariable=self.machine_count_var,
            width=8,
            font=FONTS['body'],
            justify='center',
            relief='solid',
            borderwidth=1
        )
        machine_spinbox.pack(side=tk.LEFT, padx=(0, PADDING['small']))

        machine_limit_label = tk.Label(
            machine_frame,
            text=f"Maximum: {MAX_MACHINES}",
            font=FONTS['small'],
            bg='white',
            fg=COLORS['text_light']
        )
        machine_limit_label.pack(side=tk.LEFT)

        # Job Count
        job_frame = tk.Frame(input_card, bg='white')
        job_frame.pack(fill=tk.X, pady=PADDING['medium'])

        job_label = tk.Label(
            job_frame,
            text="Number of Jobs:",
            font=FONTS['subheader'],
            bg='white',
            fg=COLORS['text_dark']
        )
        job_label.pack(side=tk.LEFT, padx=(0, PADDING['medium']))

        job_spinbox = tk.Spinbox(
            job_frame,
            from_=1,
            to=MAX_JOBS,
            textvariable=self.job_count_var,
            width=8,
            font=FONTS['body'],
            justify='center',
            relief='solid',
            borderwidth=1
        )
        job_spinbox.pack(side=tk.LEFT, padx=(0, PADDING['small']))

        job_limit_label = tk.Label(
            job_frame,
            text=f"Maximum: {MAX_JOBS}",
            font=FONTS['small'],
            bg='white',
            fg=COLORS['text_light']
        )
        job_limit_label.pack(side=tk.LEFT)

        # Submit Button
        button_frame = tk.Frame(main_container, bg=COLORS['light_bg'])
        button_frame.pack(pady=PADDING['xlarge'])

        submit_button = tk.Button(
            button_frame,
            text="Configure Tasks →",
            command=self.on_submit,
            bg=COLORS['primary'],
            fg="white",
            font=FONTS['subheader'],
            padx=30,
            pady=12,
            cursor="hand2",
            relief="flat",
            bd=0
        )
        submit_button.pack()

        # Add hover effect
        def on_enter(e):
            submit_button['bg'] = COLORS['primary_dark']

        def on_leave(e):
            submit_button['bg'] = COLORS['primary']

        submit_button.bind("<Enter>", on_enter)
        submit_button.bind("<Leave>", on_leave)

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
        super().__init__(parent, bg=COLORS['light_bg'])
        self.machine_count = machine_count
        self.job_count = job_count
        self.on_submit_callback = on_submit_callback
        self.task_entries = {}
        self.task_count_vars = {}

        self.create_widgets()

    def create_widgets(self):
        """Create task input table."""
        # Header section
        header_frame = tk.Frame(self, bg=COLORS['light_bg'], padx=PADDING['large'], pady=PADDING['medium'])
        header_frame.pack(fill=tk.X)

        title_label = tk.Label(
            header_frame,
            text="Task Configuration",
            font=FONTS['title'],
            bg=COLORS['light_bg'],
            fg=COLORS['primary_dark']
        )
        title_label.pack(anchor="w")

        info_label = tk.Label(
            header_frame,
            text=f"Machines: {self.machine_count} • Jobs: {self.job_count} • Maximum Total Tasks: {MAX_TOTAL_TASKS}",
            font=FONTS['small'],
            bg=COLORS['light_bg'],
            fg=COLORS['text_light']
        )
        info_label.pack(anchor="w", pady=(5, 0))

        # Create scrollable frame for tasks
        canvas_container = tk.Frame(self, bg=COLORS['light_bg'], padx=PADDING['medium'])
        canvas_container.pack(fill=tk.BOTH, expand=True, pady=PADDING['small'])

        canvas = tk.Canvas(canvas_container, bg=COLORS['light_bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['light_bg'], padx=PADDING['medium'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_reqwidth())
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create task input rows
        for job_idx in range(self.job_count):
            self.create_job_section(scrollable_frame, job_idx)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Buttons frame
        button_frame = tk.Frame(self, bg=COLORS['light_bg'], padx=PADDING['large'], pady=PADDING['medium'])
        button_frame.pack(fill=tk.X)

        submit_button = tk.Button(
            button_frame,
            text="Run Algorithms →",
            command=self.on_submit,
            bg=COLORS['success'],
            fg="white",
            font=FONTS['subheader'],
            padx=25,
            pady=10,
            cursor="hand2"
        )
        submit_button.pack(side=tk.LEFT, padx=(0, 10))

        reset_button = tk.Button(
            button_frame,
            text="Reset All",
            command=self.reset_values,
            bg=COLORS['text_light'],
            fg="white",
            font=FONTS['body'],
            padx=20,
            pady=8,
            cursor="hand2"
        )
        reset_button.pack(side=tk.LEFT)

    def create_job_section(self, parent, job_idx):
        """Create input section for a single job."""
        # Job card
        job_card = tk.Frame(
            parent,
            bg='white',
            relief='solid',
            borderwidth=1,
            padx=PADDING['medium'],
            pady=PADDING['medium']
        )
        job_card.pack(fill=tk.X, pady=PADDING['small'])

        # Job header
        job_header = tk.Frame(job_card, bg='white')
        job_header.pack(fill=tk.X, pady=(0, PADDING['medium']))

        job_title = tk.Label(
            job_header,
            text=f"Job {job_idx + 1}",
            font=FONTS['header'],
            bg='white',
            fg=COLORS['primary']
        )
        job_title.pack(side=tk.LEFT)

        # Task count controls
        task_count_frame = tk.Frame(job_header, bg='white')
        task_count_frame.pack(side=tk.RIGHT)

        task_label = tk.Label(
            task_count_frame,
            text="Tasks:",
            font=FONTS['body'],
            bg='white'
        )
        task_label.pack(side=tk.LEFT, padx=(0, 5))

        task_count_var = tk.IntVar(value=2)
        self.task_count_vars[job_idx] = task_count_var
        task_spinbox = tk.Spinbox(
            task_count_frame,
            from_=1,
            to=MAX_TASKS_PER_JOB,
            textvariable=task_count_var,
            width=4,
            font=FONTS['body'],
            justify='center'
        )
        task_spinbox.pack(side=tk.LEFT)

        # Tasks table
        tasks_container = tk.Frame(job_card, bg='white')
        tasks_container.pack(fill=tk.X)

        # Table headers
        header_frame = tk.Frame(tasks_container, bg=COLORS['primary'])
        header_frame.pack(fill=tk.X, pady=(0, 2))

        headers = ["Task", "Execution Time (ms)"]
        widths = [100, 150]
        for col, (header, width) in enumerate(zip(headers, widths)):
            header_label = tk.Label(
                header_frame,
                text=header,
                font=FONTS['subheader'],
                bg=COLORS['primary'],
                fg='white',
                padx=10,
                pady=8,
                width=width // 8  # Approximate character width
            )
            header_label.grid(row=0, column=col, sticky="ew", padx=(2 if col == 0 else 0, 2))
            header_frame.grid_columnconfigure(col, weight=1)

        # Store all widgets for this job
        self.task_entries[job_idx] = {'entries': [], 'labels': [], 'container': tasks_container}
        self.update_task_entries(tasks_container, job_idx, task_count_var, initial=True)

        # Bind spinbox to update tasks
        def on_task_count_change(*args):
            try:
                self.update_task_entries(tasks_container, job_idx, task_count_var)
            except tk.TclError:
                pass

        task_count_var.trace("w", on_task_count_change)

    def update_task_entries(self, tasks_container, job_idx, task_count_var, initial=False):
        """Update task entry fields based on task count."""
        try:
            new_task_count = task_count_var.get()
        except tk.TclError:
            return

        # Clear existing entries and labels if not initial
        if not initial and job_idx in self.task_entries:
            for entry in self.task_entries[job_idx]['entries']:
                entry.destroy()
            for label in self.task_entries[job_idx]['labels']:
                label.destroy()
            self.task_entries[job_idx]['entries'] = []
            self.task_entries[job_idx]['labels'] = []

        # Create entry fields container (skip header row)
        entries_frame = tk.Frame(tasks_container, bg='white')
        entries_frame.pack(fill=tk.X)

        # Create new entry fields
        for task_idx in range(new_task_count):
            # Task number label
            task_num_label = tk.Label(
                entries_frame,
                text=f"Task {task_idx + 1}",
                font=FONTS['body'],
                bg='white',
                padx=10,
                pady=8,
                relief='solid',
                borderwidth=1,
                width=12
            )
            task_num_label.grid(row=task_idx, column=0, sticky="ew", padx=(2, 1), pady=1)

            # Execution time entry
            time_entry = tk.Entry(
                entries_frame,
                width=15,
                font=FONTS['body'],
                justify='center',
                relief='solid',
                borderwidth=1
            )
            time_entry.insert(0, "100")
            time_entry.grid(row=task_idx, column=1, sticky="ew", padx=(1, 2), pady=1)

            entries_frame.grid_columnconfigure(0, weight=1)
            entries_frame.grid_columnconfigure(1, weight=1)

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

            if len(tasks) > MAX_TASKS_PER_JOB:
                messagebox.showerror(
                    "Input Limit Exceeded",
                    f"Job {job_idx + 1} has {len(tasks)} tasks, which exceeds the limit of {MAX_TASKS_PER_JOB} tasks per job."
                )
                return None

            total_tasks += len(tasks)
            jobs_data.append({"job_id": job_idx + 1, "tasks": tasks})

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
            self.task_count_vars[job_idx].set(2)
            if job_idx in self.task_entries:
                for entry in self.task_entries[job_idx]['entries']:
                    entry.delete(0, tk.END)
                    entry.insert(0, "100")


# """
# Input frames for the Job Schedule Application GUI.
# Handles user input for machine count, job count, and task details.
# """
#
# import tkinter as tk
# from tkinter import ttk, messagebox
# from .constants import MAX_MACHINES, MAX_JOBS, MAX_TOTAL_TASKS, MAX_TASKS_PER_JOB
#
#
# class BasicInputFrame(tk.Frame):
#     """Frame for inputting machine count and job count."""
#
#     def __init__(self, parent, on_submit_callback=None):
#         super().__init__(parent)
#         self.on_submit_callback = on_submit_callback
#         self.machine_count_var = tk.IntVar(value=1)
#         self.job_count_var = tk.IntVar(value=1)
#
#         self.create_widgets()
#
#     def create_widgets(self):
#         """Create and layout widgets for basic inputs."""
#         # Center the grid within the frame
#         self.grid_rowconfigure(0, weight=1)
#         self.grid_rowconfigure(4, weight=1)
#         self.grid_columnconfigure(0, weight=1)
#         self.grid_columnconfigure(3, weight=1)
#
#         # Title
#         title_label = tk.Label(
#             self,
#             text="Job Scheduling Configuration",
#             font=("Arial", 14, "bold")
#         )
#         title_label.grid(row=1, column=1, columnspan=2, pady=10)
#
#         # Machine Count
#         machine_label = tk.Label(self, text="Number of Machines:", font=("Arial", 11))
#         machine_label.grid(row=2, column=1, sticky="e", padx=10, pady=5)
#
#         machine_spinbox = tk.Spinbox(
#             self,
#             from_=1,
#             to=MAX_MACHINES,
#             textvariable=self.machine_count_var,
#             width=10,
#             font=("Arial", 11)
#         )
#         machine_spinbox.grid(row=2, column=2, sticky="w", padx=5, pady=5)
#
#         machine_limit_label = tk.Label(
#             self,
#             text=f"(Max: {MAX_MACHINES})",
#             font=("Arial", 9),
#             fg="gray"
#         )
#         machine_limit_label.grid(row=2, column=3, sticky="w", padx=5, pady=5)
#
#         # Job Count
#         job_label = tk.Label(self, text="Number of Jobs:", font=("Arial", 11))
#         job_label.grid(row=3, column=1, sticky="e", padx=10, pady=5)
#
#         job_spinbox = tk.Spinbox(
#             self,
#             from_=1,
#             to=MAX_JOBS,
#             textvariable=self.job_count_var,
#             width=10,
#             font=("Arial", 11)
#         )
#         job_spinbox.grid(row=3, column=2, sticky="w", padx=5, pady=5)
#
#         job_limit_label = tk.Label(
#             self,
#             text=f"(Max: {MAX_JOBS})",
#             font=("Arial", 9),
#             fg="gray"
#         )
#         job_limit_label.grid(row=3, column=3, sticky="w", padx=5, pady=5)
#
#         # Submit Button
#         submit_button = tk.Button(
#             self,
#             text="Configure Jobs",
#             command=self.on_submit,
#             bg="#4CAF50",
#             fg="white",
#             font=("Arial", 11, "bold"),
#             padx=10,
#             pady=5
#         )
#         submit_button.grid(row=4, column=1, columnspan=2, pady=15)
#
#     def on_submit(self):
#         """Handle submission of basic inputs."""
#         machine_count = self.machine_count_var.get()
#         job_count = self.job_count_var.get()
#
#         if machine_count < 1:
#             messagebox.showerror("Invalid Input", "Number of machines must be at least 1")
#             return
#
#         if machine_count > MAX_MACHINES:
#             messagebox.showerror("Invalid Input", f"Number of machines cannot exceed {MAX_MACHINES}")
#             return
#
#         if job_count < 1:
#             messagebox.showerror("Invalid Input", "Number of jobs must be at least 1")
#             return
#
#         if job_count > MAX_JOBS:
#             messagebox.showerror("Invalid Input", f"Number of jobs cannot exceed {MAX_JOBS}")
#             return
#
#         if self.on_submit_callback:
#             self.on_submit_callback(machine_count, job_count)
#
#     def get_values(self):
#         """Get current values."""
#         return self.machine_count_var.get(), self.job_count_var.get()
#
#
# class TaskInputFrame(tk.Frame):
#     """Frame for inputting task details in a table format."""
#
#     def __init__(self, parent, machine_count, job_count, on_submit_callback=None):
#         super().__init__(parent)
#         self.machine_count = machine_count
#         self.job_count = job_count
#         self.on_submit_callback = on_submit_callback
#         self.task_entries = {}  # Dictionary to store entry widgets
#         self.task_count_vars = {}  # Dictionary to store task count spinbox variables
#
#         self.create_widgets()
#
#     def create_widgets(self):
#         """Create task input table."""
#         # Title
#         title_label = tk.Label(
#             self,
#             text=f"Task Configuration ({self.job_count} Jobs)",
#             font=("Arial", 14, "bold")
#         )
#         title_label.pack(pady=10)
#
#         info_label = tk.Label(
#             self,
#             text=f"Machines: {self.machine_count} | Jobs: {self.job_count} | Max Total Tasks: {MAX_TOTAL_TASKS}",
#             font=("Arial", 10),
#             fg="gray"
#         )
#         info_label.pack(pady=5)
#
#         # Create scrollable frame for tasks
#         canvas_frame = tk.Frame(self)
#         canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
#
#         canvas = tk.Canvas(canvas_frame, height=400)
#         scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
#         scrollable_frame = tk.Frame(canvas)
#
#         scrollable_frame.bind(
#             "<Configure>",
#             lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
#         )
#
#         canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
#         canvas.configure(yscrollcommand=scrollbar.set)
#
#         # Create task input rows
#         for job_idx in range(self.job_count):
#             self.create_job_section(scrollable_frame, job_idx)
#
#         canvas.pack(side="left", fill="both", expand=True)
#         scrollbar.pack(side="right", fill="y")
#
#         # Buttons frame
#         button_frame = tk.Frame(self)
#         button_frame.pack(fill=tk.X, padx=15, pady=15)
#
#         submit_button = tk.Button(
#             button_frame,
#             text="Submit All Tasks",
#             command=self.on_submit,
#             bg="#2196F3",
#             fg="white",
#             font=("Arial", 11, "bold"),
#             padx=15,
#             pady=8
#         )
#         submit_button.pack(side="left", padx=5)
#
#         reset_button = tk.Button(
#             button_frame,
#             text="Reset",
#             command=self.reset_values,
#             bg="#f44336",
#             fg="white",
#             font=("Arial", 11, "bold"),
#             padx=15,
#             pady=8
#         )
#         reset_button.pack(side="left", padx=5)
#
#     def create_job_section(self, parent, job_idx):
#         """Create input section for a single job."""
#         # Job header
#         job_header = tk.Label(
#             parent,
#             text=f"Job {job_idx + 1}",
#             font=("Arial", 11, "bold"),
#             bg="#E8F5E9",
#             padx=10,
#             pady=5
#         )
#         job_header.grid(row=job_idx * 3, column=0, columnspan=3, sticky="ew", pady=(10, 5))
#
#         # Task count spinbox
#         task_label = tk.Label(parent, text="Number of Tasks:", font=("Arial", 10))
#         task_label.grid(row=job_idx * 3 + 1, column=0, sticky="w", padx=20, pady=5)
#
#         task_count_var = tk.IntVar(value=1)
#         self.task_count_vars[job_idx] = task_count_var  # Store for later reset
#         task_spinbox = tk.Spinbox(
#             parent,
#             from_=1,
#             to=MAX_TASKS_PER_JOB,
#             textvariable=task_count_var,
#             width=5,
#             font=("Arial", 10)
#         )
#         task_spinbox.grid(row=job_idx * 3 + 1, column=1, sticky="w", padx=10, pady=5)
#
#         task_limit_label = tk.Label(
#             parent,
#             text=f"(Max: {MAX_TASKS_PER_JOB})",
#             font=("Arial", 9),
#             fg="gray"
#         )
#         task_limit_label.grid(row=job_idx * 3 + 1, column=2, sticky="w", padx=5, pady=5)
#
#         # Create tasks table for this job
#         tasks_frame = tk.Frame(parent)
#         tasks_frame.grid(row=job_idx * 3 + 2, column=0, columnspan=3, sticky="ew", padx=20, pady=5)
#
#         # Table headers
#         headers = ["Task #", "Execution Time (ms)"]
#         for col, header in enumerate(headers):
#             header_label = tk.Label(
#                 tasks_frame,
#                 text=header,
#                 font=("Arial", 9, "bold"),
#                 bg="#BDBDBD",
#                 padx=10,
#                 pady=5,
#                 relief="solid",
#                 borderwidth=1
#             )
#             header_label.grid(row=0, column=col, sticky="ew", padx=2, pady=2)
#
#         # Store all widgets for this job (labels and entries)
#         self.task_entries[job_idx] = {'entries': [], 'labels': [], 'frame': tasks_frame}
#         self.update_task_entries(tasks_frame, job_idx, task_count_var, initial=True)
#
#         # Bind spinbox to update tasks
#         def on_task_count_change(*args):
#             try:
#                 self.update_task_entries(tasks_frame, job_idx, task_count_var)
#             except tk.TclError:
#                 # Ignore errors when spinbox is being edited
#                 pass
#
#         task_count_var.trace("w", on_task_count_change)
#
#     def update_task_entries(self, tasks_frame, job_idx, task_count_var, initial=False):
#         """Update task entry fields based on task count."""
#         try:
#             new_task_count = task_count_var.get()
#         except tk.TclError:
#             # Handle case where spinbox value is invalid/empty
#             return
#
#         # Clear existing entries and labels if not initial
#         if not initial and job_idx in self.task_entries:
#             # Destroy all entry widgets
#             for entry in self.task_entries[job_idx]['entries']:
#                 entry.destroy()
#             # Destroy all label widgets
#             for label in self.task_entries[job_idx]['labels']:
#                 label.destroy()
#             # Reset the lists
#             self.task_entries[job_idx]['entries'] = []
#             self.task_entries[job_idx]['labels'] = []
#
#         # Create new entry fields
#         for task_idx in range(new_task_count):
#             # Task number label
#             task_num_label = tk.Label(
#                 tasks_frame,
#                 text=f"Task {task_idx + 1}",
#                 font=("Arial", 9),
#                 padx=10,
#                 pady=5,
#                 relief="solid",
#                 borderwidth=1
#             )
#             task_num_label.grid(row=task_idx + 1, column=0, sticky="ew", padx=2, pady=2)
#
#             # Execution time entry
#             time_entry = tk.Entry(
#                 tasks_frame,
#                 width=15,
#                 font=("Arial", 9)
#             )
#             time_entry.insert(0, "0")
#             time_entry.grid(row=task_idx + 1, column=1, sticky="ew", padx=2, pady=2)
#
#             self.task_entries[job_idx]['entries'].append(time_entry)
#             self.task_entries[job_idx]['labels'].append(task_num_label)
#
#     def get_all_tasks(self):
#         """Retrieve all task data from the table."""
#         jobs_data = []
#         total_tasks = 0
#
#         for job_idx in range(self.job_count):
#             tasks = []
#             for task_idx, entry in enumerate(self.task_entries[job_idx]['entries']):
#                 try:
#                     exec_time = int(entry.get())
#                     if exec_time <= 0:
#                         raise ValueError("Execution time must be greater than 0")
#                     tasks.append(exec_time)
#                 except ValueError as e:
#                     messagebox.showerror(
#                         "Invalid Input",
#                         f"Job {job_idx + 1}, Task {task_idx + 1}: Please enter a valid execution time (must be > 0)"
#                     )
#                     return None
#
#             # Check per-job task limit
#             if len(tasks) > MAX_TASKS_PER_JOB:
#                 messagebox.showerror(
#                     "Input Limit Exceeded",
#                     f"Job {job_idx + 1} has {len(tasks)} tasks, which exceeds the limit of {MAX_TASKS_PER_JOB} tasks per job."
#                 )
#                 return None
#
#             total_tasks += len(tasks)
#             jobs_data.append({"job_id": job_idx + 1, "tasks": tasks})
#
#         # Check total tasks limit
#         if total_tasks > MAX_TOTAL_TASKS:
#             messagebox.showerror(
#                 "Input Limit Exceeded",
#                 f"Total number of tasks ({total_tasks}) cannot exceed {MAX_TOTAL_TASKS}.\n\n"
#                 f"Please reduce the number of tasks across your jobs."
#             )
#             return None
#
#         return jobs_data
#
#     def on_submit(self):
#         """Handle submission of all tasks."""
#         jobs_data = self.get_all_tasks()
#         if jobs_data and self.on_submit_callback:
#             self.on_submit_callback(self.machine_count, self.job_count, jobs_data)
#
#     def reset_values(self):
#         """Reset all entries and task counts to default values."""
#         for job_idx in self.task_count_vars:
#             # Reset task count spinbox to 1
#             self.task_count_vars[job_idx].set(1)
#
#             # Also reset all entry values to 0
#             if job_idx in self.task_entries:
#                 for entry in self.task_entries[job_idx]['entries']:
#                     entry.delete(0, tk.END)
#                     entry.insert(0, "0")
