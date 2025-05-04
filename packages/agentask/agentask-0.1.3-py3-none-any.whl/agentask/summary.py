#!/usr/bin/env python3
import os
import sys
import glob
import google.generativeai as genai
from .utils import load_environment_variables, get_markdown_files, ensure_info_folder

def generate_summary(project_path, api_key=None, quiet=False):
    """
    Generate a summary of the task based on markdown files in the 'info' folder.
    
    Args:
        project_path (str): Path to the project folder
        api_key (str, optional): Gemini API key
        quiet (bool, optional): If True, suppress detailed output
    
    Returns:
        str: Path to the generated summary file
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
    
    # Get all markdown files in the info folder
    md_files = get_markdown_files(project_path)
    if not md_files:
        if not quiet:
            print(f"No markdown files found in the 'info' folder of {project_path}")
        return None
    
    # Read the content of all markdown files
    all_content = ""
    for md_file in md_files:
        # Skip summary.md if it already exists
        if os.path.basename(md_file) == "summary.md":
            continue
            
        if not quiet:
            print(f"Reading {md_file}...")
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
            all_content += f"\n\n# {os.path.basename(md_file)}\n\n{content}"
    
    if not all_content.strip():
        print("No content found in markdown files")
        return None
    
    # Generate a summary using Gemini API
    if not quiet:
        print("Generating summary using Gemini API...")
        print(f"Using Gemini model: {model_name}")
    model = genai.GenerativeModel(model_name)
    
    prompt = f"""
    Based on the following information, generate a comprehensive summary of the task.
    Organize the summary in the following format:
    
    # Task Summary
    
    ## What
    [Provide a clear and concise description of what the task is about]
    
    ## Why
    [Explain the purpose and importance of the task]
    
    ## How
    [Outline the general approach or methodology to complete the task]
    
    ## Key Points for Excellent Execution
    [List the most important points to focus on for excellent execution]
    
    Here is the information:
    
    {all_content}
    """
    
    response = model.generate_content(prompt)
    summary_content = response.text
    
    # Save the summary to a file
    info_folder = ensure_info_folder(project_path)
    summary_file = os.path.join(project_path, "info", "summary.md")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary_content)
    
    if not quiet:
        print(f"Summary file saved to: {summary_file}")
    return summary_file
