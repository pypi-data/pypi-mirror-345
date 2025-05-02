"""
Main window UI definition for Force-Fusion dashboard.
"""

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QMainWindow,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from force_fusion import config
from force_fusion.widgets.attitude import AttitudeWidget
from force_fusion.widgets.heading import HeadingWidget
from force_fusion.widgets.mapbox_view import MapboxView
from force_fusion.widgets.minimap import MinimapWidget
from force_fusion.widgets.speedometer import SpeedometerWidget
from force_fusion.widgets.tire_force import TireForceWidget


class Ui_MainWindow:
    """Main window UI definition for Force-Fusion dashboard."""

    def setupUi(self, MainWindow):
        """Set up the UI components for the main window."""
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 800)
        MainWindow.setWindowTitle("Force-Fusion Dashboard")

        # Set up central widget
        self.centralWidget = QWidget(MainWindow)
        MainWindow.setCentralWidget(self.centralWidget)

        # Main layout is vertical
        self.mainLayout = QVBoxLayout(self.centralWidget)
        self.mainLayout.setContentsMargins(10, 5, 10, 10)
        self.mainLayout.setSpacing(5)

        # Top section - Horizontal layout for circular widgets
        self.topFrame = QFrame()
        self.topFrame.setFrameShape(QFrame.StyledPanel)
        self.topLayout = QHBoxLayout(self.topFrame)

        # Bottom section - horizontal layout for tire forces and map
        self.bottomFrame = QFrame()
        self.bottomFrame.setFrameShape(QFrame.StyledPanel)
        self.bottomLayout = QHBoxLayout(self.bottomFrame)

        # Add frames to main layout
        self.mainLayout.addWidget(self.topFrame, 2)
        self.mainLayout.addWidget(self.bottomFrame, 3)

        # Reduce spacing and margins for more compact layout
        self.mainLayout.setContentsMargins(10, 5, 10, 10)
        self.mainLayout.setSpacing(5)

        # Add margin between title and widgets in the top row
        self.topLayout.setContentsMargins(0, 20, 0, 0)
        self.topLayout.setSpacing(5)

        # Create widgets
        self.setupTopWidgets()
        self.setupBottomWidgets()

        # Set styles
        self.applyStyles()

    def setupTopWidgets(self):
        """Create and place the four circular widgets in the top grid."""
        # Create circular widgets with fixed size policy
        self.minimapWidget = MinimapWidget()
        self.speedometerWidget = SpeedometerWidget()
        self.attitudeWidget = AttitudeWidget()
        self.headingWidget = HeadingWidget()

        # Set size policies for consistent sizing
        for widget in [
            self.minimapWidget,
            self.speedometerWidget,
            self.attitudeWidget,
            self.headingWidget,
        ]:
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            widget.setMinimumSize(QSize(200, 200))

        # Add widgets to horizontal layout (order: Minimap, Speedometer, Attitude, Heading)
        self.topLayout.addWidget(self.minimapWidget)
        self.topLayout.addWidget(self.speedometerWidget)
        self.topLayout.addWidget(self.attitudeWidget)
        self.topLayout.addWidget(self.headingWidget)

    def setupBottomWidgets(self):
        """Create and place the tire force widgets and mapbox view."""
        # Left side for tire forces in a 2x2 grid
        self.tireForceFrame = QFrame()
        self.tireForceLayout = QGridLayout(self.tireForceFrame)

        # Create tire force widgets
        self.tireForceFrontLeft = TireForceWidget("FL")
        self.tireForceFrontRight = TireForceWidget("FR")
        self.tireForceRearLeft = TireForceWidget("RL")
        self.tireForceRearRight = TireForceWidget("RR")

        # Set size policies
        for widget in [
            self.tireForceFrontLeft,
            self.tireForceFrontRight,
            self.tireForceRearLeft,
            self.tireForceRearRight,
        ]:
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            widget.setMinimumSize(QSize(150, 150))

        # Add tire force widgets to grid
        self.tireForceLayout.addWidget(self.tireForceFrontLeft, 0, 0)
        self.tireForceLayout.addWidget(self.tireForceFrontRight, 0, 1)
        self.tireForceLayout.addWidget(self.tireForceRearLeft, 1, 0)
        self.tireForceLayout.addWidget(self.tireForceRearRight, 1, 1)

        # Right side for Mapbox view and GPS/time info
        self.mapFrame = QFrame()
        self.mapLayout = QVBoxLayout(self.mapFrame)

        # Create Mapbox view
        self.mapboxView = MapboxView()
        self.mapboxView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add map to map layout
        self.mapLayout.addWidget(self.mapboxView)

        # Add frames to bottom layout
        self.bottomLayout.addWidget(self.tireForceFrame, 1)
        self.bottomLayout.addWidget(self.mapFrame, 2)

    def applyStyles(self):
        """Apply QSS styles to widgets."""
        # Set background color for the main window
        self.centralWidget.setStyleSheet(
            f"background-color: {config.BACKGROUND_COLOR};"
        )

        # Style frames
        for frame in [
            self.topFrame,
            self.bottomFrame,
            self.tireForceFrame,
            self.mapFrame,
        ]:
            frame.setStyleSheet("border: none;")


class MainWindow(QMainWindow):
    """Main application window containing all dashboard widgets."""

    def __init__(self):
        """Initialize the main window and set up the UI."""
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Store widget references for easier access from controller
        self.minimap = self.ui.minimapWidget
        self.speedometer = self.ui.speedometerWidget
        self.attitude = self.ui.attitudeWidget
        self.heading = self.ui.headingWidget
        self.tire_forces = {
            "FL": self.ui.tireForceFrontLeft,
            "FR": self.ui.tireForceFrontRight,
            "RL": self.ui.tireForceRearLeft,
            "RR": self.ui.tireForceRearRight,
        }
        self.mapbox = self.ui.mapboxView
