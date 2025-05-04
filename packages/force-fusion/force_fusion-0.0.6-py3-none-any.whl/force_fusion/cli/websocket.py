"""
CLI command to start the WebSocket server.
"""

import subprocess
import sys


def setup_parser(subparsers):
    """
    Set up the parser for the WebSocket server command.

    Args:
        subparsers: The subparsers object to add to
    """
    parser = subparsers.add_parser("websocket", help="Start the WebSocket server")
    parser.add_argument(
        "--host",
        type=str,
        help="Host to bind the WebSocket server to",
    )
    parser.add_argument(
        "--port",
        type=int,
        help="Port to bind the WebSocket server to",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Enable test mode (broadcasts test data at 10Hz)",
    )


def run_websocket_command(args):
    """
    Run the WebSocket server command.

    Args:
        args: Command line arguments

    Returns:
        int: Exit code
    """
    # Start both the server and the GUI
    return start_websocket_server_and_gui(args)


def start_websocket_server_and_gui(args):
    """
    Start the WebSocket server and the GUI application.

    Args:
        args: Command line arguments

    Returns:
        int: Exit code
    """
    import time

    try:
        print("Starting WebSocket server with test mode...")

        # Build the command for WebSocket server
        server_cmd = [sys.executable, "-m", "force_fusion.utils.websocket_server"]

        # Add host and port if provided
        if args.host:
            server_cmd.extend(["--host", args.host])
        if args.port:
            server_cmd.extend(["--port", str(args.port)])
        # Add test flag if provided
        if args.test:
            server_cmd.append("--test")
            print("Test mode enabled: Server will broadcast test data at 10Hz")

        # Start the server process detached
        subprocess.Popen(server_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        print("WebSocket server started.")

        # Let the server start up
        time.sleep(2)

        # Now start the main app directly, without importing and rerunning the CLI code
        print("Starting GUI application directly...")

        # Import necessary components directly
        from PyQt5.QtWidgets import QApplication

        from force_fusion import config
        from force_fusion.controller import DashboardController
        from force_fusion.sensors import SensorProvider
        from force_fusion.ui_main_window import MainWindow

        # Update the config with the custom host/port if provided
        if args.host:
            config.WS_HOST = args.host
        if args.port:
            config.WS_PORT = args.port
            # Update the full URI as well
            config.WS_URI = f"ws://{config.WS_HOST}:{config.WS_PORT}"
            print(f"Updated WebSocket URI for GUI: {config.WS_URI}")

        # Create the Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("Force-Fusion")

        # Create the main window and controller
        main_window = MainWindow()
        sensor_provider = SensorProvider(data_source="websocket")
        controller = DashboardController(main_window, sensor_provider)  # noqa: F841

        # Show the window
        main_window.show()

        # Run the event loop
        return app.exec_()

    except KeyboardInterrupt:
        print("\nApplication stopped.")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1
