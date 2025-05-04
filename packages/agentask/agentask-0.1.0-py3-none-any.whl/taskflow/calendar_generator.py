#!/usr/bin/env python3
import os
import re
import datetime
import google.generativeai as genai
from icalendar import Calendar, Event
from .utils import load_environment_variables, ensure_info_folder
from .visual import colored_input, print_choices, BLUE

def generate_calendar(project_path, api_key=None, start_date=None, additional_notes=None, quiet=False):
    """
    Generate a calendar file in .ics format based on the plan.md file.
    
    Args:
        project_path (str): Path to the project folder
        api_key (str, optional): Gemini API key
        start_date (str, optional): Start date in the format day/month/year
        additional_notes (str, optional): Additional notes to include in the prompt
        quiet (bool, optional): Whether to suppress output
        
    Returns:
        str: Path to the generated calendar file
    """
    # Extract the project name from the project path to use as a prefix for event names
    project_name = os.path.basename(project_path)
    # Extract only the word before the first underscore for the prefix
    prefix = project_name.split('_')[0]
    # Get API key and model from environment if not provided
    if api_key is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Gemini API key not provided and not found in environment variable GEMINI_API_KEY")
    
    # Get model name from environment variables
    _, _, model_name = load_environment_variables(project_path)
    
    # Configure the Gemini API
    genai.configure(api_key=api_key)
    
    # Check if the plan file exists
    plan_file = os.path.join(project_path, "info", "plan.md")
    if not os.path.exists(plan_file):
        print(f"Plan file not found: {plan_file}")
        print(f"Please run 'plan {os.path.basename(project_path)}' first.")
        return None
    
    # Read the plan file
    with open(plan_file, "r", encoding="utf-8") as f:
        plan_content = f.read()
        
    # Read all other markdown files in the info folder for background information
    info_folder = os.path.join(project_path, "info")
    background_info = ""
    for filename in os.listdir(info_folder):
        if filename.endswith(".md") and filename != "plan.md" and filename != "calendar.md":
            file_path = os.path.join(info_folder, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    background_info += f"\n\n# Content from {filename}:\n{content}"
            except Exception as e:
                if not quiet:
                    print(f"Warning: Could not read file {filename}: {e}")
        
    # Extract start date information from the plan file
    # Try multiple patterns to match the start date in different formats
    start_date_match = re.search(r'\*\*Start Date:\*\* (\d{2}/\d{2}/\d{4})', plan_content)
    if not start_date_match:
        start_date_match = re.search(r'Start Date: (\d{2}/\d{2}/\d{4})', plan_content)
    if not start_date_match:
        start_date_match = re.search(r'\*\*Start date:\*\* (\d{2}/\d{2}/\d{4})', plan_content)
    if not start_date_match:
        start_date_match = re.search(r'Start date: (\d{2}/\d{2}/\d{4})', plan_content)
    if not start_date_match:
        # Try the markdown list format
        start_date_match = re.search(r'\*\s+\*\*Start Date:\*\* (\d{2}/\d{2}/\d{4})', plan_content)
    if not start_date_match:
        start_date_match = re.search(r'\*\s+\*\*Start date:\*\* (\d{2}/\d{2}/\d{4})', plan_content)
        
    start_date_str = None
    if start_date_match:
        start_date_str = start_date_match.group(1)
        try:
            start_date_date = datetime.datetime.strptime(start_date_str, "%d/%m/%Y").date()
        except ValueError:
            start_date_date = None
    else:
        start_date_date = None
        
    # Extract deadline information from the plan file
    # Try multiple patterns to match the deadline in different formats
    deadline_match = re.search(r'\*\*Deadline:\*\* (\d{2}/\d{2}/\d{4})', plan_content)
    if not deadline_match:
        deadline_match = re.search(r'Deadline: (\d{2}/\d{2}/\d{4})', plan_content)
    deadline_str = None
    if deadline_match:
        deadline_str = deadline_match.group(1)
        try:
            deadline_date = datetime.datetime.strptime(deadline_str, "%d/%m/%Y").date()
        except ValueError:
            deadline_date = None
    else:
        deadline_date = None

    # Use the start date from the plan.md file if available, otherwise use the provided start date
    if start_date_str and start_date is None:
        start_date = start_date_str
    elif start_date is None and start_date_date is not None:
        # Use the parsed start date from plan.md
        start_date = start_date_date.strftime('%d/%m/%Y')
    elif start_date is None:
        # Only use current date as a last resort if no start date is found anywhere
        current_date = datetime.datetime.now()
        start_date = current_date.strftime('%d/%m/%Y')
        
    # Display project range information if both start date and deadline are available
    if start_date and deadline_str and not quiet:
        print(f"Project range: {start_date} - {deadline_str}")
    start_datetime = datetime.datetime.strptime(start_date, '%d/%m/%Y')
    
    # Generate calendar events using Gemini API
    model = genai.GenerativeModel(model_name)
    
    deadline_info = ""
    if deadline_date:
        deadline_info = f"IMPORTANT: The project has a deadline of {deadline_date.strftime('%Y-%m-%d')}. Make sure the plan extends to this date and all tasks are completed by this deadline."
    
    # Include additional notes in the prompt if provided
    notes_info = ""
    if additional_notes:
        notes_info = f"\n\nADDITIONAL NOTES FROM USER:\n{additional_notes}\n\nIMPORTANT: Please take these notes into account when generating the calendar events with the following strict rules:\n1. The calendar MUST start exactly on {start_date} - do not shift the start date forward.\n2. If the user mentions they have already completed certain tasks, simply omit those specific tasks from the calendar.\n3. Do not skip days or adjust the overall timeline - maintain the original project duration.\n4. The first calendar event MUST be scheduled on {start_date}."
    
    prompt = f"""
    I need you to create a calendar of events based on the following information. Please read all three sections carefully before generating the calendar.
    
    CRITICAL REQUIREMENTS:
    - The calendar MUST start on {start_date} - this is a hard requirement
    - The first task MUST be scheduled to begin on {start_date}
    - The project ends on {deadline_str}
    - IMPORTANT: Add the prefix '{prefix}-' to EVERY event name (e.g., '{prefix}-1.1 Task Name')
    - IMPORTANT: EVERY DAY in the project period (from {start_date} to {deadline_str}) MUST have at least one task assigned to it
    
    For each task, provide the following information in a structured format:
    
    1. Task name
    2. Start date and time (in format YYYY-MM-DD HH:MM)
    3. End date and time (in format YYYY-MM-DD HH:MM)
    4. Description (optional)
    
    Format your response as a JSON array of events, with each event having the fields: name, start, end, description.
    Make sure all dates and times are specific and in the correct format.
    
    IMPORTANT: The plan should start on {start_datetime.strftime('%Y-%m-%d')}. Please ensure that the first task starts on or after this date, and adjust all other task dates accordingly.
    {deadline_info}
    
    ===== SECTION 1: PRIMARY INFORMATION - PROJECT PLAN =====
    
    {plan_content}
    
    ===== SECTION 2: BACKGROUND INFORMATION - OTHER PROJECT DOCUMENTS =====
    {background_info}
    
    ===== SECTION 3: ADDITIONAL INFORMATION - USER NOTES =====
    {notes_info}
    
    Based on ALL the information above, generate a comprehensive calendar that accurately reflects the project timeline and tasks.
    """
    
    response = model.generate_content(prompt)
    events_text = response.text
    
    # Extract JSON content from the response
    json_match = re.search(r'```json\s*(.+?)\s*```', events_text, re.DOTALL)
    if not json_match:
        json_match = re.search(r'```\s*(.+?)\s*```', events_text, re.DOTALL)
    if not json_match:
        json_match = re.search(r'\[\s*{.+}\s*\]', events_text, re.DOTALL)
    
    if json_match:
        events_json = json_match.group(1)
    else:
        print("Could not extract JSON from the API response. Using a simpler approach.")
        # Use a simpler approach to extract events
        return generate_simple_calendar(project_path, plan_content)
    
    # Create a calendar
    cal = Calendar()
    cal.add('prodid', '-//AI Task Calendar Generator//ai_task//EN')
    cal.add('version', '2.0')
    
    # Parse events from JSON and add to calendar
    import json
    try:
        # Try to parse the JSON directly
        try:
            events = json.loads(events_json)
        except json.JSONDecodeError:
            # If direct parsing fails, try to clean up the JSON string
            events_json = events_json.strip()
            if not events_json.startswith('['):
                events_json = '[' + events_json
            if not events_json.endswith(']'):
                events_json = events_json + ']'
            events = json.loads(events_json)
            
        for event_data in events:
            event = Event()
            event.add('summary', event_data['name'])
            
            # Parse start and end times
            start_dt = datetime.datetime.strptime(event_data['start'], '%Y-%m-%d %H:%M')
            end_dt = datetime.datetime.strptime(event_data['end'], '%Y-%m-%d %H:%M')
            
            event.add('dtstart', start_dt)
            event.add('dtend', end_dt)
            
            if 'description' in event_data and event_data['description']:
                event.add('description', event_data['description'])
            
            cal.add_component(event)
    except Exception as e:
        print(f"Error parsing events: {e}")
        return generate_simple_calendar(project_path, plan_content)
    
    # Save the calendar to a file
    calendar_file = os.path.join(project_path, "info", "calendar.ics")
    with open(calendar_file, "wb") as f:
        f.write(cal.to_ical())
    
    if not quiet:
        print(f"Calendar file saved to: {calendar_file}")
    return calendar_file

def generate_simple_calendar(project_path, plan_content):
    """
    Generate a simple calendar file based on the plan content.
    This is a fallback method when the API-based approach fails.
    
    Args:
        project_path (str): Path to the project folder
        plan_content (str): Content of the plan file
    
    Returns:
        str: Path to the generated calendar file
    """
    print("Generating a simple calendar based on the plan...")
    
    # Create a calendar
    cal = Calendar()
    cal.add('prodid', '-//AI Task Calendar Generator//ai_task//EN')
    cal.add('version', '2.0')
    
    # Extract task headings using regex
    tasks = re.findall(r'##\s*(.+?)\n', plan_content)
    
    # Get today's date as the starting point
    start_date = datetime.datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    
    # Add each task as an event
    for i, task in enumerate(tasks):
        event = Event()
        event.add('summary', task)
        
        # Simple scheduling: each task takes 2 hours, starting from today
        task_start = start_date + datetime.timedelta(days=i)
        task_end = task_start + datetime.timedelta(hours=2)
        
        event.add('dtstart', task_start)
        event.add('dtend', task_end)
        event.add('description', f"Task from project plan: {task}")
        
        cal.add_component(event)
    
    # Save the calendar to a file
    info_folder = ensure_info_folder(project_path)
    calendar_file = os.path.join(info_folder, "calendar.ics")
    
    with open(calendar_file, "wb") as f:
        f.write(cal.to_ical())
    
    print(f"Simple calendar file saved to: {calendar_file}")
    return calendar_file
