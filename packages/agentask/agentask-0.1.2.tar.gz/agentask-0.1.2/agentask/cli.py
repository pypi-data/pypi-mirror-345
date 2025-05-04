#!/usr/bin/env python3
import os
import sys
import re
import argparse
import datetime
from pathlib import Path

# Redirect stderr to /dev/null to suppress all warning messages
# This is done at the module level to ensure it affects all code
original_stderr = sys.stderr
sys.stderr = open(os.devnull, 'w')

from .utils import load_environment_variables, check_info_folder, get_pdf_files
from .ocr import process_project_pdfs
from .summary import generate_summary
from .planner import generate_plan
from .calendar_generator import generate_calendar
from .visual import print_logo, progress_bar, simple_progress, colored_input, print_choices, suppress_stderr, success_message, run_with_suppressed_warnings, BLUE, RESET

def understand_command(args):
    """
    Handle the 'understand' command.
    
    Args:
        args: Command-line arguments
    """
    # Display the AI Task logo
    print_logo()
    
    project_name = args.project_name
    
    # Special case: If project_name matches the current directory name,
    # use the current directory
    current_dir = os.path.basename(os.getcwd())
    if project_name == current_dir:
        project_path = os.getcwd()
    else:
        project_path = os.path.abspath(project_name)
    
    # Check if the project directory exists
    if not os.path.exists(project_path) or not os.path.isdir(project_path):
        print(f"Error: Project directory '{project_name}' not found.")
        return 1
    
    # Load environment variables from the project directory
    mistral_api_key, gemini_api_key, model_name = load_environment_variables(project_path, quiet=True)
    if not mistral_api_key or not gemini_api_key:
        print("Error: Required API keys not found in .env file.")
        return 1
    
    # Use progress bars for the main steps
    simple_progress("Models waking up")
    progress_bar("Understanding the project", num_steps=8, duration=1.5)
    
    # Process files in the info folder (silently)
    markdown_files = process_project_pdfs(project_path, api_key=mistral_api_key, quiet=True)
    if not markdown_files:
        print("Error: No markdown files found or generated in the 'info' folder.")
        return 1
    
    # Generate summary using Gemini API
    progress_bar("Generating the summary", num_steps=10, duration=2.0)
    summary_file = generate_summary(project_path, api_key=gemini_api_key, quiet=True)
    if not summary_file:
        print("Error: Failed to generate summary.")
        return 1
    
    success_message("Task understood, summary file generated in info folder.")
    return 0

def plan_command(args):
    """
    Handle the 'plan' command.
    
    Args:
        args: Command-line arguments
    """
    project_name = args.project_name
    
    # Special case: If project_name matches the current directory name,
    # use the current directory
    current_dir = os.path.basename(os.getcwd())
    if project_name == current_dir:
        project_path = os.getcwd()
    else:
        project_path = os.path.abspath(project_name)
    
    # Check if the project directory exists
    if not os.path.exists(project_path) or not os.path.isdir(project_path):
        print(f"Error: Project directory '{project_name}' not found.")
        return 1
    
    # Check if the summary file exists
    summary_file = os.path.join(project_path, "info", "summary.md")
    if not os.path.exists(summary_file):
        print(f"Summary file not found: {summary_file}")
        print(f"Please run 'understand {project_name}' first.")
        return 1
    
    # Load environment variables from the project directory
    _, gemini_api_key, model_name = load_environment_variables(project_path, quiet=True)
    # Model name is available but we don't need to print it
    if not gemini_api_key:
        print("Error: GEMINI_API_KEY not found in .env file.")
        return 1
    
    # Get start date from command-line arguments or user input
    if hasattr(args, 'start_date') and args.start_date:
        start_date = args.start_date
        print(f"Using start date: {start_date}")
    else:
        start_date = colored_input(f"{BLUE}Please input the project start date in the format of day/month/year: {RESET}")
    
    # Get deadline from command-line arguments or user input
    if hasattr(args, 'deadline') and args.deadline:
        deadline = args.deadline
        print(f"Using deadline: {deadline}")
    else:
        deadline = colored_input("Please input the project deadline in the format of day/month/year: ")
    
    # Get priority from command-line arguments or user input
    if hasattr(args, 'priority') and args.priority is not None:
        priority = args.priority
        if priority < 0 or priority > 100:
            print("Error: Priority must be between 0 and 100.")
            return 1
        print(f"Using priority: {priority}%")
    else:
        priority_str = colored_input("Deadline received, what is your priority(%) of this project? ")
        try:
            priority = int(priority_str)
            if priority < 0 or priority > 100:
                print("Error: Priority must be between 0 and 100.")
                return 1
        except ValueError:
            print("Error: Priority must be a number between 0 and 100.")
            return 1
    
    # Calculate remaining priority
    remaining_priority = 100 - priority
    print(f"Priority set at {priority}%, your remaining priority balance is {remaining_priority}%.")    
    
    # Get unavailable time from command-line arguments or user input
    if hasattr(args, 'unavailable_hours') and args.unavailable_hours is not None:
        unavailable_hours = args.unavailable_hours
        if unavailable_hours < 0 or unavailable_hours > 24:
            print("Error: Unavailable hours must be between 0 and 24.")
            return 1
        print(f"Using unavailable hours: {unavailable_hours} hours")
    else:
        unavailable_hours_str = colored_input("How long is your unavailable time in a day? (hours): ")
        try:
            unavailable_hours = float(unavailable_hours_str)
            if unavailable_hours < 0 or unavailable_hours > 24:
                print("Error: Unavailable hours must be between 0 and 24.")
                return 1
        except ValueError:
            print("Error: Unavailable hours must be a number between 0 and 24.")
            return 1
    
    # Calculate available working hours
    available_hours = 24 - unavailable_hours
    print(f"Received, available working hour = {available_hours} hours.")
    
    # Get time range from command-line arguments or user input
    if hasattr(args, 'time_range') and args.time_range:
        time_range = args.time_range
        print(f"Using time range: {time_range}")
    else:
        time_range = colored_input("What time do you prefer to work on this project in a day? ")
    
    # If all arguments were provided via command line, skip confirmation
    if hasattr(args, 'deadline') and args.deadline and \
       hasattr(args, 'priority') and args.priority is not None and \
       hasattr(args, 'unavailable_hours') and args.unavailable_hours is not None and \
       hasattr(args, 'time_range') and args.time_range:
        generate_plan_response = 'y'
    else:
        print(f"Time range set to {time_range}.")
        # Ask if user wants to generate a plan
        generate_plan_response = colored_input("Want to generate a plan? y/n: ").strip().lower()
    
    if generate_plan_response != 'y':
        print("Plan not generated, no plan file generated in info folder.")
        return 0
    
    # Ask if the user has any additional information to provide
    additional_notes = colored_input("Anything else you want us to know? (Press Enter to skip): ").strip()
    
    # Generate a plan using Gemini API with visual elements
    simple_progress("Models waking up")
    progress_bar("Analyzing project requirements", num_steps=6, duration=1.2)
    progress_bar("Generating detailed plan", num_steps=10, duration=2.0)
    
    plan_file = generate_plan(project_path, start_date, deadline, priority, time_range, available_hours=available_hours, api_key=gemini_api_key, additional_notes=additional_notes, quiet=True)
    if not plan_file:
        print("Error: Failed to generate plan.")
        return 1
    
    success_message("Plan generated, plan file generated in info folder.")
    return 0

def calendar_command(args):
    """
    Handle the 'generate calendar' command.
    
    Args:
        args: Command-line arguments
    """
    project_name = args.project_name
    
    # Special case: If project_name matches the current directory name,
    # use the current directory
    current_dir = os.path.basename(os.getcwd())
    if project_name == current_dir:
        project_path = os.getcwd()
    else:
        project_path = os.path.abspath(project_name)
    
    # Check if the project directory exists
    if not os.path.exists(project_path) or not os.path.isdir(project_path):
        print(f"Error: Project directory '{project_name}' not found.")
        return 1
    
    # Check if the plan file exists
    plan_file = os.path.join(project_path, "info", "plan.md")
    if not os.path.exists(plan_file):
        print("Plan absent, please generate the plan first.")
        return 1
    
    # Load environment variables from the project directory
    _, gemini_api_key, model_name = load_environment_variables(project_path, quiet=True)
    # Model name is available but we don't need to print it
    if not gemini_api_key:
        print("Error: GEMINI_API_KEY not found in .env file.")
        return 1
    
    # Get start date from command-line arguments if provided
    start_date = None
    if hasattr(args, 'start_date') and args.start_date:
        start_date = args.start_date
        print(f"Using start date from command line: {start_date}")
    # We don't need to ask for the start date here anymore, as it's now included in the plan.md file
    
    # Get additional notes from command-line arguments or user input
    additional_notes = None
    if hasattr(args, 'notes') and args.notes:
        additional_notes = args.notes
        print(f"Using additional notes from command line")
    else:
        additional_notes_input = colored_input("Anything else you want us to know? (Press Enter to skip): ")
        if additional_notes_input.strip():
            additional_notes = additional_notes_input
            print("Additional notes received.")
    
    # Generate calendar using Gemini API with visual elements
    simple_progress("Models waking up")
    progress_bar("Analyzing project plan", num_steps=6, duration=1.2)
    progress_bar("Generating calendar events", num_steps=10, duration=2.0)
    
    # Pass start_date=None to use the start date from the plan.md file
    calendar_file = generate_calendar(project_path, api_key=gemini_api_key, start_date=start_date, additional_notes=additional_notes, quiet=False)
    if not calendar_file:
        print("Error: Failed to generate calendar.")
        return 1
    
    success_message("Calendar generated, calendar file generated in info folder.")
    return 0

def understand_main():
    """
    Entry point for the understand command.
    """
    parser = argparse.ArgumentParser(description="Understand the task from description files")
    parser.add_argument("project_name", help="Name of the project folder")
    
    args = parser.parse_args()
    return run_with_suppressed_warnings(understand_command, args)

def plan_main():
    """
    Entry point for the plan command.
    """
    parser = argparse.ArgumentParser(description="Generate a plan for the task")
    parser.add_argument("project_name", help="Name of the project folder")
    parser.add_argument("--deadline", help="Project deadline in the format of day/month/year")
    parser.add_argument("--priority", type=int, help="Priority percentage (0-100) of this project")
    parser.add_argument("--unavailable-hours", type=float, help="Hours per day you are unavailable (0-24)")
    parser.add_argument("--time-range", help="Time range when you prefer to work on this project (e.g., '9-12, 14-17')")
    
    args = parser.parse_args()
    return run_with_suppressed_warnings(plan_command, args)

def calendar_main():
    """
    Entry point for the generate calendar command.
    """
    parser = argparse.ArgumentParser(description="Generate a calendar for the task")
    parser.add_argument("project_name", help="Name of the project folder")
    parser.add_argument("--start-date", help="Start date for the calendar in the format of day/month/year (dd/mm/yyyy)")
    parser.add_argument("--notes", help="Additional notes or instructions for calendar generation")
    
    # Parse arguments
    args = parser.parse_args()
    return run_with_suppressed_warnings(calendar_command, args)

def main():
    """
    Main entry point for the CLI.
    This function is kept for backward compatibility.
    """
    parser = argparse.ArgumentParser(description="AI Task Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Understand command
    understand_parser = subparsers.add_parser("understand", help="Understand the task from description files")
    understand_parser.add_argument("project_name", help="Name of the project folder")
    
    # Plan command
    plan_parser = subparsers.add_parser("plan", help="Generate a plan for the task")
    plan_parser.add_argument("project_name", help="Name of the project folder")
    plan_parser.add_argument("--start-date", help="Start date in the format day/month/year")
    
    # Generate calendar command
    calendar_parser = subparsers.add_parser("generate", help="Generate a calendar for the task")
    calendar_parser.add_argument("calendar", help="Generate a calendar for the task", nargs="?", const="calendar")
    calendar_parser.add_argument("project_name", help="Name of the project folder")
    
    args = parser.parse_args()
    
    if args.command == "understand":
        return understand_command(args)
    elif args.command == "plan":
        return plan_command(args)
    elif args.command == "generate" and hasattr(args, "calendar") and args.calendar == "calendar":
        return calendar_command(args)
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
