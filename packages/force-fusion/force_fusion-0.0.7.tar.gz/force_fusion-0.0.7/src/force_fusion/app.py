"""
Main application entry point for Force-Fusion dashboard.
"""

import os
import pathlib
import socket
import subprocess
import sys
import time

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from force_fusion import config
from force_fusion.cli.cli import process_args
from force_fusion.controller import DashboardController
from force_fusion.sensors import SensorProvider
from force_fusion.ui_main_window import MainWindow


def get_version():
    """
    Read the version from pyproject.toml.

    Returns:
        str: The version string from pyproject.toml or "0.1.0" if not found.
    """
    try:
        # Find the pyproject.toml file by looking up from the current file
        module_dir = pathlib.Path(__file__).parent
        project_root = module_dir.parent.parent  # Go up to project root
        pyproject_path = project_root / "pyproject.toml"

        # Try to use tomllib (Python 3.11+) or fallback to toml package
        try:
            if sys.version_info >= (3, 11):
                import tomllib

                with open(pyproject_path, "rb") as f:
                    pyproject_data = tomllib.load(f)
            else:
                # For older Python versions, try to use toml package
                import toml

                with open(pyproject_path, "r") as f:
                    pyproject_data = toml.load(f)

            # Extract the version
            version = pyproject_data.get("project", {}).get("version", "N/A")
            return version
        except ImportError:
            # If neither tomllib nor toml is available, read it manually
            with open(pyproject_path, "r") as f:
                for line in f:
                    if line.strip().startswith("version"):
                        # Extract version from line like 'version = "0.0.6"'
                        return line.split("=")[1].strip().strip("\"'")

            # If version not found, return default
            return "N/A"
    except Exception as e:
        if config.DEBUG_MODE:
            print(f"⚠️ Could not read version from pyproject.toml: {e}")
        return "N/A"


def is_port_in_use(port, host="localhost"):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex((host, port)) == 0


def start_websocket_server():
    """Start the WebSocket server as a background process."""
    try:
        print("🔄 Starting WebSocket server...")

        # Check if a server is already running on this port
        if is_port_in_use(config.WS_PORT):
            print(f"✓ WebSocket server already running on port {config.WS_PORT}")
            return True  # Server is already running

        # Start WebSocket server as a subprocess that will continue running after app exit
        cmd = [sys.executable, "-m", "force_fusion.utils.websocket_server"]

        # Use platform-specific methods to start a detached process
        if sys.platform == "win32":
            # Windows - use DETACHED_PROCESS
            process = subprocess.Popen(  # noqa: F841
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=subprocess.DETACHED_PROCESS
                | subprocess.CREATE_NEW_PROCESS_GROUP,
            )
        else:
            # Unix/Linux - use daemon approach
            process = subprocess.Popen(  # noqa: F841
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                preexec_fn=os.setpgrp,  # This creates a new process group
            )

        # Wait for the server to start
        max_attempts = 20  # Wait up to 4 seconds (20 * 0.2)
        for attempt in range(max_attempts):
            time.sleep(0.2)
            if is_port_in_use(config.WS_PORT):
                print(
                    f"✓ WebSocket server started successfully on port {config.WS_PORT}"
                )
                # Extra wait to ensure the server is fully initialized
                time.sleep(0.5)
                return True

        print(
            f"❌ Failed to start WebSocket server: port {config.WS_PORT} not open after waiting"
        )
        return False

    except Exception as e:
        print(f"❌ Error starting WebSocket server: {e}")
        return False


def main(cli_args=None):
    """
    Initialize and run the Force-Fusion dashboard application.

    This function:
    1. Processes CLI commands if provided
    2. Creates the QApplication
    3. Sets up the main window
    4. Creates the sensor provider
    5. Connects the dashboard controller
    6. Starts the event loop
    """
    # Process CLI commands if any
    exit_code = process_args(cli_args)
    if exit_code is not None:
        return exit_code

    # Start WebSocket server automatically when GUI is launched
    # We intentionally don't save the process handle since we want the server
    # to continue running independently after the GUI is closed
    server_running = start_websocket_server()

    # Wait a moment to ensure the server is ready
    if server_running:
        time.sleep(0.5)  # Give the server a little more time to initialize

    # Create and configure the application
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL, True)
    app = QApplication(sys.argv)
    app.setApplicationName("Force-Fusion")

    # Get version from pyproject.toml
    version = get_version()
    app.setApplicationVersion(version)

    # Print information about CSV logging
    print(f"\n📊 Vehicle data will be logged to: {os.path.abspath(config.CSV_PATH)}")

    # Load application stylesheet
    try:
        # Use a path relative to the module directory instead of execution directory
        module_dir = os.path.dirname(os.path.abspath(__file__))
        style_path = os.path.join(module_dir, "resources", "styles.qss")
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())
        print(f"✓ Loaded stylesheet from: {style_path}")
    except Exception as e:
        print(f"⚠️ Could not load stylesheet: {e}")

    # Create and show the main window
    main_window = MainWindow()

    # Print a more concise startup banner
    print("\n" + "=" * 50)
    print(f"🚀 FORCE-FUSION DASHBOARD v{app.applicationVersion()}")
    print(f"🔌 WebSocket URL: {config.WS_URI}")
    print("=" * 50)

    # Create sensor provider with WebSocket as the initial data source
    sensor_provider = SensorProvider(data_source="websocket")
    controller = DashboardController(main_window, sensor_provider)  # noqa: F841

    main_window.show()

    # Start the event loop
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
