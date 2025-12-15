"""
Data display module for showing collected job scheduling data.
"""

import tkinter as tk
from tkinter import ttk


class DataDisplay(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(
            self,
            text="Schedule Data Preview",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)

        text_frame = tk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_display = tk.Text(
            text_frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("Courier", 10),
            bg="#f5f5f5",
            padx=10,
            pady=10
        )
        self.text_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_display.yview)

        self.text_display.insert(tk.END, "Waiting for input data...\n")
        self.text_display.config(state=tk.DISABLED)

    def update_display(self, machine_count, jobs_data):
        self.text_display.config(state=tk.NORMAL)
        self.text_display.delete(1.0, tk.END)

        output = f"SCHEDULE CONFIGURATION\n"
        output += f"{'=' * 50}\n"
        output += f"Number of Machines: {machine_count}\n"
        output += f"Number of Jobs: {len(jobs_data)}\n\n"

        output += f"JOB DETAILS\n"
        output += f"{'=' * 50}\n"

        for job in jobs_data:
            job_id = job['job_id']
            tasks = job['tasks']
            total_time = sum(tasks)

            output += f"\nJob {job_id}:\n"
            output += f"  Number of Tasks: {len(tasks)}\n"
            output += f"  Task Execution Times (ms):\n"

            for task_idx, exec_time in enumerate(tasks, 1):
                output += f"    Task {task_idx}: {exec_time} ms\n"

            output += f"  Total Job Time: {total_time} ms\n"
            output += f"  {'-' * 48}\n"

        self.text_display.insert(tk.END, output)
        self.text_display.config(state=tk.DISABLED)

        print("\n" + "=" * 60)
        print(output)
        print("=" * 60 + "\n")
