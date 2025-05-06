"""
This module provides basic testing functionality for Force Fusion components.
It creates simple test windows for each widget with simulated data.
"""

import math
import os
import random
import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Imported config from force_fusion
from force_fusion import config
from force_fusion.widgets.attitude import AttitudeWidget
from force_fusion.widgets.gg_diagram import GgDiagramWidget
from force_fusion.widgets.heading import HeadingWidget
from force_fusion.widgets.mapbox_view import MapboxView
from force_fusion.widgets.minimap import MinimapWidget
from force_fusion.widgets.speedometer import SpeedometerWidget
from force_fusion.widgets.tire_force import TireForceWidget


class TestWindow(QMainWindow):
    """Test window for individual widgets."""

    def __init__(self, widget, widget_name):
        """Initialize the test window with a widget."""
        super().__init__()

        self.setWindowTitle(f"Test: {widget_name}")
        self.setGeometry(100, 100, 400, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        # Add the widget to test
        self.widget = widget
        self.layout.addWidget(self.widget)

        # Add control buttons
        self.buttons_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Test")
        self.stop_button = QPushButton("Stop Test")
        self.buttons_layout.addWidget(self.start_button)
        self.buttons_layout.addWidget(self.stop_button)
        self.layout.addLayout(self.buttons_layout)

        # Connect signals
        self.start_button.clicked.connect(self.start_test)
        self.stop_button.clicked.connect(self.stop_test)
        self.stop_button.setEnabled(False)

        # Timer for animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)

        # Test data
        self.test_data = {
            "counter": 0,
            "latitude": config.DEFAULT_CENTER[1],  # Use config default
            "longitude": config.DEFAULT_CENTER[0],  # Use config default
            "speed": 0.0,
            "acceleration": 0.0,
            "pitch": 0.0,
            "roll": 0.0,
            "heading": 0.0,
            "forces": {
                "FL": config.TIRE_FORCE_NORMAL,
                "FR": config.TIRE_FORCE_NORMAL,
                "RL": config.TIRE_FORCE_NORMAL,
                "RR": config.TIRE_FORCE_NORMAL,
            },
            "lateral_acceleration": 0.0,  # Added for GG diagram
        }

    def start_test(self):
        """Start the animation test."""
        self.timer.start(config.SPEED_UPDATE_INTERVAL)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_test(self):
        """Stop the animation test."""
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_data(self):
        """Update the test data and widget."""
        # Update counter
        self.test_data["counter"] += 1
        counter = self.test_data["counter"]

        # Generate test data
        self.test_data["speed"] = 50 + 30 * math.sin(counter * 0.05)
        self.test_data["acceleration"] = 3 * math.cos(counter * 0.05)
        self.test_data["heading"] = (counter * 2) % 360
        self.test_data["pitch"] = 10 * math.sin(counter * 0.1)
        self.test_data["roll"] = 15 * math.cos(counter * 0.08)

        # Add lateral acceleration values (for GG diagram)
        self.test_data["lateral_acceleration"] = 2 * math.sin(counter * 0.07)

        # Update position based on heading and speed
        speed_ms = self.test_data["speed"] / 3.6  # km/h to m/s
        update_interval_sec = config.SPEED_UPDATE_INTERVAL / 1000.0
        distance = speed_ms * update_interval_sec  # distance based on timer interval
        heading_rad = math.radians(self.test_data["heading"])

        # Simple movement calculation (approximation)
        # Meters per degree latitude is relatively constant
        meters_per_degree_lat = 111000
        # Meters per degree longitude varies with latitude
        meters_per_degree_lon = 111000 * math.cos(
            math.radians(self.test_data["latitude"])
        )

        # Avoid division by zero if at poles, though unlikely
        if meters_per_degree_lon == 0:
            meters_per_degree_lon = 0.001

        lat_change = distance * math.cos(heading_rad) / meters_per_degree_lat
        lon_change = distance * math.sin(heading_rad) / meters_per_degree_lon

        self.test_data["latitude"] += lat_change
        self.test_data["longitude"] += lon_change

        # Update tire forces with some randomness and weight transfer effects
        lat_transfer = self.test_data["roll"] * 20
        long_transfer = self.test_data["acceleration"] * 100

        self.test_data["forces"]["FL"] = (
            config.TIRE_FORCE_NORMAL
            - long_transfer
            + lat_transfer
            + random.uniform(-50, 50)
        )
        self.test_data["forces"]["FR"] = (
            config.TIRE_FORCE_NORMAL
            - long_transfer
            - lat_transfer
            + random.uniform(-50, 50)
        )
        self.test_data["forces"]["RL"] = (
            config.TIRE_FORCE_NORMAL
            + long_transfer
            + lat_transfer
            + random.uniform(-50, 50)
        )
        self.test_data["forces"]["RR"] = (
            config.TIRE_FORCE_NORMAL
            + long_transfer
            - lat_transfer
            + random.uniform(-50, 50)
        )

        # Ensure forces are within limits
        for key in self.test_data["forces"]:
            self.test_data["forces"][key] = max(
                500, min(config.TIRE_FORCE_MAX, self.test_data["forces"][key])
            )

        # Update widget based on type
        if isinstance(self.widget, MinimapWidget):
            self.widget.update_position(
                self.test_data["latitude"], self.test_data["longitude"]
            )

        elif isinstance(self.widget, SpeedometerWidget):
            self.widget.update_speed(self.test_data["speed"])
            self.widget.update_acceleration(self.test_data["acceleration"])

        elif isinstance(self.widget, AttitudeWidget):
            self.widget.set_pitch(self.test_data["pitch"])
            self.widget.set_roll(self.test_data["roll"])

        elif isinstance(self.widget, HeadingWidget):
            self.widget.set_heading(self.test_data["heading"])

        elif isinstance(self.widget, TireForceWidget):
            position = self.widget._position
            self.widget.set_force(self.test_data["forces"][position])

        elif isinstance(self.widget, MapboxView):
            self.widget.update_pose(
                self.test_data["latitude"],
                self.test_data["longitude"],
                self.test_data["heading"],
                self.test_data["pitch"],
                self.test_data["roll"],
            )

        elif isinstance(self.widget, GgDiagramWidget):
            # Convert m/s² to G (1G ≈ 9.81 m/s²)
            longit_g = self.test_data["acceleration"] / 9.81
            lateral_g = self.test_data["lateral_acceleration"] / 9.81
            self.widget.setAccel(longit_g, lateral_g)


def test_minimap():
    """Test the minimap widget."""
    app = QApplication(sys.argv)
    window = TestWindow(MinimapWidget(), "Minimap Widget")
    window.show()
    sys.exit(app.exec_())


def test_speedometer():
    """Test the speedometer widget."""
    app = QApplication(sys.argv)
    window = TestWindow(SpeedometerWidget(), "Speedometer Widget")
    window.show()
    sys.exit(app.exec_())


def test_attitude():
    """Test the attitude widget."""
    app = QApplication(sys.argv)
    window = TestWindow(AttitudeWidget(), "Attitude Widget")
    window.show()
    sys.exit(app.exec_())


def test_heading():
    """Test the heading widget."""
    app = QApplication(sys.argv)
    window = TestWindow(HeadingWidget(), "Heading Widget")
    window.show()
    sys.exit(app.exec_())


def test_gg_diagram():
    """Test the GG diagram widget."""
    app = QApplication(sys.argv)
    window = TestWindow(GgDiagramWidget(), "GG Diagram Widget")
    window.show()
    sys.exit(app.exec_())


def test_tire_force():
    """Test the tire force widget."""
    app = QApplication(sys.argv)
    layout = QWidget()
    main_layout = QVBoxLayout(
        layout
    )  # Changed from QHBoxLayout to QVBoxLayout for better spacing

    # Add a title with margin
    title_layout = QVBoxLayout()
    title_layout.addSpacing(20)  # Add space above the grid
    main_layout.addLayout(title_layout)

    # Create four tire force widgets
    fl_widget = TireForceWidget("FL")
    fr_widget = TireForceWidget("FR")
    rl_widget = TireForceWidget("RL")
    rr_widget = TireForceWidget("RR")

    # Add them to a grid layout
    grid_layout = QVBoxLayout()
    grid_layout.addSpacing(20)  # Add spacing between title and widgets
    row1 = QHBoxLayout()
    row2 = QHBoxLayout()

    row1.addWidget(fl_widget)
    row1.addWidget(fr_widget)
    row2.addWidget(rl_widget)
    row2.addWidget(rr_widget)

    grid_layout.addLayout(row1)
    grid_layout.addLayout(row2)

    main_layout.addLayout(grid_layout)

    window = QMainWindow()
    window.setWindowTitle("Test: Tire Force Widgets")
    window.setCentralWidget(layout)
    window.setGeometry(100, 100, 600, 400)

    # Create and connect a timer for animation
    timer = QTimer(window)

    # Test data
    test_data = {
        "counter": 0,
        "forces": {"FL": 0.0, "FR": 0.0, "RL": 0.0, "RR": 0.0},  # Start all at 0
        "phase_offsets": {"FL": 0, "FR": 25, "RL": 50, "RR": 75},  # Offset percentages
    }

    def update_data():
        """Update force values in a clear cycle from 0 to max and back to 0"""
        test_data["counter"] += 1
        counter = test_data["counter"]

        # Maximum force and cycle period
        max_force = config.TIRE_FORCE_MAX  # Maximum force in Newtons
        cycle_period = 300  # Total cycle time (3 seconds at 100ms timer)

        # Update each tire with proper phase offset
        for position in ["FL", "FR", "RL", "RR"]:
            # Apply phase offset for each tire
            offset = test_data["phase_offsets"][position]
            adjusted_counter = (counter + offset * cycle_period / 100) % cycle_period

            # First half of cycle: 0 to max force (monotonically increasing)
            if adjusted_counter < cycle_period / 2:
                ratio = adjusted_counter / (cycle_period / 2)
                test_data["forces"][position] = ratio * max_force
            # Second half of cycle: max force to 0 (monotonically decreasing)
            else:
                ratio = (adjusted_counter - cycle_period / 2) / (cycle_period / 2)
                test_data["forces"][position] = (1 - ratio) * max_force

        # Print the current forces to verify
        # print(
        #     f"Forces: FL={test_data['forces']['FL']:.0f}N, "
        #     + f"FR={test_data['forces']['FR']:.0f}N, "
        #     + f"RL={test_data['forces']['RL']:.0f}N, "
        #     + f"RR={test_data['forces']['RR']:.0f}N"
        # )

        # Update widgets with calculated forces
        fl_widget.set_force(test_data["forces"]["FL"])
        fr_widget.set_force(test_data["forces"]["FR"])
        rl_widget.set_force(test_data["forces"]["RL"])
        rr_widget.set_force(test_data["forces"]["RR"])

    timer.timeout.connect(update_data)
    timer.start(config.SPEED_UPDATE_INTERVAL)

    window.show()
    sys.exit(app.exec_())


def test_mapbox():
    """Test the mapbox widget."""
    # Disable GPU acceleration for WebEngine to avoid EGL errors on some systems
    # Must be done before QApplication is initialized
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu"
    print("Attempting to disable GPU acceleration for Mapbox test...")

    app = QApplication(sys.argv)
    window = TestWindow(MapboxView(), "Mapbox View")
    window.show()
    sys.exit(app.exec_())


def test_all():
    """Test all widgets together (main dashboard)."""
    # Disable GPU acceleration for WebEngine if MapboxView is included
    # Should be done before QApplication for safety
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu"
    print("Attempting to disable GPU acceleration for full dashboard test...")

    # Don't import main - this causes a circular dependency
    app = QApplication(sys.argv)

    # Create the main window with all widgets
    from force_fusion.controller import DashboardController
    from force_fusion.sensors import SensorProvider
    from force_fusion.ui_main_window import MainWindow

    main_window = MainWindow()
    sensor_provider = SensorProvider(data_source="simulated")
    controller = DashboardController(main_window, sensor_provider)  # noqa: F841

    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    # Make sure os is imported if we need it here or in called functions
    import os

    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name == "minimap":
            test_minimap()
        elif test_name == "speedometer":
            test_speedometer()
        elif test_name == "attitude":
            test_attitude()
        elif test_name == "heading":
            test_heading()
        elif test_name == "tire_force":
            test_tire_force()
        elif test_name == "mapbox":
            test_mapbox()
        elif test_name == "gg_diagram":
            test_gg_diagram()
        else:
            # Default to testing all if argument is unknown
            print(f"Unknown test '{test_name}', running 'all' instead.")
            test_all()
    else:
        test_all()
