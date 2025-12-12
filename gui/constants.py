"""
Configuration constants for the Job Scheduling Application.
These values can be easily modified as requirements change.
"""

# Input limits
MAX_MACHINES = 10
MAX_JOBS = 30
MAX_TOTAL_TASKS = 200
MAX_TASKS_PER_JOB = 20

# Validation error messages
ERROR_MAX_MACHINES = f"Number of machines cannot exceed {MAX_MACHINES}"
ERROR_MAX_JOBS = f"Number of jobs cannot exceed {MAX_JOBS}"
ERROR_MAX_TOTAL_TASKS = f"Total number of tasks across all jobs cannot exceed {MAX_TOTAL_TASKS}"
ERROR_MAX_TASKS_PER_JOB = f"Number of tasks per job cannot exceed {MAX_TASKS_PER_JOB}"

# Color scheme
COLORS = {
    'primary': '#2E86AB',
    'primary_dark': '#1B5E7A',
    'secondary': '#A23B72',
    'success': '#4CAF50',
    'warning': '#FF9800',
    'danger': '#F44336',
    'light_bg': '#F8F9FA',
    'dark_bg': '#343A40',
    'border': '#DEE2E6',
    'text_light': '#6C757D',
    'text_dark': '#212529'
}

# Fonts
FONTS = {
    'title': ('Arial', 18, 'bold'),
    'header': ('Arial', 14, 'bold'),
    'subheader': ('Arial', 12, 'bold'),
    'body': ('Arial', 10),
    'small': ('Arial', 9)
}

# Layout constants
PADDING = {
    'small': 5,
    'medium': 10,
    'large': 15,
    'xlarge': 20
}

