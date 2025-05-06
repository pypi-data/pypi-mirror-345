"""
CLI command to run Force-Fusion widget tests.
"""

import argparse
import sys

from force_fusion.utils.test_utils import (
    test_all,
    test_attitude,
    test_gg_diagram,
    test_heading,
    test_mapbox,
    test_minimap,
    test_speedometer,
    test_tire_force,
)


def run_test_command(args):
    """
    Run the test command with the given arguments.

    Args:
        args: Command line arguments
    """
    # Map widget names to test functions
    test_functions = {
        "all": test_all,
        "minimap": test_minimap,
        "speedometer": test_speedometer,
        "attitude": test_attitude,
        "heading": test_heading,
        "tire_force": test_tire_force,
        "mapbox": test_mapbox,
        "gg_diagram": test_gg_diagram,
    }

    # Get the widget to test
    widget = args.widget

    # Run the test if valid widget
    if widget in test_functions:
        return test_functions[widget]()
    else:
        print(f"Unknown widget: {widget}")
        return 1


def setup_parser(subparsers):
    """
    Set up the command line parser for the test command.

    Args:
        subparsers: Subparsers object from argparse
    """
    test_parser = subparsers.add_parser("test", help="Run widget tests")
    test_parser.add_argument(
        "widget",
        nargs="?",
        default="all",
        choices=[
            "all",
            "minimap",
            "speedometer",
            "attitude",
            "heading",
            "tire_force",
            "mapbox",
            "gg_diagram",
        ],
        help="Widget to test (default: all)",
    )

    return test_parser


def main():
    """Main entry point when running as a script."""
    parser = argparse.ArgumentParser(description="Run Force-Fusion widget tests")
    parser.add_argument(
        "widget",
        nargs="?",
        default="all",
        choices=[
            "all",
            "minimap",
            "speedometer",
            "attitude",
            "heading",
            "tire_force",
            "mapbox",
            "gg_diagram",
        ],
        help="Widget to test (default: all)",
    )

    args = parser.parse_args()
    return run_test_command(args)


if __name__ == "__main__":
    sys.exit(main())
