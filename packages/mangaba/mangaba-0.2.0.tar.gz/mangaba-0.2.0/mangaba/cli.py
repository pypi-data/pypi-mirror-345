"""
Command-line interface for Mangaba.AI
"""
import argparse
import sys
from pathlib import Path

# Import version from the package
from mangaba import __version__


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Mangaba.AI - Framework para equipes de agentes AI autônomos"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"Mangaba.AI v{__version__}"
    )
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Example command: init
    init_parser = subparsers.add_parser("init", help="Initialize a new Mangaba project")
    init_parser.add_argument("--path", type=str, default=".", help="Path to initialize project")
    
    # Example command: run
    run_parser = subparsers.add_parser("run", help="Run a Mangaba agent or team")
    run_parser.add_argument("--config", type=str, required=True, help="Path to configuration file")
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no command is provided, show help
    if not args.command:
        parser.print_help()
        return
    
    # Handle commands
    if args.command == "init":
        print(f"Initializing new Mangaba project at {args.path}")
        # Implementation for init command
    
    elif args.command == "run":
        print(f"Running Mangaba with configuration from {args.config}")
        # Implementation for run command


if __name__ == "__main__":
    main()
