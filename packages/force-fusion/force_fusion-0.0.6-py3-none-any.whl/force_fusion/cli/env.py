"""
CLI command to export Force-Fusion configuration as a .env file.
"""

import argparse
import os
import sys

from force_fusion.utils.env_utils import config_manager


def run_env_command(args):
    """
    Run the env command with the given arguments.

    Args:
        args: Command line arguments
    """
    if args.output:
        output_path = args.output
    else:
        # Default to .env in current directory
        output_path = os.path.join(os.getcwd(), ".env")

    # Check if file exists and confirm overwrite if --force not provided
    if os.path.exists(output_path) and not args.force:
        confirm = input(f"File {output_path} already exists. Overwrite? (y/N): ")
        if confirm.lower() not in ("y", "yes"):
            print("Operation cancelled.")
            return 1

    # Export the config to .env file
    config_manager.export_to_env(output_path)
    return 0


def setup_parser(subparsers):
    """
    Set up the command line parser for the env command.

    Args:
        subparsers: Subparsers object from argparse
    """
    env_parser = subparsers.add_parser("env", help="Export configuration to .env file")
    env_parser.add_argument(
        "-o", "--output", help="Output file path (default: .env in current directory)"
    )
    env_parser.add_argument(
        "-f", "--force", action="store_true", help="Force overwrite if file exists"
    )

    return env_parser


def main():
    """Main entry point when running as a script."""
    parser = argparse.ArgumentParser(description="Export Force-Fusion configuration")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument(
        "-f", "--force", action="store_true", help="Force overwrite if file exists"
    )

    args = parser.parse_args()
    return run_env_command(args)


if __name__ == "__main__":
    sys.exit(main())
