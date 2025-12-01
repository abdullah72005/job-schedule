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
        self.is_resetting = False

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

        # Bind mouse wheel scroll to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _on_mousewheel_linux(event):
            if event.num == 5:
                canvas.yview_scroll(3, "units")
            elif event.num == 4:
                canvas.yview_scroll(-3, "units")
        
        # Windows and macOS
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        # Linux
        canvas.bind_all("<Button-4>", _on_mousewheel_linux)
        canvas.bind_all("<Button-5>", _on_mousewheel_linux)

        # Create task input rows
        for job_idx in range(self.job_count):
            self.create_job_section(scrollable_frame, job_idx)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Buttons frame
        button_frame = tk.Frame(self, bg=COLORS['light_bg'], padx=PADDING['large'], pady=PADDING['medium'])
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)

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

        task_count_var = tk.IntVar(value=1)
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
        self.task_entries[job_idx] = {'entries': [], 'labels': [], 'container': tasks_container, 'entries_frame': None}
        self.update_task_entries(tasks_container, job_idx, task_count_var, initial=True)

        # Bind spinbox to update tasks
        def on_task_count_change(*args):
            if not self.is_resetting:
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

        current_count = len(self.task_entries[job_idx]['entries'])
        
        # Get or create the entries frame
        if initial or 'entries_frame' not in self.task_entries[job_idx]:
            # Create entry fields container
            entries_frame = tk.Frame(tasks_container, bg='white')
            entries_frame.pack(fill=tk.X)
            self.task_entries[job_idx]['entries_frame'] = entries_frame
        else:
            entries_frame = self.task_entries[job_idx]['entries_frame']

        # If task count decreased, remove extra widgets
        if new_task_count < current_count:
            for task_idx in range(new_task_count, current_count):
                self.task_entries[job_idx]['entries'][task_idx].destroy()
                self.task_entries[job_idx]['labels'][task_idx].destroy()
            self.task_entries[job_idx]['entries'] = self.task_entries[job_idx]['entries'][:new_task_count]
            self.task_entries[job_idx]['labels'] = self.task_entries[job_idx]['labels'][:new_task_count]
            return

        # If task count increased, add new widgets
        for task_idx in range(current_count, new_task_count):
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
            time_entry.insert(0, "1")
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
        self.is_resetting = True
        try:
            for job_idx in self.task_count_vars:
                # Reset task count to 1
                self.task_count_vars[job_idx].set(1)
                if job_idx in self.task_entries:
                    # Explicitly update the entries to reflect the change
                    tasks_container = self.task_entries[job_idx]['container']
                    self.update_task_entries(tasks_container, job_idx, self.task_count_vars[job_idx])
        finally:
            self.is_resetting = False


