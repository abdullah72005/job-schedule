"""
Algorithm selection and execution pages for the Job Schedule GUI.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from .constants import COLORS, FONTS, PADDING
from src.cultural.cultural import cultural_algorithm, get_metrics


class AlgorithmSelectionPage(tk.Frame):
    """Page for selecting and running algorithms."""

    def __init__(self, parent, machine_count, job_count, jobs_data, on_back_callback=None, on_run_callback=None):
        super().__init__(parent, bg=COLORS['light_bg'])
        self.machine_count = machine_count
        self.job_count = job_count
        self.jobs_data = jobs_data
        self.on_back_callback = on_back_callback
        self.on_run_callback = on_run_callback
        self.selected_algorithm = tk.StringVar(value="backtracking")

        self.create_widgets()

    def create_widgets(self):
        """Create the algorithm selection interface."""
        # Main container
        main_container = tk.Frame(self, bg=COLORS['light_bg'], padx=PADDING['xlarge'], pady=PADDING['xlarge'])
        main_container.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = tk.Frame(main_container, bg=COLORS['light_bg'])
        header_frame.pack(fill=tk.X, pady=(0, PADDING['large']))

        header_label = tk.Label(
            header_frame,
            text="Algorithm Selection",
            font=FONTS['title'],
            bg=COLORS['light_bg'],
            fg=COLORS['primary_dark']
        )
        header_label.pack(anchor="w")

        subtitle_label = tk.Label(
            header_frame,
            text="Choose an algorithm to solve your scheduling problem",
            font=FONTS['small'],
            bg=COLORS['light_bg'],
            fg=COLORS['text_light']
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))

        # Problem summary card
        summary_card = tk.Frame(
            main_container,
            bg='white',
            relief='solid',
            borderwidth=1,
            padx=PADDING['medium'],
            pady=PADDING['medium']
        )
        summary_card.pack(fill=tk.X, pady=(0, PADDING['large']))

        summary_label = tk.Label(
            summary_card,
            text=f"📊 Problem Summary: {self.machine_count} Machines • {self.job_count} Jobs • {sum(len(job['tasks']) for job in self.jobs_data)} Total Tasks",
            font=FONTS['subheader'],
            bg='white',
            fg=COLORS['text_dark']
        )
        summary_label.pack(anchor="w")

        # Algorithm selection cards
        algo_container = tk.Frame(main_container, bg=COLORS['light_bg'])
        algo_container.pack(fill=tk.BOTH, expand=True, pady=(0, PADDING['large']))

        # Left column - Backtracking
        backtrack_card = tk.Frame(
            algo_container,
            bg='white',
            relief='solid',
            borderwidth=1,
            padx=PADDING['medium'],
            pady=PADDING['medium']
        )
        backtrack_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, PADDING['small']))

        # Right column - Cultural
        cultural_card = tk.Frame(
            algo_container,
            bg='white',
            relief='solid',
            borderwidth=1,
            padx=PADDING['medium'],
            pady=PADDING['medium']
        )
        cultural_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(PADDING['small'], 0))

        # Backtracking algorithm card content
        backtrack_header = tk.Frame(backtrack_card, bg='white')
        backtrack_header.pack(fill=tk.X, pady=(0, PADDING['medium']))

        backtrack_radio = tk.Radiobutton(
            backtrack_header,
            text="Backtracking Search",
            variable=self.selected_algorithm,
            value="backtracking",
            font=FONTS['header'],
            bg='white',
            fg=COLORS['text_dark'],
            selectcolor=COLORS['light_bg'],
            cursor="hand2"
        )
        backtrack_radio.pack(anchor="w")

        backtrack_desc = tk.Label(
            backtrack_card,
            text="A systematic search algorithm that explores all possible solutions by building candidates incrementally and abandoning partial candidates when they cannot possibly lead to a valid solution.",
            font=FONTS['body'],
            bg='white',
            fg=COLORS['text_light'],
            wraplength=300,
            justify='left'
        )
        backtrack_desc.pack(anchor="w", pady=(0, PADDING['medium']))

        backtrack_features = tk.Label(
            backtrack_card,
            text="• Guaranteed optimal solution\n• Complete search space exploration\n• Best for small problem sizes",
            font=FONTS['small'],
            bg='white',
            fg=COLORS['text_dark'],
            justify='left'
        )
        backtrack_features.pack(anchor="w")

        # Cultural algorithm card content
        cultural_header = tk.Frame(cultural_card, bg='white')
        cultural_header.pack(fill=tk.X, pady=(0, PADDING['medium']))

        cultural_radio = tk.Radiobutton(
            cultural_header,
            text="Cultural Algorithm",
            variable=self.selected_algorithm,
            value="cultural",
            font=FONTS['header'],
            bg='white',
            fg=COLORS['text_dark'],
            selectcolor=COLORS['light_bg'],
            cursor="hand2"
        )
        cultural_radio.pack(anchor="w")

        cultural_desc = tk.Label(
            cultural_card,
            text="An evolutionary algorithm inspired by cultural evolution processes. Uses a belief space to guide the population-based search toward promising regions.",
            font=FONTS['body'],
            bg='white',
            fg=COLORS['text_light'],
            wraplength=300,
            justify='left'
        )
        cultural_desc.pack(anchor="w", pady=(0, PADDING['medium']))

        cultural_features = tk.Label(
            cultural_card,
            text="• Heuristic approach\n• Faster convergence\n• Good for larger problems\n• Cultural knowledge sharing",
            font=FONTS['small'],
            bg='white',
            fg=COLORS['text_dark'],
            justify='left'
        )
        cultural_features.pack(anchor="w")

        # Button frame
        button_frame = tk.Frame(main_container, bg=COLORS['light_bg'])
        button_frame.pack(fill=tk.X, pady=PADDING['medium'])

        run_button = tk.Button(
            button_frame,
            text="Run Selected Algorithm →",
            command=self.on_run,
            bg=COLORS['primary'],
            fg="white",
            font=FONTS['subheader'],
            padx=25,
            pady=10,
            cursor="hand2"
        )
        run_button.pack(side=tk.LEFT, padx=(0, 10))

        compare_button = tk.Button(
            button_frame,
            text="Compare Both Algorithms",
            command=self.on_compare,
            bg=COLORS['secondary'],
            fg="white",
            font=FONTS['body'],
            padx=20,
            pady=8,
            cursor="hand2"
        )
        compare_button.pack(side=tk.LEFT, padx=(0, 10))

        back_button = tk.Button(
            button_frame,
            text="← Back to Input",
            command=self.on_back,
            bg=COLORS['text_light'],
            fg="white",
            font=FONTS['body'],
            padx=20,
            pady=8,
            cursor="hand2"
        )
        back_button.pack(side=tk.LEFT)

    def on_run(self):
        """Handle run algorithm button."""
        algorithm = self.selected_algorithm.get()
        if self.on_run_callback:
            self.on_run_callback(algorithm, self.machine_count, self.job_count, self.jobs_data)

    def on_compare(self):
        """Handle compare both button."""
        if self.on_run_callback:
            self.on_run_callback("compare", self.machine_count, self.job_count, self.jobs_data)

    def on_back(self):
        """Handle back button."""
        if self.on_back_callback:
            self.on_back_callback()


class AlgorithmResultsPage(tk.Frame):
    """Page displaying algorithm results with Gantt chart and statistics."""

    def __init__(self, parent, algorithm, machine_count, job_count, jobs_data, on_back_callback=None):
        super().__init__(parent, bg=COLORS['light_bg'])
        self.algorithm = algorithm
        self.machine_count = machine_count
        self.job_count = job_count
        self.jobs_data = jobs_data
        self.on_back_callback = on_back_callback
        self.timeline = None
        self.metrics = None
        self.is_running = False
        self.generation_data = []  # Store generation history for display

        self.create_widgets()
        self.run_algorithm()

    def create_widgets(self):
        """Create the results display interface."""
        # Header
        header_frame = tk.Frame(self, bg=COLORS['light_bg'], padx=PADDING['large'], pady=PADDING['medium'])
        header_frame.pack(fill=tk.X)

        title_label = tk.Label(
            header_frame,
            text=f"{self.algorithm.title()} Algorithm Results",
            font=FONTS['title'],
            bg=COLORS['light_bg'],
            fg=COLORS['primary_dark']
        )
        title_label.pack(side=tk.LEFT)

        back_button = tk.Button(
            header_frame,
            text="← Back to Selection",
            command=self.on_back,
            bg=COLORS['text_light'],
            fg="white",
            font=FONTS['body'],
            padx=15,
            pady=6,
            cursor="hand2"
        )
        back_button.pack(side=tk.RIGHT)

        # Main content - Gantt chart takes most space, stats on right as sidebar
        content_frame = tk.Frame(self, bg=COLORS['light_bg'], padx=PADDING['large'], pady=PADDING['small'])
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Gantt Chart Section (65% of width)
        gantt_frame = tk.Frame(
            content_frame,
            bg='white',
            relief='solid',
            borderwidth=1
        )
        gantt_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, PADDING['small']))

        gantt_header = tk.Frame(gantt_frame, bg=COLORS['primary'], pady=8)
        gantt_header.pack(fill=tk.X)

        gantt_title = tk.Label(
            gantt_header,
            text="Gantt Chart Visualization",
            font=FONTS['subheader'],
            bg=COLORS['primary'],
            fg='white'
        )
        gantt_title.pack()

        self.gantt_canvas = tk.Canvas(
            gantt_frame,
            bg="#f8f9fa",
            height=400
        )
        self.gantt_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Statistics Section (35% of width)
        stats_frame = tk.Frame(
            content_frame,
            bg='white',
            relief='solid',
            borderwidth=1
        )
        stats_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(PADDING['small'], 0))
        stats_frame.configure(width=450)  # Wider sidebar for 35%

        stats_header = tk.Frame(stats_frame, bg=COLORS['secondary'], pady=8)
        stats_header.pack(fill=tk.X)

        stats_title = tk.Label(
            stats_header,
            text="Performance Statistics",
            font=FONTS['subheader'],
            bg=COLORS['secondary'],
            fg='white'
        )
        stats_title.pack()

        # Create scrollable text widget for stats
        stats_content_frame = tk.Frame(stats_frame)
        stats_content_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        scrollbar = tk.Scrollbar(stats_content_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.stats_text = tk.Text(
            stats_content_frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=('Consolas', 9),
            bg="#f8f9fa",
            padx=8,
            pady=8,
            relief='flat',
            width=50  # Wider for 35% width section
        )
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.stats_text.yview)

        # Populate with loading stats
        self._display_loading_stats()

    def run_algorithm(self):
        """Run the algorithm in a background thread."""
        if self.is_running:
            return
        
        self.is_running = True
        thread = threading.Thread(target=self._run_algorithm_thread, daemon=True)
        thread.start()

    def _run_algorithm_thread(self):
        """Execute algorithm in background thread."""
        try:
            # Prepare data for the algorithm
            problem_data = self._prepare_problem_data()
            
            start_time = time.time()
            if self.algorithm == "cultural":
                timeline, fitness, fitness_history = cultural_algorithm(
                    problem_data, 
                    generation_callback=self._on_generation_update
                )
            else:
                # Placeholder for backtracking
                messagebox.showwarning("Not Implemented", "Backtracking algorithm not yet integrated")
                return
            
            exec_time = time.time() - start_time
            
            # Get metrics
            self.metrics = get_metrics(timeline, exec_time)
            self.timeline = timeline
            
            # Update UI in main thread
            self.after(0, self._display_results)
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Algorithm Error", str(e)))
            print(f"Algorithm error: {e}")
            import traceback
            traceback.print_exc()

    def _on_generation_update(self, generation, fitness):
        """Callback for generation updates from the algorithm."""
        self.generation_data.append((generation, fitness))
        # Update UI in main thread
        self.after(0, self._update_generation_display)

    def _prepare_problem_data(self):
        """Convert GUI data format to algorithm format."""
        problem_data = {
            'machines_count': self.machine_count,
            'total_jobs': self.job_count,
            'total_tasks': sum(len(job['tasks']) for job in self.jobs_data),
            'jobs': []
        }
        
        for job in self.jobs_data:
            job_data = {
                'job_id': job['job_id'],
                'tasks': []
            }
            for task_idx, exec_time in enumerate(job['tasks'], 1):
                job_data['tasks'].append({
                    'task_id': task_idx,
                    'execution_time': exec_time
                })
            problem_data['jobs'].append(job_data)
        
        return problem_data

    def _display_loading_stats(self):
        """Display loading message."""
        stats_content = f"""ALGORITHM: {self.algorithm.upper()}
{'=' * 40}

Status: Running algorithm...
Please wait...

GENERATION EVOLUTION
{'=' * 40}
"""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_content)
        self.stats_text.config(state=tk.DISABLED)

    def _update_generation_display(self):
        """Update generation display in real-time."""
        self.stats_text.config(state=tk.NORMAL)
        
        stats_content = f"""ALGORITHM: {self.algorithm.upper()}
{'=' * 40}

GENERATION EVOLUTION
{'=' * 40}
"""
        # Add generation data
        for gen, fitness in self.generation_data[-10:]:  # Show last 10 generations
            stats_content += f"Gen {gen:3d}: Fitness = {fitness:.2f}\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_content)
        self.stats_text.see(tk.END)  # Auto-scroll to bottom
        self.stats_text.config(state=tk.DISABLED)

    def _display_results(self):
        """Display actual results after algorithm execution."""
        if not self.metrics:
            return
        
        stats_content = f"""ALGORITHM: {self.algorithm.upper()}
{'=' * 40}

GENERATION EVOLUTION
{'=' * 40}
"""
        # Add all generations
        for gen, fitness in self.generation_data:
            stats_content += f"Gen {gen:3d}: Fitness = {fitness:.2f}\n"
        
        stats_content += f"""
{'=' * 40}
PROBLEM CONFIGURATION
{'=' * 40}
• Machines: {self.machine_count}
• Jobs: {self.job_count}
• Total Tasks: {sum(len(job['tasks']) for job in self.jobs_data)}

PERFORMANCE METRICS
{'=' * 40}
• Makespan: {self.metrics['makespan']}
• Total Idle Time: {self.metrics['idle_time']}
• Resource Utilization: {self.metrics['utilization']}%
• Execution Time: {self.metrics['execTime']}

{'=' * 40}
Status: Optimization Complete
"""
        
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_content)
        self.stats_text.see(tk.END)  # Scroll to end
        self.stats_text.config(state=tk.DISABLED)
        
        # Draw Gantt chart
        self._draw_gantt_chart()

    def _draw_gantt_chart(self):
        """Draw a simple Gantt chart representation."""
        if not self.timeline:
            return
        
        self.gantt_canvas.delete("all")
        
        # Get timeline dimensions
        makespan = max(max(
            list(task_dict.values())[0][0] + list(task_dict.values())[0][1]
            for task_dict in tasks
        ) for tasks in self.timeline.values() if tasks)
        
        # Canvas dimensions
        canvas_width = self.gantt_canvas.winfo_width()
        canvas_height = self.gantt_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 600
            canvas_height = 300
        
        # Margins
        left_margin = 80
        top_margin = 40
        right_margin = 20
        bottom_margin = 40
        
        chart_width = canvas_width - left_margin - right_margin
        chart_height = canvas_height - top_margin - bottom_margin
        
        # Draw title
        self.gantt_canvas.create_text(
            canvas_width // 2, 20,
            text="Gantt Chart",
            font=FONTS['subheader']
        )
        
        # Colors for different machines
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2']
        
        machines = sorted(self.timeline.keys())
        machine_height = chart_height / len(machines) if machines else 0
        
        # Draw machines and tasks
        for machine_idx, machine in enumerate(machines):
            y_pos = top_margin + machine_idx * machine_height
            
            # Draw machine label
            self.gantt_canvas.create_text(
                left_margin - 10, y_pos + machine_height / 2,
                text=f"M{machine}",
                font=FONTS['body'],
                anchor='e'
            )
            
            # Draw tasks
            for task_dict in self.timeline[machine]:
                for (job_id, task_id), (start_time, duration) in task_dict.items():
                    x_start = left_margin + (start_time / makespan) * chart_width
                    x_width = (duration / makespan) * chart_width
                    
                    color = colors[(job_id - 1) % len(colors)]
                    
                    self.gantt_canvas.create_rectangle(
                        x_start, y_pos,
                        x_start + x_width, y_pos + machine_height - 2,
                        fill=color, outline='black', width=1
                    )
                    
                    # Add label if space permits
                    if x_width > 30:
                        self.gantt_canvas.create_text(
                            x_start + x_width / 2, y_pos + machine_height / 2,
                            text=f"J{job_id}T{task_id}",
                            font=FONTS['small'],
                            fill='white'
                        )
        
        # Draw time axis
        self.gantt_canvas.create_line(
            left_margin, top_margin + chart_height,
            left_margin + chart_width, top_margin + chart_height,
            width=2
        )
        
        # Draw time labels
        time_intervals = 5
        for i in range(time_intervals + 1):
            time_val = (makespan / time_intervals) * i
            x_pos = left_margin + (i / time_intervals) * chart_width
            self.gantt_canvas.create_line(x_pos, top_margin + chart_height, x_pos, top_margin + chart_height + 5)
            self.gantt_canvas.create_text(
                x_pos, top_margin + chart_height + 15,
                text=f"{int(time_val)}",
                font=FONTS['small']
            )

    def on_back(self):
        """Handle back button."""
        if self.on_back_callback:
            self.on_back_callback()


class AlgorithmComparisonPage(tk.Frame):
    """Page displaying comparison between Backtracking and Cultural algorithms."""

    def __init__(self, parent, machine_count, job_count, jobs_data, on_back_callback=None):
        super().__init__(parent, bg=COLORS['light_bg'])
        self.machine_count = machine_count
        self.job_count = job_count
        self.jobs_data = jobs_data
        self.on_back_callback = on_back_callback

        self.create_widgets()

    def create_widgets(self):
        """Create the comparison interface."""
        # Header
        header_frame = tk.Frame(self, bg=COLORS['light_bg'], padx=PADDING['large'], pady=PADDING['medium'])
        header_frame.pack(fill=tk.X)

        title_label = tk.Label(
            header_frame,
            text="Algorithm Comparison Dashboard",
            font=FONTS['title'],
            bg=COLORS['light_bg'],
            fg=COLORS['primary_dark']
        )
        title_label.pack(side=tk.LEFT)

        back_button = tk.Button(
            header_frame,
            text="← Back to Selection",
            command=self.on_back,
            bg=COLORS['text_light'],
            fg="white",
            font=FONTS['body'],
            padx=15,
            pady=6,
            cursor="hand2"
        )
        back_button.pack(side=tk.RIGHT)

        # Problem summary
        summary_card = tk.Frame(
            self,
            bg='white',
            relief='solid',
            borderwidth=1,
            padx=PADDING['medium'],
            pady=PADDING['medium']
        )
        summary_card.pack(fill=tk.X, padx=PADDING['large'], pady=(0, PADDING['medium']))

        summary_label = tk.Label(
            summary_card,
            text=f"📊 Comparison Basis: {self.machine_count} Machines • {self.job_count} Jobs • {sum(len(job['tasks']) for job in self.jobs_data)} Total Tasks",
            font=FONTS['subheader'],
            bg='white',
            fg=COLORS['text_dark']
        )
        summary_label.pack(anchor="w")

        # Comparison table container
        table_container = tk.Frame(self, bg=COLORS['light_bg'], padx=PADDING['large'], pady=PADDING['small'])
        table_container.pack(fill=tk.BOTH, expand=True)

        table_card = tk.Frame(
            table_container,
            bg='white',
            relief='solid',
            borderwidth=1
        )
        table_card.pack(fill=tk.BOTH, expand=True)

        table_header = tk.Frame(table_card, bg=COLORS['primary'], pady=8)
        table_header.pack(fill=tk.X)

        table_title = tk.Label(
            table_header,
            text="Performance Metrics Comparison",
            font=FONTS['subheader'],
            bg=COLORS['primary'],
            fg='white'
        )
        table_title.pack()

        # Create treeview for comparison
        columns = ("Metric", "Backtracking", "Cultural", "Winner")
        self.comparison_tree = ttk.Treeview(
            table_card,
            columns=columns,
            height=12,
            show="headings",
            style="Custom.Treeview"
        )

        # Configure style for better appearance
        style = ttk.Style()
        style.configure("Custom.Treeview",
                       background="white",
                       fieldbackground="white",
                       foreground=COLORS['text_dark'],
                       rowheight=25)
        style.configure("Custom.Treeview.Heading",
                       background=COLORS['light_bg'],
                       foreground=COLORS['text_dark'],
                       font=('Arial', 10, 'bold'))

        # Define column headings and widths
        self.comparison_tree.heading("Metric", text="Performance Metric")
        self.comparison_tree.column("Metric", width=200, anchor="w")

        self.comparison_tree.heading("Backtracking", text="Backtracking")
        self.comparison_tree.column("Backtracking", width=150, anchor="center")

        self.comparison_tree.heading("Cultural", text="Cultural")
        self.comparison_tree.column("Cultural", width=150, anchor="center")

        self.comparison_tree.heading("Winner", text="Winner")
        self.comparison_tree.column("Winner", width=100, anchor="center")

        # Add sample rows with better formatting
        metrics = [
            ("Makespan (ms)", "Pending", "Pending", "TBD"),
            ("Total Idle Time (ms)", "Pending", "Pending", "TBD"),
            ("Resource Utilization (%)", "Pending", "Pending", "TBD"),
            ("Execution Time (s)", "Pending", "Pending", "TBD"),
        ]

        for metric in metrics:
            self.comparison_tree.insert("", "end", values=metric)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.comparison_tree.yview)
        self.comparison_tree.configure(yscrollcommand=scrollbar.set)

        self.comparison_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

    def on_back(self):
        """Handle back button."""
        if self.on_back_callback:
            self.on_back_callback()
