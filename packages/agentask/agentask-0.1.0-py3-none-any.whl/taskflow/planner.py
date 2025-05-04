#!/usr/bin/env python3
import os
import sys
import datetime
import google.generativeai as genai
from .utils import load_environment_variables, ensure_info_folder, parse_time_range

def parse_deadline(deadline_str):
    """
    Parse a deadline string in the format day/month/year.
    
    Args:
        deadline_str (str): Deadline string in the format day/month/year
    
    Returns:
        datetime.datetime: Parsed deadline
    """
    try:
        day, month, year = map(int, deadline_str.split('/'))
        return datetime.datetime(year, month, day)
    except ValueError as e:
        raise ValueError(f"Invalid deadline format. Please use day/month/year format. Error: {e}")

def parse_start_date(start_date_str):
    """
    Parse a start date string in the format day/month/year.
    
    Args:
        start_date_str (str): Start date string in the format day/month/year
    
    Returns:
        datetime.datetime: Parsed start date
    """
    try:
        day, month, year = map(int, start_date_str.split('/'))
        return datetime.datetime(year, month, day)
    except ValueError as e:
        raise ValueError(f"Invalid start date format. Please use day/month/year format. Error: {e}")

def generate_plan(project_path, start_date_str, deadline_str, priority, time_range_str, available_hours=None, api_key=None, additional_notes=None, quiet=False):
    """
    Generate a detailed plan for the project.
    
    Args:
        project_path (str): Path to the project folder
        start_date_str (str): Start date string in the format day/month/year
        deadline_str (str): Deadline string in the format day/month/year
        priority (int): Priority percentage (0-100)
        time_range_str (str): Time range string in the format "7-9, 22-23"
        available_hours (float, optional): Available working hours per day (24 - unavailable hours)
        api_key (str, optional): Gemini API key
        additional_notes (str, optional): Additional information provided by the user
        quiet (bool, optional): Whether to suppress output
    
    Returns:
        str: Path to the generated plan file
    """
    # Get API key and model from environment if not provided
    if api_key is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Gemini API key not provided and not found in environment variable GEMINI_API_KEY")
    
    # Get model name from environment variables
    _, _, model_name = load_environment_variables(project_path)
    
    # Configure the Gemini API
    genai.configure(api_key=api_key)
    
    # Parse the start date and deadline
    try:
        start_date = parse_start_date(start_date_str)
    except ValueError as e:
        raise ValueError(f"Error parsing start date: {e}")
        
    try:
        deadline = parse_deadline(deadline_str)
    except ValueError as e:
        raise ValueError(f"Error parsing deadline: {e}")
        return None
    
    # Parse the time range
    try:
        time_ranges = parse_time_range(time_range_str)
    except ValueError as e:
        print(f"Error parsing time range: {e}")
        return None
    
    # Check if the summary file exists
    summary_file = os.path.join(project_path, "info", "summary.md")
    if not os.path.exists(summary_file):
        print(f"Summary file not found: {summary_file}")
        print("Please generate a summary first using the 'understand' command.")
        return None
    
    # Read the summary file
    with open(summary_file, "r", encoding="utf-8") as f:
        summary_content = f.read()
        
    # Read all other markdown files in the info folder for background information
    info_folder = os.path.join(project_path, "info")
    background_info = ""
    for filename in os.listdir(info_folder):
        if filename.endswith(".md") and filename != "summary.md" and filename != "plan.md" and filename != "calendar.md":
            file_path = os.path.join(info_folder, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    background_info += f"\n\n# Content from {filename}:\n{content}"
            except Exception as e:
                if not quiet:
                    print(f"Warning: Could not read file {filename}: {e}")
    
    # Calculate days until deadline
    today = datetime.datetime.now()
    days_until_deadline = (deadline - today).days
    
    # Format time ranges for the prompt
    time_ranges_str = ", ".join([f"{start}-{end}" for start, end in time_ranges])
    
    # Generate a plan using Gemini API
    if not quiet:
        print("Generating plan using Gemini API...")
        # Use the model name from environment variables
        print(f"Using Gemini model: {model_name}")
    model = genai.GenerativeModel(model_name)
    
    # Include available hours information in the prompt if provided
    available_hours_info = ""
    if available_hours is not None:
        daily_task_hours = (available_hours * priority) / 100
        available_hours_info = f"- Available working hours per day: {available_hours} hours\n    - Based on priority, you should spend approximately {daily_task_hours:.1f} hours per day on this project"
    
    # Calculate project duration
    days_duration = (deadline.date() - start_date.date()).days
    
    # Include additional notes in the prompt if provided
    notes_info = ""
    if additional_notes:
        notes_info = f"\n\n{additional_notes}"
    
    prompt = f"""
    I need you to create a detailed project plan based on the following information. Please read all three sections carefully before generating the plan.
    
    ===== SECTION 1: PRIMARY INFORMATION - PROJECT REQUIREMENTS =====
    
    # Task Information
    - Start date: {start_date.strftime('%d/%m/%Y')}
    - Deadline: {deadline.strftime('%d/%m/%Y')} ({days_until_deadline} days from now)
    - Project duration: {days_duration} days
    - Priority: {priority}%
    - Preferred working hours: {time_ranges_str}
    {available_hours_info}
    
    # Task Summary
    {summary_content}
    
    ===== SECTION 2: BACKGROUND INFORMATION - OTHER PROJECT DOCUMENTS =====
    {background_info}
    
    ===== SECTION 3: ADDITIONAL INFORMATION - USER NOTES =====
    {notes_info}
    
    Based on ALL the information above, please create a detailed plan that includes:
    
    1. A breakdown of the task into manageable subtasks on a daily basis throughout the project period
    2. Estimated time required for each subtask
    3. Suggested schedule based on the preferred working hours
    4. Key milestones and deadlines
    5. Resources needed for each subtask
    
    Format the plan as a well-structured markdown document with clear headings and bullet points.
    Make sure the plan is realistic and achievable within the given deadline and working hours.
    Include the start date and deadline in the plan document for reference.
    """
    
    response = model.generate_content(prompt)
    plan_content = response.text
    
    # Save the plan to a file
    info_folder = ensure_info_folder(project_path)
    plan_file = os.path.join(info_folder, "plan.md")
    
    with open(plan_file, "w", encoding="utf-8") as f:
        f.write(plan_content)
    
    print(f"Plan file saved to: {plan_file}")
    return plan_file
