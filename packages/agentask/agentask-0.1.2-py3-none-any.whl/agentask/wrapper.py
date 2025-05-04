#!/usr/bin/env python3
"""
Wrapper script to suppress stderr warnings when running AI Task commands.
"""
import os
import sys
import subprocess

def run_command_with_suppressed_warnings(command):
    """
    Run a command with stderr redirected to /dev/null.
    
    Args:
        command (str): The command to run
    """
    # Create a null file to redirect stderr
    with open(os.devnull, 'w') as devnull:
        # Run the command with stderr redirected to /dev/null
        subprocess.run(command, stderr=devnull)

def main():
    """
    Main entry point for the wrapper script.
    """
    # Get the command from the command line arguments
    if len(sys.argv) < 2:
        print("Usage: python -m ai_task.wrapper [command]")
        return 1
    
    # The first argument is the command to run
    command = sys.argv[1]
    
    # Map the command to the appropriate module
    command_map = {
        "understand": ["python", "-m", "ai_task.understand_main"],
        "plan": ["python", "-m", "ai_task.plan_main"],
        "generate-calendar": ["python", "-m", "ai_task.calendar_main"]
    }
    
    if command not in command_map:
        print(f"Unknown command: {command}")
        return 1
    
    # Get the command to run
    cmd = command_map[command]
    
    # Add any additional arguments
    cmd.extend(sys.argv[2:])
    
    # Run the command with suppressed warnings
    run_command_with_suppressed_warnings(cmd)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
