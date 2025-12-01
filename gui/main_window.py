"""
Main window for the Job Schedule GUI application.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from .data_display import DataDisplay
from .input_form import InputForm
from .algorithm_pages import AlgorithmSelectionPage, AlgorithmResultsPage, AlgorithmComparisonPage
from .constants import COLORS, FONTS


class MainWindow:
    """Main application window combining input and display areas."""

    def __init__(self, root):
        self.root = root
        self.root.title("Job Schedule Manager - Advanced Scheduling System")
        self.root.geometry("1300x800")
        self.root.minsize(1200, 700)

        # Set window icon and theme
        self.root.configure(bg=COLORS['light_bg'])
        self.setup_styles()

        self.machine_count = None
        self.jobs_data = []
        self.current_page = None

        # Create main container
        self.main_frame = tk.Frame(root, bg=COLORS['light_bg'])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Initialize pages
        self.show_input_page()

    def setup_styles(self):
        """Configure custom styles for the application."""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure button styles
        style.configure('Primary.TButton',
                        background=COLORS['primary'],
                        foreground='white',
                        font=FONTS['body'],
                        borderwidth=0,
                        focuscolor='none')

        style.configure('Secondary.TButton',
                        background=COLORS['secondary'],
                        foreground='white',
                        font=FONTS['body'],
                        borderwidth=0,
                        focuscolor='none')

    def show_input_page(self):
        """Display the input form page."""
        self.clear_main_frame()

        # Create input page with modern layout
        input_form = InputForm(self.main_frame, self.on_data_update)
        input_form.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.current_page = "input"

    def on_data_update(self, machine_count, job_count, jobs_data):
        """Callback when data is updated from the input form."""
        self.machine_count = machine_count
        self.job_count = job_count
        self.jobs_data = jobs_data
        self.show_algorithm_selection_page()

    def show_algorithm_selection_page(self):
        """Display the algorithm selection page."""
        self.clear_main_frame()

        algo_page = AlgorithmSelectionPage(
            self.main_frame,
            self.machine_count,
            self.job_count,
            self.jobs_data,
            on_back_callback=self.show_input_page,
            on_run_callback=self.on_algorithm_selected
        )
        algo_page.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.current_page = "algorithm_selection"

    def on_algorithm_selected(self, algorithm, machine_count, job_count, jobs_data):
        """Callback when algorithm is selected."""
        if algorithm == "compare":
            self.show_comparison_page()
        else:
            self.show_results_page(algorithm)

    def show_results_page(self, algorithm):
        """Display results page for a selected algorithm."""
        self.clear_main_frame()

        results_page = AlgorithmResultsPage(
            self.main_frame,
            algorithm,
            self.machine_count,
            len(self.jobs_data),
            self.jobs_data,
            on_back_callback=self.show_algorithm_selection_page
        )
        results_page.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.current_page = "results"

    def show_comparison_page(self):
        """Display comparison page for both algorithms."""
        self.clear_main_frame()

        comparison_page = AlgorithmComparisonPage(
            self.main_frame,
            self.machine_count,
            len(self.jobs_data),
            self.jobs_data,
            on_back_callback=self.show_algorithm_selection_page
        )
        comparison_page.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.current_page = "comparison"

    def clear_main_frame(self):
        """Clear all widgets from the main frame."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()


def run_app():
    """Start the application."""
    root = tk.Tk()

    # Center the window on screen
    window_width = 1300
    window_height = 800
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()

