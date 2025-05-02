"""
Main application entry point for Force-Fusion dashboard.
"""

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from force_fusion.controller import DashboardController
from force_fusion.sensors import SensorProvider
from force_fusion.ui_main_window import MainWindow


def main():
    """
    Initialize and run the Force-Fusion dashboard application.

    This function:
    1. Creates the QApplication
    2. Sets up the main window
    3. Creates the sensor provider
    4. Connects the dashboard controller
    5. Starts the event loop
    """
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Try using software OpenGL to avoid WebGL/GPU context issues
    QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL, True)

    # Create the application
    app = QApplication(sys.argv)
    app.setApplicationName("Force-Fusion")
    app.setApplicationVersion("0.1.0")

    # Load application stylesheet
    try:
        with open("src/force_fusion/resources/styles.qss", "r") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"Warning: Could not load stylesheet: {e}")

    # Create the main window
    main_window = MainWindow()

    # Create the sensor provider
    sensor_provider = SensorProvider(data_source="simulated")

    # Create the dashboard controller
    controller = DashboardController(main_window, sensor_provider)  # noqa: F841

    # Show the main window
    main_window.show()

    # Start the event loop
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
