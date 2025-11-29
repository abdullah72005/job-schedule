"""
Main window for the Job Schedule GUI application.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from .data_display import DataDisplay
from .input_form import InputForm
from .algorithm_pages import AlgorithmSelectionPage, AlgorithmResultsPage, AlgorithmComparisonPage


class MainWindow:
    """Main application window combining input and display areas."""

    def __init__(self, root):
        self.root = root
        self.root.title("Job Schedule Manager")
        self.root.geometry("1200x750")
        self.root.minsize(1200, 700)

        self.machine_count = None
        self.jobs_data = []
        self.current_page = None

        # Create main container
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Initialize pages
        self.show_input_page()

    def show_input_page(self):
        """Display the input form page."""
        # Clear previous content
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Create centered frame for input
        center_frame = tk.Frame(self.main_frame)
        center_frame.pack(fill=tk.BOTH, expand=True)

        # Initialize input form (centered)
        input_form = InputForm(center_frame, self.on_data_update)
        input_form.pack(fill=tk.BOTH, expand=True)

        self.current_page = "input"

    def on_data_update(self, machine_count, job_count, jobs_data):
        """Callback when data is updated from the input form."""
        self.machine_count = machine_count
        self.job_count = job_count
        self.jobs_data = jobs_data
        self.show_algorithm_selection_page()

    def show_algorithm_selection_page(self):
        """Display the algorithm selection page."""
        # Clear previous content
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        algo_page = AlgorithmSelectionPage(
            self.main_frame,
            self.machine_count,
            self.job_count,
            self.jobs_data,
            on_back_callback=self.show_input_page,
            on_run_callback=self.on_algorithm_selected
        )
        algo_page.pack(fill=tk.BOTH, expand=True)
        self.current_page = "algorithm_selection"

    def on_algorithm_selected(self, algorithm, machine_count, job_count, jobs_data):
        """Callback when algorithm is selected."""
        if algorithm == "compare":
            self.show_comparison_page()
        else:
            self.show_results_page(algorithm)

    def show_results_page(self, algorithm):
        """Display results page for a selected algorithm."""
        # Clear previous content
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        results_page = AlgorithmResultsPage(
            self.main_frame,
            algorithm,
            self.machine_count,
            len(self.jobs_data),
            self.jobs_data,
            on_back_callback=self.show_algorithm_selection_page
        )
        results_page.pack(fill=tk.BOTH, expand=True)
        self.current_page = "results"

    def show_comparison_page(self):
        """Display comparison page for both algorithms."""
        # Clear previous content
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        comparison_page = AlgorithmComparisonPage(
            self.main_frame,
            self.machine_count,
            len(self.jobs_data),
            self.jobs_data,
            on_back_callback=self.show_algorithm_selection_page
        )
        comparison_page.pack(fill=tk.BOTH, expand=True)
        self.current_page = "comparison"


def run_app():
    """Start the application."""
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()
