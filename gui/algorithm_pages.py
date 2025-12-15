"""
Algorithm selection and execution pages for the Job Schedule GUI.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from .constants import COLORS, FONTS, PADDING
from src.cultural.cultural import cultural_algorithm, get_metrics as cultural_get_metrics
from src.backTracking.backTracking import backtracking_algorithm


class AlgorithmSelectionPage(tk.Frame):

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
        main_container = tk.Frame(self, bg=COLORS['light_bg'], padx=PADDING['xlarge'], pady=PADDING['xlarge'])
        main_container.pack(fill=tk.BOTH, expand=True)

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
            text=f"Problem Summary: {self.machine_count} Machines • {self.job_count} Jobs • {sum(len(job['tasks']) for job in self.jobs_data)} Total Tasks",
            font=FONTS['subheader'],
            bg='white',
            fg=COLORS['text_dark']
        )
        summary_label.pack(anchor="w")

        algo_container = tk.Frame(main_container, bg=COLORS['light_bg'])
        algo_container.pack(fill=tk.BOTH, expand=True, pady=(0, PADDING['large']))

        backtrack_card = tk.Frame(
            algo_container,
            bg='white',
            relief='solid',
            borderwidth=1,
            padx=PADDING['medium'],
            pady=PADDING['medium']
        )
        backtrack_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, PADDING['small']))

        cultural_card = tk.Frame(
            algo_container,
            bg='white',
            relief='solid',
            borderwidth=1,
            padx=PADDING['medium'],
            pady=PADDING['medium']
        )
        cultural_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(PADDING['small'], 0))

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
            text="A systematic search algorithm that explores all possible solutions by searching the domain space and abandoning partial candidates when they cannot possibly lead to a valid solution.",
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
        algorithm = self.selected_algorithm.get()
        if self.on_run_callback:
            self.on_run_callback(algorithm, self.machine_count, self.job_count, self.jobs_data)

    def on_compare(self):
        if self.on_run_callback:
            self.on_run_callback("compare", self.machine_count, self.job_count, self.jobs_data)

    def on_back(self):
        if self.on_back_callback:
            self.on_back_callback()


class AlgorithmResultsPage(tk.Frame):

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
        self.generation_data = []  

        self.create_widgets()
        self.run_algorithm()

    def create_widgets(self):
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

        if self.algorithm == "cultural":
            self._create_cultural_layout()
        else:
            self._create_backtracking_layout()

    def _create_backtracking_layout(self):
        content_frame = tk.Frame(self, bg=COLORS['light_bg'], padx=PADDING['large'], pady=PADDING['small'])
        content_frame.pack(fill=tk.BOTH, expand=True)

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
            height=500
        )
        self.gantt_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        stats_frame = tk.Frame(
            content_frame,
            bg='white',
            relief='solid',
            borderwidth=1
        )
        stats_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(PADDING['small'], 0))
        stats_frame.configure(width=450)  

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
            width=50 
        )
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.stats_text.yview)

        self._display_loading_stats()
        
        self.plot_canvas_frame = None
        self.fig = None
        self.canvas = None

    def _create_cultural_layout(self):
        content_frame = tk.Frame(self, bg=COLORS['light_bg'], padx=PADDING['large'], pady=PADDING['small'])
        content_frame.pack(fill=tk.BOTH, expand=True)

        stats_frame = tk.Frame(
            content_frame,
            bg='white',
            relief='solid',
            borderwidth=1
        )
        stats_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(PADDING['small'], 0))
        stats_frame.configure(width=450)

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
            width=50
        )
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.stats_text.yview)

        vis_frame = tk.Frame(
            content_frame,
            bg='white',
            relief='solid',
            borderwidth=1
        )
        vis_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, PADDING['small']))

        vis_header = tk.Frame(vis_frame, bg=COLORS['primary'], pady=8)
        vis_header.pack(fill=tk.X)

        vis_title = tk.Label(
            vis_header,
            text="Schedule Visualization",
            font=FONTS['subheader'],
            bg=COLORS['primary'],
            fg='white'
        )
        vis_title.pack(side=tk.LEFT, padx=10)

        toggle_frame = tk.Frame(vis_header, bg=COLORS['primary'])
        toggle_frame.pack(side=tk.RIGHT, padx=10)

        self.chart_button = tk.Button(
            toggle_frame,
            text="Gantt Chart",
            command=lambda: self._toggle_view("chart"),
            bg=COLORS['primary_dark'],
            fg="white",
            font=('Arial', 9),
            padx=10,
            pady=3,
            cursor="hand2",
            relief="flat",
            bd=0
        )
        self.chart_button.pack(side=tk.LEFT, padx=3)

        self.plot_button = tk.Button(
            toggle_frame,
            text="Evolution Plot",
            command=lambda: self._toggle_view("plot"),
            bg=COLORS['text_light'],
            fg="white",
            font=('Arial', 9),
            padx=10,
            pady=3,
            cursor="hand2",
            relief="flat",
            bd=0
        )
        self.plot_button.pack(side=tk.LEFT, padx=3)

        self.view_container = tk.Frame(vis_frame, bg='white')
        self.view_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.gantt_frame_alt = tk.Frame(self.view_container, bg='white')

        self.gantt_canvas_alt = tk.Canvas(
            self.gantt_frame_alt,
            bg="#f8f9fa",
            height=350
        )
        self.gantt_canvas_alt.pack(fill=tk.BOTH, expand=True)

        self.plot_frame_alt = tk.Frame(self.view_container, bg='white')

        self.plot_canvas_frame = tk.Frame(self.plot_frame_alt)
        self.plot_canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.fig = None
        self.canvas = None

        self._display_loading_stats()
        
        self._toggle_view("chart")

    def run_algorithm(self):
        if self.is_running:
            return
        
        self.is_running = True
        thread = threading.Thread(target=self._run_algorithm_thread, daemon=True)
        thread.start()

    def _run_algorithm_thread(self):
        try:
            problem_data = self._prepare_problem_data()
            
            if self.algorithm == "cultural":
                start_time = time.time()
                timeline, fitness, fitness_history = cultural_algorithm(
                    problem_data, 
                    generation_callback=self._on_generation_update
                )
                exec_time = time.time() - start_time
                self.metrics = cultural_get_metrics(timeline, exec_time)
            elif self.algorithm == "backtracking":
                timeline, self.metrics, step_history = backtracking_algorithm(
                    problem_data,
                    generation_callback=self._on_generation_update
                )
                fitness_history = step_history
            else:
                messagebox.showerror("Error", f"Unknown algorithm: {self.algorithm}")
                return
            
            self.timeline = timeline
            
            self.after(0, self._display_results)
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Algorithm Error", str(e)))
            print(f"Algorithm error: {e}")
            import traceback
            traceback.print_exc()

    def _on_generation_update(self, step, info):
        if isinstance(info, dict):
            fitness = info.get('best_makespan', 'N/A')
        else:
            fitness = info
        
        self.generation_data.append((step, fitness))
        self.after(0, self._update_generation_display)

    def _prepare_problem_data(self):
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
        self.stats_text.config(state=tk.NORMAL)
        
        algo_label = "GENERATIONS" if self.algorithm == "cultural" else "SEARCH PROGRESS"
        step_name = "Node" if self.algorithm == "backtracking" else "Generation"
        best_name = "Best Makespan" if self.algorithm == "backtracking" else "Best Fitness"

        
        stats_content = f"""ALGORITHM: {self.algorithm.upper()}
{'=' * 40}

{algo_label}
{'=' * 40}
"""
        for step, fitness in self.generation_data[-10:]:  
            if isinstance(fitness, float):
                stats_content += f"{step_name} {step:5d}: {best_name} = {fitness:.2f}\n"
            else:
                stats_content += f"{step_name} {step:5d}: {best_name} = {fitness}\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_content)
        self.stats_text.see(tk.END)  
        self.stats_text.config(state=tk.DISABLED)

    def _display_results(self):
        if not self.metrics:
            return
        
        try:
            if not self.winfo_exists() or not self.stats_text.winfo_exists():
                return
        except tk.TclError:
            return
        
        algo_label = "GENERATIONS" if self.algorithm == "cultural" else "SEARCH PROGRESS"
        step_name = "Node" if self.algorithm == "backtracking" else "Generation"
        best_name = "Best Makespan" if self.algorithm == "backtracking" else "Best Fitness"

        
        stats_content = f"""ALGORITHM: {self.algorithm.upper()}
{'=' * 40}

{algo_label}
{'=' * 40}
"""
        for step, fitness in self.generation_data:
            if isinstance(fitness, float):
                stats_content += f"{step_name} {step:5d}: {best_name} = {fitness:.2f}\n"
            else:
                stats_content += f"{step_name} {step:5d}: {best_name} = {fitness}\n"
        
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
        
        try:
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, stats_content)
            self.stats_text.see(tk.END)  # Scroll to end
            self.stats_text.config(state=tk.DISABLED)
        except tk.TclError:
            return
        
        self._draw_gantt_chart()
        
        self._draw_fitness_evolution_plot()

    def _toggle_view(self, view_type):
        if view_type == "chart":
            self.gantt_frame_alt.pack(fill=tk.BOTH, expand=True)
            self.plot_frame_alt.pack_forget()
            self.chart_button.config(bg=COLORS['primary_dark'])
            self.plot_button.config(bg=COLORS['text_light'])
        else:
            self.gantt_frame_alt.pack_forget()
            self.plot_frame_alt.pack(fill=tk.BOTH, expand=True)
            self.chart_button.config(bg=COLORS['text_light'])
            self.plot_button.config(bg=COLORS['primary_dark'])

    def _draw_gantt_chart(self):
        if not self.timeline:
            return
        
        canvas = self.gantt_canvas_alt if self.algorithm == "cultural" else self.gantt_canvas
        
        try:
            if not canvas.winfo_exists():
                return
        except tk.TclError:
            return
        
        try:
            canvas.delete("all")
        except tk.TclError:
            return
        
        makespan = max(max(
            list(task_dict.values())[0][0] + list(task_dict.values())[0][1]
            for task_dict in tasks
        ) for tasks in self.timeline.values() if tasks)
        
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 600
            canvas_height = 300
        
        left_margin = 80
        top_margin = 40
        right_margin = 20
        bottom_margin = 40
        
        chart_width = canvas_width - left_margin - right_margin
        chart_height = canvas_height - top_margin - bottom_margin
        
        canvas.create_text(
            canvas_width // 2, 20,
            text="Gantt Chart",
            font=FONTS['subheader']
        )
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2']
        
        machines = sorted(self.timeline.keys())
        machine_height = chart_height / len(machines) if machines else 0
        
        for machine_idx, machine in enumerate(machines):
            y_pos = top_margin + machine_idx * machine_height
            
            canvas.create_text(
                left_margin - 10, y_pos + machine_height / 2,
                text=f"M{machine}",
                font=FONTS['body'],
                anchor='e'
            )
            
            for task_dict in self.timeline[machine]:
                for (job_id, task_id), (start_time, duration) in task_dict.items():
                    x_start = left_margin + (start_time / makespan) * chart_width
                    x_width = (duration / makespan) * chart_width
                    
                    color = colors[(job_id - 1) % len(colors)]
                    
                    canvas.create_rectangle(
                        x_start, y_pos,
                        x_start + x_width, y_pos + machine_height - 2,
                        fill=color, outline='black', width=1
                    )
                    
                    if x_width > 30:
                        canvas.create_text(
                            x_start + x_width / 2, y_pos + machine_height / 2,
                            text=f"J{job_id}T{task_id}",
                            font=FONTS['small'],
                            fill='white'
                        )
        
        canvas.create_line(
            left_margin, top_margin + chart_height,
            left_margin + chart_width, top_margin + chart_height,
            width=2
        )
        
        time_intervals = 5
        for i in range(time_intervals + 1):
            time_val = (makespan / time_intervals) * i
            x_pos = left_margin + (i / time_intervals) * chart_width
            canvas.create_line(x_pos, top_margin + chart_height, x_pos, top_margin + chart_height + 5)
            canvas.create_text(
                x_pos, top_margin + chart_height + 15,
                text=f"{int(time_val)}",
                font=FONTS['small']
            )

    def _draw_fitness_evolution_plot(self):
        """Draw fitness evolution plot using matplotlib (only for cultural algorithm)."""
        if self.algorithm != "cultural" or not self.generation_data:
            return
        
        try:
            if not self.plot_canvas_frame or not self.plot_canvas_frame.winfo_exists():
                return
        except tk.TclError:
            return
        
        try:
            generations = [step for step, _ in self.generation_data]
            fitness_values = [fit if isinstance(fit, (int, float)) else float(str(fit).split('=')[-1].strip()) 
                            for _, fit in self.generation_data]
            
            self.fig = Figure(figsize=(12, 5), dpi=100)
            ax = self.fig.add_subplot(111)
            
            ax.plot(generations, fitness_values, 'b-o', linewidth=2, markersize=5)
            ax.set_xlabel('Generation', fontsize=12, fontweight='bold')
            ax.set_ylabel('Best Fitness (ms)', fontsize=12, fontweight='bold')
            ax.set_title('Cultural Algorithm Evolution Over Generations', fontsize=13, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.set_facecolor('#f8f9fa')
            
            self.fig.patch.set_facecolor('white')
            
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
            
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_canvas_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            print(f"Error drawing fitness evolution plot: {e}")
            import traceback
            traceback.print_exc()

    def on_back(self):
        if self.on_back_callback:
            self.on_back_callback()


class AlgorithmComparisonPage(tk.Frame):

    def __init__(self, parent, machine_count, job_count, jobs_data, on_back_callback=None):
        super().__init__(parent, bg=COLORS['light_bg'])
        self.machine_count = machine_count
        self.job_count = job_count
        self.jobs_data = jobs_data
        self.on_back_callback = on_back_callback
        
        self.backtrack_metrics = None
        self.cultural_metrics = None
        self.backtrack_timeline = None
        self.cultural_timeline = None
        self.is_running = False
        self.backtrack_thread = None
        self.cultural_thread = None

        self.create_widgets()
        self.run_comparison()

    def create_widgets(self):
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

        columns = ("Metric", "Backtracking", "Cultural", "Winner")
        self.comparison_tree = ttk.Treeview(
            table_card,
            columns=columns,
            height=12,
            show="headings",
            style="Custom.Treeview"
        )

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

        self.comparison_tree.heading("Metric", text="Performance Metric")
        self.comparison_tree.column("Metric", width=200, anchor="w")

        self.comparison_tree.heading("Backtracking", text="Backtracking")
        self.comparison_tree.column("Backtracking", width=150, anchor="center")

        self.comparison_tree.heading("Cultural", text="Cultural")
        self.comparison_tree.column("Cultural", width=150, anchor="center")

        self.comparison_tree.heading("Winner", text="Winner")
        self.comparison_tree.column("Winner", width=100, anchor="center")

        self.metric_rows = {}
        metrics = [
            ("Makespan (ms)", "Running...", "Running...", "..."),
            ("Total Idle Time (ms)", "Running...", "Running...", "..."),
            ("Resource Utilization (%)", "Running...", "Running...", "..."),
            ("Execution Time (s)", "Running...", "Running...", "..."),
        ]

        for i, metric in enumerate(metrics):
            row_id = self.comparison_tree.insert("", "end", values=metric)
            self.metric_rows[metric[0]] = row_id

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.comparison_tree.yview)
        self.comparison_tree.configure(yscrollcommand=scrollbar.set)

        self.comparison_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        gantt_label = tk.Label(
            self,
            text="Schedule Visualization - Gantt Charts",
            font=FONTS['subheader'],
            bg=COLORS['light_bg'],
            fg=COLORS['primary_dark']
        )
        gantt_label.pack(anchor="w", padx=PADDING['large'], pady=(PADDING['medium'], PADDING['small']))

        gantt_container = tk.Frame(self, bg=COLORS['light_bg'])
        gantt_container.pack(fill=tk.BOTH, expand=True, padx=PADDING['large'], pady=(0, PADDING['medium']))

        backtrack_frame = tk.Frame(gantt_container, bg='white', relief='solid', borderwidth=1)
        backtrack_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, PADDING['small']))

        backtrack_title = tk.Label(
            backtrack_frame,
            text="Backtracking Schedule",
            font=FONTS['body'],
            bg=COLORS['primary'],
            fg='white'
        )
        backtrack_title.pack(fill=tk.X, pady=5)

        self.backtrack_gantt = tk.Canvas(
            backtrack_frame,
            bg='white',
            height=200,
            relief='flat'
        )
        self.backtrack_gantt.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self._setup_canvas_scrollwheel(self.backtrack_gantt, backtrack_frame)

        cultural_frame = tk.Frame(gantt_container, bg='white', relief='solid', borderwidth=1)
        cultural_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(PADDING['small'], 0))

        cultural_title = tk.Label(
            cultural_frame,
            text="Cultural Schedule",
            font=FONTS['body'],
            bg=COLORS['secondary'],
            fg='white'
        )
        cultural_title.pack(fill=tk.X, pady=5)

        self.cultural_gantt = tk.Canvas(
            cultural_frame,
            bg='white',
            height=200,
            relief='flat'
        )
        self.cultural_gantt.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self._setup_canvas_scrollwheel(self.cultural_gantt, cultural_frame)

    def run_comparison(self):
        """Run both algorithms in parallel."""
        self.is_running = True
        
        problem_data = self._prepare_problem_data()
        
        self.backtrack_thread = threading.Thread(
            target=self._run_backtracking,
            args=(problem_data,),
            daemon=True
        )
        self.backtrack_thread.start()
        
        self.cultural_thread = threading.Thread(
            target=self._run_cultural,
            args=(problem_data,),
            daemon=True
        )
        self.cultural_thread.start()
        
        self.check_completion()

    def _prepare_problem_data(self):
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

    def _run_backtracking(self, problem_data):
        try:
            start_time = time.time()
            timeline, metrics, _ = backtracking_algorithm(problem_data)
            exec_time = time.time() - start_time
            self.backtrack_timeline = timeline
            self.backtrack_metrics = metrics
            self.after(0, self._draw_backtrack_gantt)
        except Exception as e:
            print(f"Backtracking error: {e}")
            import traceback
            traceback.print_exc()
            self.backtrack_metrics = None

    def _run_cultural(self, problem_data):
        try:
            start_time = time.time()
            timeline, _, _ = cultural_algorithm(problem_data)
            exec_time = time.time() - start_time
            self.cultural_timeline = timeline
            self.cultural_metrics = cultural_get_metrics(timeline, exec_time)
            self.after(0, self._draw_cultural_gantt)
        except Exception as e:
            print(f"Cultural error: {e}")
            import traceback
            traceback.print_exc()
            self.cultural_metrics = None

    def check_completion(self):
        if self.backtrack_metrics is not None:
            self._update_backtrack_display()
        
        if self.cultural_metrics is not None:
            self._update_cultural_display()
        
        if self.backtrack_metrics is not None and self.cultural_metrics is not None:
            self._update_winners()
            self.is_running = False
        elif self.is_running:
            self.after(500, self.check_completion)

    def _update_backtrack_display(self):
        if not self.backtrack_metrics:
            return
        
        metrics_map = {
            "Makespan (ms)": self.backtrack_metrics['makespan'],
            "Total Idle Time (ms)": self.backtrack_metrics['idle_time'],
            "Resource Utilization (%)": f"{self.backtrack_metrics['utilization']:.2f}%",
            "Execution Time (s)": self.backtrack_metrics['execTime'],
        }
        
        for metric_name, metric_value in metrics_map.items():
            if metric_name in self.metric_rows:
                row_id = self.metric_rows[metric_name]
                current_values = self.comparison_tree.item(row_id)['values']
                self.comparison_tree.item(
                    row_id,
                    values=(current_values[0], metric_value, current_values[2], current_values[3])
                )

    def _update_cultural_display(self):
        if not self.cultural_metrics:
            return
        
        metrics_map = {
            "Makespan (ms)": self.cultural_metrics['makespan'],
            "Total Idle Time (ms)": self.cultural_metrics['idle_time'],
            "Resource Utilization (%)": f"{self.cultural_metrics['utilization']:.2f}%",
            "Execution Time (s)": self.cultural_metrics['execTime'],
        }
        
        for metric_name, metric_value in metrics_map.items():
            if metric_name in self.metric_rows:
                row_id = self.metric_rows[metric_name]
                current_values = self.comparison_tree.item(row_id)['values']
                # Update cultural column (index 2), keep others as is
                self.comparison_tree.item(
                    row_id,
                    values=(current_values[0], current_values[1], metric_value, current_values[3])
                )

    def _update_winners(self):
        if not self.backtrack_metrics or not self.cultural_metrics:
            return
        
        backtrack_makespan = float(self.backtrack_metrics['makespan'].split()[0])
        cultural_makespan = float(self.cultural_metrics['makespan'].split()[0])
        
        backtrack_idle = float(self.backtrack_metrics['idle_time'].split()[0])
        cultural_idle = float(self.cultural_metrics['idle_time'].split()[0])
        
        backtrack_util = float(self.backtrack_metrics['utilization'])
        cultural_util = float(self.cultural_metrics['utilization'])
        
        backtrack_time = float(self.backtrack_metrics['execTime'].split()[0])
        cultural_time = float(self.cultural_metrics['execTime'].split()[0])
        
        winners = {
            "Makespan (ms)": "Backtracking" if backtrack_makespan < cultural_makespan else "Cultural",
            "Total Idle Time (ms)": "Backtracking" if backtrack_idle < cultural_idle else "Cultural",
            "Resource Utilization (%)": "Cultural" if cultural_util > backtrack_util else "Backtracking",
            "Execution Time (s)": "Cultural" if cultural_time < backtrack_time else "Backtracking",
        }
        
        for metric_name, winner in winners.items():
            if metric_name in self.metric_rows:
                row_id = self.metric_rows[metric_name]
                current_values = self.comparison_tree.item(row_id)['values']
                self.comparison_tree.item(
                    row_id,
                    values=(current_values[0], current_values[1], current_values[2], winner)
                )

    def _update_comparison_display(self):
        backtrack_makespan = float(self.backtrack_metrics['makespan'].split()[0])
        cultural_makespan = float(self.cultural_metrics['makespan'].split()[0])
        
        backtrack_idle = float(self.backtrack_metrics['idle_time'].split()[0])
        cultural_idle = float(self.cultural_metrics['idle_time'].split()[0])
        
        backtrack_util = float(self.backtrack_metrics['utilization'])
        cultural_util = float(self.cultural_metrics['utilization'])
        
        backtrack_time = float(self.backtrack_metrics['execTime'].split()[0])
        cultural_time = float(self.cultural_metrics['execTime'].split()[0])
        
        makespan_winner = "Backtracking" if backtrack_makespan < cultural_makespan else "Cultural"
        idle_winner = "Backtracking" if backtrack_idle < cultural_idle else "Cultural"
        util_winner = "Cultural" if cultural_util > backtrack_util else "Backtracking"
        time_winner = "Cultural" if cultural_time < backtrack_time else "Backtracking"
        
        metrics_data = [
            ("Makespan (ms)", self.backtrack_metrics['makespan'], self.cultural_metrics['makespan'], makespan_winner),
            ("Total Idle Time (ms)", self.backtrack_metrics['idle_time'], self.cultural_metrics['idle_time'], idle_winner),
            ("Resource Utilization (%)", f"{self.backtrack_metrics['utilization']:.2f}%", f"{self.cultural_metrics['utilization']:.2f}%", util_winner),
            ("Execution Time (s)", self.backtrack_metrics['execTime'], self.cultural_metrics['execTime'], time_winner),
        ]
        
        for metric_name, backtrack_val, cultural_val, winner in metrics_data:
            if metric_name in self.metric_rows:
                self.comparison_tree.item(
                    self.metric_rows[metric_name],
                    values=(metric_name, backtrack_val, cultural_val, winner)
                )

    def _draw_backtrack_gantt(self):
        if not self.backtrack_timeline:
            return
        
        self.backtrack_gantt.delete("all")
        self._draw_gantt_on_canvas(self.backtrack_gantt, self.backtrack_timeline, "Backtracking")

    def _draw_cultural_gantt(self):
        if not self.cultural_timeline:
            return
        
        self.cultural_gantt.delete("all")
        self._draw_gantt_on_canvas(self.cultural_gantt, self.cultural_timeline, "Cultural")

    def _draw_gantt_on_canvas(self, canvas, timeline, algorithm_name):
        if not timeline:
            return
        
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = 400
        if canvas_height <= 1:
            canvas_height = 200
        
        try:
            max_time = max(
                max(
                    list(task_dict.values())[0][0] + list(task_dict.values())[0][1]
                    for task_dict in tasks
                )
                for tasks in timeline.values() if tasks
            )
        except (ValueError, IndexError, KeyError):
            max_time = 100
        
        margin_left = 40
        margin_right = 20
        margin_top = 20
        margin_bottom = 20
        
        chart_width = canvas_width - margin_left - margin_right
        chart_height = canvas_height - margin_top - margin_bottom
        
        time_scale = chart_width / max(max_time, 1)
        
        num_machines = len(timeline)
        machine_height = chart_height / max(num_machines, 1)
        
        colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
            '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B88B', '#ABEBC6'
        ]
        
        for machine_idx, (machine, tasks) in enumerate(sorted(timeline.items())):
            y_pos = margin_top + machine_idx * machine_height
            
            canvas.create_text(
                margin_left - 10, y_pos + machine_height / 2,
                text=f"M{machine}", anchor="e", font=(FONTS['small'][0], 8),
                fill=COLORS['text_dark']
            )
            
            canvas.create_rectangle(
                margin_left, y_pos,
                canvas_width + margin_left, y_pos + machine_height - 2,
                fill='#F0F0F0', outline='#CCCCCC'
            )
            
            for task_dict in tasks:
                for (job_id, task_id), (start_time, duration) in task_dict.items():
                    x1 = margin_left + start_time * time_scale
                    x2 = x1 + duration * time_scale
                    y1 = y_pos + 2
                    y2 = y_pos + machine_height - 2
                    
                    color = colors[(job_id - 1) % len(colors)]
                    
                    canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=color, outline='#333333', width=1
                    )
                    
                    if x2 - x1 > 30:
                        canvas.create_text(
                            (x1 + x2) / 2, (y1 + y2) / 2,
                            text=f"J{job_id}", anchor="center",
                            font=(FONTS['small'][0], 7), fill='white'
                        )
        
        axis_y = margin_top + chart_height
        canvas.create_line(
            margin_left, axis_y,
            canvas_width + margin_left, axis_y,
            fill='#333333', width=2
        )
        
        num_ticks = 5
        for i in range(num_ticks + 1):
            x = margin_left + (i / num_ticks) * chart_width
            time_val = (i / num_ticks) * max_time
            canvas.create_line(x, axis_y, x, axis_y + 5, fill='#333333', width=1)
            canvas.create_text(
                x, axis_y + 15,
                text=f"{int(time_val)}", anchor="n",
                font=(FONTS['small'][0], 8), fill=COLORS['text_dark']
            )

    def _setup_canvas_scrollwheel(self, canvas, parent_frame):
        """Setup scrollwheel support for a canvas with vertical scrolling."""
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas.update_idletasks()
        
        def _on_mousewheel(event):
            try:
                scroll_amount = int(-1 * (event.delta / 120) * 3)
                canvas.yview_scroll(scroll_amount, "units")
            except tk.TclError:
                pass
        
        def _on_mousewheel_linux(event):
            try:
                if event.num == 5:  # Scroll down
                    canvas.yview_scroll(3, "units")
                elif event.num == 4:  # Scroll up
                    canvas.yview_scroll(-3, "units")
            except tk.TclError:
                pass
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        canvas.bind("<Button-4>", _on_mousewheel_linux)
        canvas.bind("<Button-5>", _on_mousewheel_linux)

    def on_back(self):
        """Handle back button."""
        if self.on_back_callback:
            self.on_back_callback()