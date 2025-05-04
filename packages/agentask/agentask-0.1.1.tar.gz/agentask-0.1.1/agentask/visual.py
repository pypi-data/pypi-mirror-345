#!/usr/bin/env python3
import sys
import time
import os
import contextlib
from tqdm import tqdm

# ANSI color codes
ORANGE = "\033[38;5;208m"
GREEN = "\033[32m"
BLUE = "\033[34m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_logo():
    """Print the TaskFlow logo in retro terminal style."""
    logo = f"""
{BLUE}{BOLD}
    ████████╗ █████╗ ███████╗██╗  ██╗███████╗██╗      ██████╗ ██╗    ██╗
    ╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝██╔════╝██║     ██╔═══██╗██║    ██║
       ██║   ███████║███████╗█████╔╝ █████╗  ██║     ██║   ██║██║ █╗ ██║
       ██║   ██╔══██║╚════██║██╔═██╗ ██╔══╝  ██║     ██║   ██║██║███╗██║
       ██║   ██║  ██║███████║██║  ██╗██║     ███████╗╚██████╔╝╚███╔███╔╝
       ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝ 
{RESET}
   {CYAN}Your AI-powered task planning assistant{RESET}
   {YELLOW}Version 0.1.0{RESET}
"""
    print(logo)

def progress_bar(description, num_steps=10, duration=1.0):
    """
    Display a progress bar with a description.
    
    Args:
        description (str): Description of the task
        num_steps (int): Number of steps in the progress bar
        duration (float): Total duration in seconds
    """
    print(f"{BLUE}{description}...{RESET}")
    for _ in tqdm(range(num_steps), desc="  Progress", ncols=70, bar_format="{l_bar}{bar}"):
        time.sleep(duration / num_steps)
    print(f"{GREEN}✓ Done{RESET}")

def simple_progress(description, duration=1.0):
    """
    Display a simple progress indicator without a progress bar.
    
    Args:
        description (str): Description of the task
        duration (float): Total duration in seconds
    """
    print(f"{BLUE}{description}...{RESET}")
    sys.stdout.flush()
    time.sleep(duration)
    print(f"{GREEN}✓ Done{RESET}")


def colored_input(prompt, color=BLUE):
    """
    Display a colored prompt for input.
    
    Args:
        prompt (str): The input prompt to display
        color (str): ANSI color code to use
        
    Returns:
        str: User input
    """
    return input(f"{color}{prompt}{RESET}")


@contextlib.contextmanager
def suppress_stderr():
    """
    Context manager to suppress stderr output.
    Useful for hiding warning messages from libraries.
    """
    original_stderr = sys.stderr
    null_file = open(os.devnull, 'w')
    try:
        sys.stderr = null_file
        yield
    finally:
        sys.stderr = original_stderr
        null_file.close()


def run_with_suppressed_warnings(func, *args, **kwargs):
    """
    Run a function with all warnings suppressed.
    This is more aggressive than just using suppress_stderr.
    
    Args:
        func: The function to run
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        The return value of the function
    """
    # Suppress all warnings
    import warnings
    import os
    import sys
    import logging
    
    # Disable all logging
    logging.disable(logging.CRITICAL)
    
    # Suppress all warnings
    warnings.filterwarnings("ignore")
    
    # Save original stderr
    original_stderr = sys.stderr
    
    try:
        # Redirect stderr to /dev/null
        null_fd = open(os.devnull, 'w')
        sys.stderr = null_fd
        
        # Run the function
        result = func(*args, **kwargs)
        
        # Force flush and close stderr to ensure all warnings are captured
        sys.stderr.flush()
        
        return result
    finally:
        # Restore stderr
        sys.stderr = original_stderr
        
        # Close the null file descriptor
        try:
            null_fd.close()
        except:
            pass


def print_choices(choices, color=BLUE):
    """
    Print a list of choices with colored formatting.
    
    Args:
        choices (list): List of choice strings
        color (str): ANSI color code to use
    """
    for i, choice in enumerate(choices, 1):
        print(f"{color}{i}. {choice}{RESET}")


def success_message(message, color=BLUE):
    """
    Print a success message with colored formatting.
    
    Args:
        message (str): The success message to display
        color (str): ANSI color code to use
    """
    print(f"{color}{message}{RESET}")
