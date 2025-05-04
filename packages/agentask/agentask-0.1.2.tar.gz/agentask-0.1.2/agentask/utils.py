#!/usr/bin/env python3
import os
import sys
import glob
from pathlib import Path
from dotenv import load_dotenv

def load_environment_variables(project_path=None, quiet=False):
    """
    Load environment variables from .env file in the specified project path or current directory.
    Check if required API keys are present.
    
    Args:
        project_path (str, optional): Path to the project folder containing the .env file
        quiet (bool, optional): If True, suppress print statements
    
    Returns:
        tuple: (mistral_api_key, gemini_api_key, model)
    """
    # Load environment variables from .env file
    if project_path and os.path.exists(os.path.join(project_path, ".env")):
        # Load from project path if specified and .env exists there
        env_path = os.path.join(project_path, ".env")
        load_dotenv(dotenv_path=env_path)
        # Never print this message as it clutters the output
    else:
        # Fall back to current directory
        load_dotenv()
    
    # Check if required API keys are present
    mistral_api_key = os.environ.get("MISTRAL_API_KEY")
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    
    # Get the model name if specified, otherwise use default
    model = os.environ.get("MODEL", "gemini-2.5-flash-preview-04-17")
    
    if not mistral_api_key and not quiet:
        print("Warning: MISTRAL_API_KEY not found in environment variables.")
    
    if not gemini_api_key and not quiet:
        print("Warning: GEMINI_API_KEY not found in environment variables.")
    
    return mistral_api_key, gemini_api_key, model

def check_info_folder(project_path):
    """
    Check if the 'info' folder exists in the project path and contains any files.
    Accepts both PDF and markdown files.
    
    Args:
        project_path (str): Path to the project folder
    
    Returns:
        bool: True if the info folder exists and contains files, False otherwise
    """
    info_folder = os.path.join(project_path, "info")
    
    # Check if the info folder exists
    if not os.path.exists(info_folder) or not os.path.isdir(info_folder):
        print(f"Error: 'info' folder not found in {project_path}")
        return False
    
    # Check if the info folder contains any files
    files = os.listdir(info_folder)
    if not files:
        print(f"Error: 'info' folder in {project_path} is empty")
        return False
    
    # Check if there are any PDF or markdown files
    pdf_files = glob.glob(os.path.join(info_folder, "*.pdf"))
    md_files = glob.glob(os.path.join(info_folder, "*.md"))
    
    if not pdf_files and not md_files:
        print(f"Error: No PDF or markdown files found in the 'info' folder of {project_path}")
        return False
    
    return True

def get_pdf_files(project_path):
    """
    Get all PDF files in the 'info' folder of the project.
    
    Args:
        project_path (str): Path to the project folder
    
    Returns:
        list: List of paths to PDF files in the info folder
    """
    info_folder = os.path.join(project_path, "info")
    pdf_files = glob.glob(os.path.join(info_folder, "*.pdf"))
    return pdf_files

def get_markdown_files(project_path):
    """
    Get all markdown files in the 'info' folder of the project.
    
    Args:
        project_path (str): Path to the project folder
    
    Returns:
        list: List of paths to markdown files in the info folder
    """
    info_folder = os.path.join(project_path, "info")
    md_files = glob.glob(os.path.join(info_folder, "*.md"))
    return md_files

def ensure_info_folder(project_path):
    """
    Ensure that the 'info' folder exists in the project path.
    Create it if it doesn't exist.
    
    Args:
        project_path (str): Path to the project folder
    
    Returns:
        str: Path to the info folder
    """
    info_folder = os.path.join(project_path, "info")
    
    # Create the info folder if it doesn't exist
    if not os.path.exists(info_folder):
        os.makedirs(info_folder)
    
    return info_folder

def parse_time_range(time_range_str):
    """
    Parse a time range string in the format "7-9, 22-23" into a list of tuples.
    
    Args:
        time_range_str (str): Time range string in the format "7-9, 22-23"
    
    Returns:
        list: List of tuples representing time ranges, e.g. [(7, 9), (22, 23)]
    """
    time_ranges = []
    
    # Split by comma and process each range
    for range_str in time_range_str.split(','):
        # Remove whitespace and split by hyphen
        start, end = map(int, range_str.strip().split('-'))
        time_ranges.append((start, end))
    
    return time_ranges
