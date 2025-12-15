"""
Input form module combining basic inputs and task configuration.
"""

import tkinter as tk
from tkinter import ttk
from .input_frames import BasicInputFrame, TaskInputFrame


class InputForm(tk.Frame):

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
        self.container_frame = tk.Frame(self)
        self.container_frame.pack(expand=True, fill=tk.BOTH)
        
        self.container_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        self.basic_frame = BasicInputFrame(self.container_frame, on_submit_callback=self.on_basic_submit)
        self.basic_frame.pack(fill=tk.BOTH, expand=True)

    def on_basic_submit(self, machine_count, job_count):
        self.machine_count = machine_count
        self.job_count = job_count

        if self.basic_frame:
            self.basic_frame.pack_forget()

        self.task_frame = TaskInputFrame(
            self.container_frame,
            machine_count,
            job_count,
            on_submit_callback=self.on_task_submit
        )
        self.task_frame.pack(fill=tk.BOTH, expand=True)
        self.current_view = "tasks"

    def on_task_submit(self, machine_count, job_count, jobs_data):
        if self.on_submit_callback:
            self.on_submit_callback(machine_count, job_count, jobs_data)
