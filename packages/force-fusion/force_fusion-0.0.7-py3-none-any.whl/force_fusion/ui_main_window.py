"""
Main window UI definition for Force-Fusion dashboard.
"""

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSizePolicy,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from force_fusion import config
from force_fusion.widgets.attitude import AttitudeWidget
from force_fusion.widgets.gg_diagram import GgDiagramWidget
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

        # Data Source Selector
        self.dataSourceFrame = QFrame()
        self.dataSourceLayout = QHBoxLayout(self.dataSourceFrame)
        self.dataSourceLayout.setContentsMargins(0, 0, 0, 5)

        # Data Source Label
        self.dataSourceLabel = QLabel("Data Source:")
        self.dataSourceLabel.setStyleSheet(
            f"color: {config.TEXT_COLOR}; font-weight: bold;"
        )

        # Data Source Selector ComboBox
        self.dataSourceComboBox = QComboBox()
        self.dataSourceComboBox.addItem("Simulated Data", "simulated")
        self.dataSourceComboBox.addItem("WebSocket", "websocket")

        # Set default selection
        index = self.dataSourceComboBox.findData(config.DEFAULT_DATA_SOURCE)
        if index >= 0:
            self.dataSourceComboBox.setCurrentIndex(index)

        # Connection Status Label
        self.connectionStatusLabel = QLabel("Connection: ")
        self.connectionStatusLabel.setStyleSheet(
            f"color: {config.TEXT_COLOR}; font-weight: bold;"
        )

        self.connectionStatusValue = QLabel("Inactive")
        self.connectionStatusValue.setStyleSheet(f"color: {config.WARNING_COLOR};")

        # Add widgets to data source layout
        self.dataSourceLayout.addWidget(self.dataSourceLabel)
        self.dataSourceLayout.addWidget(self.dataSourceComboBox)
        self.dataSourceLayout.addSpacing(20)
        self.dataSourceLayout.addWidget(self.connectionStatusLabel)
        self.dataSourceLayout.addWidget(self.connectionStatusValue)
        self.dataSourceLayout.addStretch(1)

        # Add data source frame to main layout
        self.mainLayout.addWidget(self.dataSourceFrame)

        # Top section - Horizontal layout for circular widgets
        self.topFrame = QFrame()
        self.topFrame.setFrameShape(QFrame.StyledPanel)
        self.topLayout = QVBoxLayout(self.topFrame)  # Changed to VBox to include titles
        self.topLayout.setContentsMargins(0, 0, 0, 0)
        self.topLayout.setSpacing(0)

        # Add a container for the title labels
        self.titleContainer = QWidget()
        self.titleLayout = QHBoxLayout(self.titleContainer)
        self.titleLayout.setContentsMargins(0, 0, 0, 5)  # Add margin at bottom

        # Add a container for the circular widgets
        self.circleContainer = QWidget()
        self.circleLayout = QHBoxLayout(self.circleContainer)
        self.circleLayout.setContentsMargins(0, 0, 0, 0)
        self.circleLayout.setSpacing(5)

        # Add the containers to the top layout
        self.topLayout.addWidget(self.titleContainer)
        self.topLayout.addWidget(self.circleContainer)

        # Bottom section - horizontal layout for tire forces and map
        self.bottomFrame = QFrame()
        self.bottomFrame.setFrameShape(QFrame.StyledPanel)
        self.bottomLayout = QHBoxLayout(self.bottomFrame)

        # Add frames to main layout
        self.mainLayout.addWidget(self.topFrame, 2)
        self.mainLayout.addWidget(self.bottomFrame, 3)

        # Status bar for additional information
        self.statusBar = QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Force-Fusion Dashboard Ready")

        # Reduce spacing and margins for more compact layout
        self.mainLayout.setContentsMargins(10, 5, 10, 10)
        self.mainLayout.setSpacing(5)

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
        self.ggDiagramWidget = GgDiagramWidget()

        # Set size policies for consistent sizing
        for widget in [
            self.minimapWidget,
            self.speedometerWidget,
            self.attitudeWidget,
            self.ggDiagramWidget,
        ]:
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            widget.setMinimumSize(QSize(200, 200))

        # Create title labels
        self.minimapTitle = QLabel("Minimap")
        self.speedometerTitle = QLabel("Speedometer")
        self.attitudeTitle = QLabel("Attitude")
        self.ggDiagramTitle = QLabel("G-G Diagram")

        # Set styles for title labels
        title_style = f"color: {config.TEXT_COLOR}; font-family: Arial; font-size: 12px; font-weight: bold;"
        for label in [
            self.minimapTitle,
            self.speedometerTitle,
            self.attitudeTitle,
            self.ggDiagramTitle,
        ]:
            label.setStyleSheet(title_style)
            label.setAlignment(Qt.AlignCenter)

        # Add title labels to the title layout
        self.titleLayout.addWidget(self.minimapTitle)
        self.titleLayout.addWidget(self.speedometerTitle)
        self.titleLayout.addWidget(self.attitudeTitle)
        self.titleLayout.addWidget(self.ggDiagramTitle)

        # Add widgets to the circle layout
        self.circleLayout.addWidget(self.minimapWidget)
        self.circleLayout.addWidget(self.speedometerWidget)
        self.circleLayout.addWidget(self.attitudeWidget)
        self.circleLayout.addWidget(self.ggDiagramWidget)

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

        # Style the status bar
        self.statusBar.setStyleSheet(
            f"background-color: {config.BACKGROUND_COLOR}; color: {config.TEXT_COLOR};"
        )

        # Style the data source selector
        self.dataSourceComboBox.setStyleSheet(
            f"background-color: {config.BEZEL_COLOR}; color: {config.TEXT_COLOR}; padding: 3px;"
        )


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
        self.gg_diagram = self.ui.ggDiagramWidget
        self.tire_forces = {
            "FL": self.ui.tireForceFrontLeft,
            "FR": self.ui.tireForceFrontRight,
            "RL": self.ui.tireForceRearLeft,
            "RR": self.ui.tireForceRearRight,
        }
        self.mapbox = self.ui.mapboxView
        self.data_source_selector = self.ui.dataSourceComboBox
        self.connection_status_label = self.ui.connectionStatusValue
        self.status_bar = self.ui.statusBar

    def update_connection_status(self, status, message=""):
        """Update the connection status display."""
        self.connection_status_label.setText(status)

        # Set color based on status
        if status == "Active":
            self.connection_status_label.setStyleSheet(
                f"color: {config.SUCCESS_COLOR};"
            )
            # Update the status bar when connection is active
            if message and "WebSocket" in message:
                self.status_bar.showMessage("WebSocket Connected")
            elif message:
                self.status_bar.showMessage(message)
        elif status == "Connecting" or status == "Reconnecting":
            self.connection_status_label.setStyleSheet(
                f"color: {config.WARNING_COLOR};"
            )
            # Update status bar when connecting
            self.status_bar.showMessage(
                f"Connecting to {message} - Run 'python src/force_fusion/utils/websocket_client_test.py' to send test data"
            )
        elif status == "Inactive":
            self.connection_status_label.setStyleSheet(f"color: {config.TEXT_COLOR};")
            # Update status bar when inactive
            self.status_bar.showMessage(
                "Connection Inactive - Run 'python src/force_fusion/utils/websocket_client_test.py' to send test data"
            )
        elif status == "Error":
            self.connection_status_label.setStyleSheet(f"color: {config.DANGER_COLOR};")
            # Update status bar with error message
            self.status_bar.showMessage(f"Error: {message}")

        # Always show message in status bar if provided
        if message:
            if (
                status == "Connecting"
                or status == "Reconnecting"
                or status == "Inactive"
            ):
                self.status_bar.showMessage(
                    f"{message} - Run 'python src/force_fusion/utils/websocket_client_test.py' to send test data"
                )
            else:
                self.status_bar.showMessage(message)
