"""
Algorithm selection and execution pages for the Job Schedule GUI.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from .constants import COLORS, FONTS, PADDING


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

        self.create_widgets()

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

        # Gantt Chart Section (75% of width)
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

        # Placeholder for Gantt chart
        self.gantt_canvas.create_text(
            300, 200,
            text="Gantt Chart Visualization\n(Algorithm implementation required)",
            font=FONTS['body'],
            fill=COLORS['text_light'],
            justify='center'
        )

        # Statistics Section (25% of width - smaller sidebar)
        stats_frame = tk.Frame(
            content_frame,
            bg='white',
            relief='solid',
            borderwidth=1
        )
        stats_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(PADDING['small'], 0))
        stats_frame.configure(width=300)  # Fixed width for sidebar

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
            width=30  # Limit width to prevent taking too much space
        )
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.stats_text.yview)

        # Populate with placeholder stats
        self._display_placeholder_stats()

    def _display_placeholder_stats(self):
        """Display placeholder statistics."""
        stats_content = f"""ALGORITHM: {self.algorithm.upper()}
{'=' * 35}

PROBLEM CONFIGURATION
• Machines: {self.machine_count}
• Jobs: {self.job_count}
• Total Tasks: {sum(len(job['tasks']) for job in self.jobs_data)}

PERFORMANCE METRICS
• Makespan: [To be calculated]
• Total Idle Time: [To be calculated]
• Resource Utilization: [To be calculated]%
• Execution Time: [To be calculated] ms

ALGORITHM STATISTICS
• Generation: [To be calculated]
• Convergence: [To be calculated]
• Best Fitness: [To be calculated]
• Average Fitness: [To be calculated]

SCHEDULE DETAILS
• Status: Ready for implementation
• Optimization Level: [To be calculated]
"""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_content)
        self.stats_text.config(state=tk.DISABLED)

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
            ("Best Fitness Score", "Pending", "Pending", "TBD"),
            ("Average Fitness", "Pending", "Pending", "TBD"),
            ("Convergence Generation", "Pending", "Pending", "TBD"),
            ("Solution Quality", "Pending", "Pending", "TBD"),
            ("Memory Usage (MB)", "Pending", "Pending", "TBD"),
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
#
# """
# Algorithm selection and execution pages for the Job Schedule GUI.
# """
#
# import tkinter as tk
# from tkinter import ttk, messagebox
#
#
# class AlgorithmSelectionPage(tk.Frame):
#     """Page for selecting and running algorithms."""
#
#     def __init__(self, parent, machine_count, job_count, jobs_data, on_back_callback=None, on_run_callback=None):
#         super().__init__(parent)
#         self.machine_count = machine_count
#         self.job_count = job_count
#         self.jobs_data = jobs_data
#         self.on_back_callback = on_back_callback
#         self.on_run_callback = on_run_callback
#         self.selected_algorithm = tk.StringVar(value="backtracking")
#
#         self.create_widgets()
#
#     def create_widgets(self):
#         """Create the algorithm selection interface."""
#         # Header
#         header_label = tk.Label(
#             self,
#             text="Algorithm Selection",
#             font=("Arial", 16, "bold")
#         )
#         header_label.pack(pady=15)
#
#         # Problem summary
#         summary_frame = tk.LabelFrame(self, text="Problem Summary", font=("Arial", 11, "bold"), padx=10, pady=10)
#         summary_frame.pack(fill=tk.X, padx=15, pady=10)
#
#         summary_text = f"Machines: {self.machine_count} | Jobs: {self.job_count} | Total Tasks: {sum(len(job['tasks']) for job in self.jobs_data)}"
#         summary_label = tk.Label(summary_frame, text=summary_text, font=("Arial", 10), fg="gray")
#         summary_label.pack(anchor="w")
#
#         # Algorithm selection frame
#         algo_frame = tk.LabelFrame(self, text="Select Algorithm", font=("Arial", 12, "bold"), padx=15, pady=15)
#         algo_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
#
#         # Backtracking option
#         backtrack_radio = tk.Radiobutton(
#             algo_frame,
#             text="Backtracking Search Algorithm",
#             variable=self.selected_algorithm,
#             value="backtracking",
#             font=("Arial", 11),
#             padx=10,
#             pady=8
#         )
#         backtrack_radio.pack(anchor="w", fill=tk.X)
#
#         backtrack_desc = tk.Label(
#             algo_frame,
#             text="A systematic search algorithm that explores the solution space by backtracking when constraints are violated.",
#             font=("Arial", 9),
#             fg="gray",
#             wraplength=400,
#             justify="left"
#         )
#         backtrack_desc.pack(anchor="w", padx=30, pady=(0, 15))
#
#         # Cultural option
#         cultural_radio = tk.Radiobutton(
#             algo_frame,
#             text="Cultural Algorithm",
#             variable=self.selected_algorithm,
#             value="cultural",
#             font=("Arial", 11),
#             padx=10,
#             pady=8
#         )
#         cultural_radio.pack(anchor="w", fill=tk.X)
#
#         cultural_desc = tk.Label(
#             algo_frame,
#             text="An evolutionary algorithm that uses cultural beliefs and norms to guide the search process.",
#             font=("Arial", 9),
#             fg="gray",
#             wraplength=400,
#             justify="left"
#         )
#         cultural_desc.pack(anchor="w", padx=30, pady=(0, 15))
#
#         # Button frame
#         button_frame = tk.Frame(self)
#         button_frame.pack(fill=tk.X, padx=15, pady=20)
#
#         run_button = tk.Button(
#             button_frame,
#             text="Run Algorithm",
#             command=self.on_run,
#             bg="#4CAF50",
#             fg="white",
#             font=("Arial", 11, "bold"),
#             padx=20,
#             pady=10,
#             width=15
#         )
#         run_button.pack(side=tk.LEFT, padx=5)
#
#         compare_button = tk.Button(
#             button_frame,
#             text="Compare Both",
#             command=self.on_compare,
#             bg="#FF9800",
#             fg="white",
#             font=("Arial", 11, "bold"),
#             padx=20,
#             pady=10,
#             width=15
#         )
#         compare_button.pack(side=tk.LEFT, padx=5)
#
#         back_button = tk.Button(
#             button_frame,
#             text="Back",
#             command=self.on_back,
#             bg="#9E9E9E",
#             fg="white",
#             font=("Arial", 11, "bold"),
#             padx=20,
#             pady=10,
#             width=15
#         )
#         back_button.pack(side=tk.LEFT, padx=5)
#
#     def on_run(self):
#         """Handle run algorithm button."""
#         algorithm = self.selected_algorithm.get()
#         if self.on_run_callback:
#             self.on_run_callback(algorithm, self.machine_count, self.job_count, self.jobs_data)
#
#     def on_compare(self):
#         """Handle compare both button."""
#         if self.on_run_callback:
#             self.on_run_callback("compare", self.machine_count, self.job_count, self.jobs_data)
#
#     def on_back(self):
#         """Handle back button."""
#         if self.on_back_callback:
#             self.on_back_callback()
#
#
# class AlgorithmResultsPage(tk.Frame):
#     """Page displaying algorithm results with Gantt chart and statistics."""
#
#     def __init__(self, parent, algorithm, machine_count, job_count, jobs_data, on_back_callback=None):
#         super().__init__(parent)
#         self.algorithm = algorithm
#         self.machine_count = machine_count
#         self.job_count = job_count
#         self.jobs_data = jobs_data
#         self.on_back_callback = on_back_callback
#
#         self.create_widgets()
#
#     def create_widgets(self):
#         """Create the results display interface."""
#         # Header
#         header_frame = tk.Frame(self)
#         header_frame.pack(fill=tk.X, padx=15, pady=10)
#
#         title_label = tk.Label(
#             header_frame,
#             text=f"Results - {self.algorithm.title()} Algorithm",
#             font=("Arial", 16, "bold")
#         )
#         title_label.pack(side=tk.LEFT)
#
#         back_button = tk.Button(
#             header_frame,
#             text="← Back",
#             command=self.on_back,
#             bg="#9E9E9E",
#             fg="white",
#             font=("Arial", 10, "bold"),
#             padx=10,
#             pady=5
#         )
#         back_button.pack(side=tk.RIGHT)
#
#         # Main content split: Gantt chart on left, stats on right
#         content_frame = tk.Frame(self)
#         content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
#
#         # Gantt Chart Section (70% of space)
#         gantt_frame = tk.LabelFrame(
#             content_frame,
#             text="Gantt Chart",
#             font=("Arial", 12, "bold"),
#             padx=10,
#             pady=10
#         )
#         gantt_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
#         gantt_frame.pack_propagate(False)
#
#         # Placeholder for Gantt chart
#         self.gantt_canvas = tk.Canvas(
#             gantt_frame,
#             bg="#f0f0f0",
#             height=500,
#             relief=tk.SUNKEN,
#             borderwidth=1
#         )
#         self.gantt_canvas.pack(fill=tk.BOTH, expand=True)
#
#         # Gantt chart placeholder text
#         self.gantt_canvas.create_text(
#             250, 250,
#             text="Gantt Chart will be displayed here",
#             font=("Arial", 12),
#             fill="gray"
#         )
#
#         # Statistics Section (30% of space)
#         stats_frame = tk.LabelFrame(
#             content_frame,
#             text="Evolution Statistics",
#             font=("Arial", 11, "bold"),
#             padx=8,
#             pady=8
#         )
#         stats_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
#         stats_frame.pack_propagate(False)
#         stats_frame.configure(width=350, height=500)
#
#         # Create scrollable text widget for stats
#         stats_text_frame = tk.Frame(stats_frame)
#         stats_text_frame.pack(fill=tk.BOTH, expand=True)
#
#         scrollbar = tk.Scrollbar(stats_text_frame)
#         scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
#
#         self.stats_text = tk.Text(
#             stats_text_frame,
#             wrap=tk.WORD,
#             yscrollcommand=scrollbar.set,
#             font=("Courier", 10),
#             bg="#f9f9f9",
#             padx=10,
#             pady=10
#         )
#         self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
#         scrollbar.config(command=self.stats_text.yview)
#
#         # Populate with placeholder stats
#         self._display_placeholder_stats()
#
#     def _display_placeholder_stats(self):
#         """Display placeholder statistics."""
#         stats_content = f"""ALGORITHM: {self.algorithm.upper()}
# {'=' * 45}
#
# Problem Configuration:
#   - Machines: {self.machine_count}
#   - Jobs: {self.job_count}
#   - Total Tasks: {sum(len(job['tasks']) for job in self.jobs_data)}
#
# Algorithm Results:
#   - Makespan: [To be calculated]
#   - Total Idle Time: [To be calculated]
#   - Resource Utilization: [To be calculated]%
#
# Evolution Statistics:
#   - Generation: [To be calculated]
#   - Convergence: [To be calculated]
#   - Best Fitness: [To be calculated]
#   - Average Fitness: [To be calculated]
#
# Schedule Details:
#   - Execution Status: Ready for implementation
#   - Optimization Level: [To be calculated]
#   - Time Complexity: [To be calculated]
# """
#         self.stats_text.config(state=tk.NORMAL)
#         self.stats_text.delete(1.0, tk.END)
#         self.stats_text.insert(tk.END, stats_content)
#         self.stats_text.config(state=tk.DISABLED)
#
#     def on_back(self):
#         """Handle back button."""
#         if self.on_back_callback:
#             self.on_back_callback()
#
#
# class AlgorithmComparisonPage(tk.Frame):
#     """Page displaying comparison between Backtracking and Cultural algorithms."""
#
#     def __init__(self, parent, machine_count, job_count, jobs_data, on_back_callback=None):
#         super().__init__(parent)
#         self.machine_count = machine_count
#         self.job_count = job_count
#         self.jobs_data = jobs_data
#         self.on_back_callback = on_back_callback
#
#         self.create_widgets()
#
#     def create_widgets(self):
#         """Create the comparison interface."""
#         # Header
#         header_frame = tk.Frame(self)
#         header_frame.pack(fill=tk.X, padx=15, pady=10)
#
#         title_label = tk.Label(
#             header_frame,
#             text="Algorithm Comparison",
#             font=("Arial", 16, "bold")
#         )
#         title_label.pack(side=tk.LEFT)
#
#         back_button = tk.Button(
#             header_frame,
#             text="← Back",
#             command=self.on_back,
#             bg="#9E9E9E",
#             fg="white",
#             font=("Arial", 10, "bold"),
#             padx=10,
#             pady=5
#         )
#         back_button.pack(side=tk.RIGHT)
#
#         # Problem summary
#         summary_frame = tk.LabelFrame(self, text="Problem Summary", font=("Arial", 11, "bold"), padx=10, pady=10)
#         summary_frame.pack(fill=tk.X, padx=15, pady=10)
#
#         summary_text = f"Machines: {self.machine_count} | Jobs: {self.job_count} | Total Tasks: {sum(len(job['tasks']) for job in self.jobs_data)}"
#         summary_label = tk.Label(summary_frame, text=summary_text, font=("Arial", 10), fg="gray")
#         summary_label.pack(anchor="w")
#
#         # Comparison table
#         comparison_frame = tk.LabelFrame(
#             self,
#             text="Performance Metrics",
#             font=("Arial", 12, "bold"),
#             padx=15,
#             pady=15
#         )
#         comparison_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
#
#         # Create treeview for comparison
#         columns = ("Metric", "Backtracking", "Cultural", "Winner")
#         self.comparison_tree = ttk.Treeview(
#             comparison_frame,
#             columns=columns,
#             height=15,
#             show="headings"
#         )
#
#         # Define column headings and widths
#         self.comparison_tree.heading("Metric", text="Metric")
#         self.comparison_tree.column("Metric", width=200)
#
#         self.comparison_tree.heading("Backtracking", text="Backtracking")
#         self.comparison_tree.column("Backtracking", width=150)
#
#         self.comparison_tree.heading("Cultural", text="Cultural")
#         self.comparison_tree.column("Cultural", width=150)
#
#         self.comparison_tree.heading("Winner", text="Winner")
#         self.comparison_tree.column("Winner", width=100)
#
#         # Add sample rows
#         metrics = [
#             ("Makespan (ms)", "[To be calculated]", "[To be calculated]", "[TBD]"),
#             ("Total Idle Time (ms)", "[To be calculated]", "[To be calculated]", "[TBD]"),
#             ("Resource Utilization (%)", "[To be calculated]", "[To be calculated]", "[TBD]"),
#             ("Execution Time (s)", "[To be calculated]", "[To be calculated]", "[TBD]"),
#             ("Best Fitness", "[To be calculated]", "[To be calculated]", "[TBD]"),
#             ("Average Fitness", "[To be calculated]", "[To be calculated]", "[TBD]"),
#             ("Convergence Generation", "[To be calculated]", "[To be calculated]", "[TBD]"),
#             ("Solution Stability", "[To be calculated]", "[To be calculated]", "[TBD]"),
#         ]
#
#         for metric in metrics:
#             self.comparison_tree.insert("", "end", values=metric)
#
#         # Add scrollbar
#         scrollbar = ttk.Scrollbar(comparison_frame, orient="vertical", command=self.comparison_tree.yview)
#         self.comparison_tree.configure(yscrollcommand=scrollbar.set)
#
#         self.comparison_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
#         scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
#
#         # Button frame for actions
#         button_frame = tk.Frame(self)
#         button_frame.pack(fill=tk.X, padx=15, pady=15)
#
#         run_backtrack_btn = tk.Button(
#             button_frame,
#             text="Run Backtracking",
#             bg="#2196F3",
#             fg="white",
#             font=("Arial", 10, "bold"),
#             padx=15,
#             pady=8
#         )
#         run_backtrack_btn.pack(side=tk.LEFT, padx=5)
#
#         run_cultural_btn = tk.Button(
#             button_frame,
#             text="Run Cultural",
#             bg="#FF5722",
#             fg="white",
#             font=("Arial", 10, "bold"),
#             padx=15,
#             pady=8
#         )
#         run_cultural_btn.pack(side=tk.LEFT, padx=5)
#
#     def on_back(self):
#         """Handle back button."""
#         if self.on_back_callback:
#             self.on_back_callback()
