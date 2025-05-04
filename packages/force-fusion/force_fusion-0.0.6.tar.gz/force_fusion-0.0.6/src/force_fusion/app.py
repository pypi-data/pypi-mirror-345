"""
Main application entry point for Force-Fusion dashboard.
"""

import os
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


def is_port_in_use(port, host="localhost"):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex((host, port)) == 0


def start_websocket_server():
    """Start the WebSocket server as a background process."""
    try:
        print("Starting WebSocket server automatically...")

        # Check if a server is already running on this port
        if is_port_in_use(config.WS_PORT):
            print(f"WebSocket server already running on port {config.WS_PORT}")
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
        print("Waiting for WebSocket server to start...")
        max_attempts = 20  # Wait up to 4 seconds (20 * 0.2)
        for attempt in range(max_attempts):
            time.sleep(0.2)
            if is_port_in_use(config.WS_PORT):
                print(f"WebSocket server started successfully on port {config.WS_PORT}")
                # Extra wait to ensure the server is fully initialized
                time.sleep(0.5)
                return True

        print(
            f"Failed to start WebSocket server: port {config.WS_PORT} not open after waiting"
        )
        return False

    except Exception as e:
        print(f"Error starting WebSocket server: {e}")
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
    app.setApplicationVersion("0.1.0")

    # Print information about CSV logging
    print(f"\nVehicle data will be logged to: {os.path.abspath(config.CSV_PATH)}")

    # Load application stylesheet
    try:
        with open("src/force_fusion/resources/styles.qss", "r") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"Warning: Could not load stylesheet: {e}")

    # Create and show the main window
    main_window = MainWindow()

    # Explicitly set WebSocket as the data source
    print("\n### FORCE-FUSION DASHBOARD STARTUP ###")
    print(f"WebSocket server URL: {config.WS_URI}")
    print("Starting with 'websocket' data source")

    sensor_provider = SensorProvider(
        data_source="websocket"
    )  # Start with WebSocket mode
    controller = DashboardController(main_window, sensor_provider)  # noqa: F841

    # Verify data source is set
    print(f"Data source active: {sensor_provider.data_source}")
    print("### END STARTUP ###\n")

    main_window.show()

    # Start the event loop
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
