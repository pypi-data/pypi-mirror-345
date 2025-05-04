import argparse
import os
import sys
from mcp_server import main as mcp_main

def main():
    parser = argparse.ArgumentParser(
        description="Run Talk-To-My-Org-Chart (ttmoc) MCP server"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        help="Path to log file (if not specified, logs will be written to stderr)"
    )
    
    # Parse arguments
    args = parser.parse_args()

    # Set up logging to file if specified
    if args.log_file:
        log_file = open(args.log_file, 'w')
        sys.stderr = log_file
        print(f"Logging to file: {args.log_file}", file=sys.stderr)

    # Initialize the server
    mcp = mcp_main.initialize_server()
    
    # Call the main server logic
    try:
        mcp.run()
    except Exception as e:
        print(f"Error starting MCP server: {str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        if args.log_file and 'log_file' in locals():
            log_file.close()

if __name__ == "__main__":
    main()
