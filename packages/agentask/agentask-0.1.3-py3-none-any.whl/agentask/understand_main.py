#!/usr/bin/env python3
"""
Entry point for the understand command with warning suppression.
"""
import os
import sys
import logging

# Set environment variables to control Google libraries' logging
os.environ['GRPC_VERBOSITY'] = 'ERROR'    # Limits gRPC logs to errors only
os.environ['GLOG_minloglevel'] = '2'      # Limits Google logging to errors only (0:INFO, 1:WARNING, 2:ERROR, 3:FATAL)

# Disable Python logging
logging.disable(logging.CRITICAL)

from .cli import understand_main

def main():
    """
    Main entry point with warning suppression.
    """
    # Save original stderr
    original_stderr = sys.stderr
    
    try:
        # Redirect stderr to /dev/null
        sys.stderr = open(os.devnull, 'w')
        
        # Run the command
        return understand_main()
    finally:
        # Restore stderr
        sys.stderr = original_stderr

if __name__ == "__main__":
    sys.exit(main())
