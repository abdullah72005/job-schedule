"""
Input form module combining basic inputs and task configuration.
"""

import tkinter as tk
from tkinter import ttk
from .input_frames import BasicInputFrame, TaskInputFrame


class InputForm(tk.Frame):
    """Combined form for basic inputs and task configuration."""

    def __init__(self, parent, on_submit_callback=None):
        super().__init__(parent)
        self.on_submit_callback = on_submit_callback
        self.machine_count = None
        self.job_count = None
        self.current_view = "basic"
        self.basic_frame = None
        self.task_frame = None

        self.create_widgets()

    def create_widgets(self):
        """Create the initial basic input frame."""
        # Create a centered container
        self.container_frame = tk.Frame(self)
        self.container_frame.pack(expand=True, fill=tk.BOTH)
        
        # Place container in the center
        self.container_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        self.basic_frame = BasicInputFrame(self.container_frame, on_submit_callback=self.on_basic_submit)
        self.basic_frame.pack(fill=tk.BOTH, expand=True)

    def on_basic_submit(self, machine_count, job_count):
        """Handle submission of basic inputs and switch to task input."""
        self.machine_count = machine_count
        self.job_count = job_count

        # Hide basic frame
        if self.basic_frame:
            self.basic_frame.pack_forget()

        # Show task frame
        self.task_frame = TaskInputFrame(
            self.container_frame,
            machine_count,
            job_count,
            on_submit_callback=self.on_task_submit
        )
        self.task_frame.pack(fill=tk.BOTH, expand=True)
        self.current_view = "tasks"

    def on_task_submit(self, machine_count, job_count, jobs_data):
        """Handle submission of task data."""
        if self.on_submit_callback:
            self.on_submit_callback(machine_count, job_count, jobs_data)
