"""
Aggregates all CLI commands for Force-Fusion dashboard.
"""

import argparse
from typing import List, Optional

from force_fusion.cli import env, test, websocket


def setup_parser() -> argparse.ArgumentParser:
    """
    Set up the main argument parser with all available commands.

    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(description="Force-Fusion Vehicle Dashboard")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Add CLI commands
    test.setup_parser(subparsers)
    env.setup_parser(subparsers)
    websocket.setup_parser(subparsers)

    return parser


def print_help() -> None:
    """Print the help message."""
    print("Force-Fusion Vehicle Dashboard")
    print("\nUsage:")
    print("  force-fusion [command] [options]")
    print("\nCommands:")
    print("  test [widget]    Run widget tests")
    print("  env              Export configuration to .env file")
    print("  websocket        Start or manage the WebSocket server")
    print("\nRun force-fusion <command> --help for command-specific help.")


def process_args(cli_args: Optional[List[str]] = None) -> int:
    """
    Process command line arguments and run the appropriate command.

    Args:
        cli_args: Command line arguments (or None to use sys.argv)

    Returns:
        int: Exit code
    """
    parser = setup_parser()
    args = parser.parse_args(cli_args)

    # Handle commands
    if args.command == "test":
        return test.run_test_command(args)
    elif args.command == "env":
        return env.run_env_command(args)
    elif args.command == "websocket":
        return websocket.run_websocket_command(args)

    # If no command provided, return None to indicate the GUI should run
    return None
