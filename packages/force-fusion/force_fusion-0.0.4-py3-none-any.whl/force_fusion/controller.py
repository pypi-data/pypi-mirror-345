"""
Controller class for wiring sensor signals to dashboard widgets.
"""

from PyQt5.QtCore import QObject

from force_fusion import config


class DashboardController(QObject):
    """
    Connects sensor provider signals to dashboard widgets.

    Responsible for:
    - Wiring signals to widget update methods
    - Converting units as needed
    - Applying smoothing and filtering
    - Throttling update rates for performance
    """

    def __init__(self, main_window, sensor_provider):
        """
        Initialize the dashboard controller.

        Args:
            main_window: MainWindow instance containing dashboard widgets
            sensor_provider: SensorProvider instance emitting data signals
        """
        super().__init__()

        self.main_window = main_window
        self.sensor_provider = sensor_provider

        # Connect signals to widget update methods
        self._connect_signals()

        # Set up moving averages for smoothing
        self._speed_history = []
        self._accel_history = []
        self._position_history = []
        self._MAX_HISTORY = 10

        # Flag to accumulate position history for the minimap
        self._record_trajectory = True

        # Start the sensor provider
        self.sensor_provider.start()

    def _connect_signals(self):
        """Connect sensor signals to widget update methods."""
        # Connect position signals
        self.sensor_provider.position_changed.connect(self._on_position_changed)

        # Connect speed signals
        self.sensor_provider.speed_changed.connect(self._on_speed_changed)
        self.sensor_provider.acceleration_changed.connect(self._on_acceleration_changed)

        # Connect attitude signals
        self.sensor_provider.pitch_changed.connect(self._on_pitch_changed)
        self.sensor_provider.roll_changed.connect(self._on_roll_changed)
        self.sensor_provider.heading_changed.connect(self._on_heading_changed)

        # Connect tire force signals
        self.sensor_provider.tire_forces_changed.connect(self._on_tire_forces_changed)

    def _on_position_changed(self, latitude, longitude):
        """
        Process position updates.

        Args:
            latitude: Latitude in degrees
            longitude: Longitude in degrees
        """
        # Update the minimap
        self.main_window.minimap.update_position(latitude, longitude)

        # Update the Mapbox view
        self.main_window.mapbox.update_position(latitude, longitude)

        # Add to position history (used for trajectory)
        if self._record_trajectory:
            self._position_history.append((latitude, longitude))
            # Limit the size of the history
            if len(self._position_history) > config.TRAJECTORY_HISTORY_LENGTH:
                self._position_history.pop(0)

    def _on_speed_changed(self, speed):
        """
        Process speed updates.

        Args:
            speed: Speed in km/h
        """
        # Apply moving average for smoothing
        self._speed_history.append(speed)
        if len(self._speed_history) > self._MAX_HISTORY:
            self._speed_history.pop(0)

        smooth_speed = sum(self._speed_history) / len(self._speed_history)

        # Update the speedometer
        self.main_window.speedometer.update_speed(smooth_speed)

    def _on_acceleration_changed(self, acceleration):
        """
        Process acceleration updates.

        Args:
            acceleration: Acceleration in m/s²
        """
        # Apply moving average for smoothing
        self._accel_history.append(acceleration)
        if len(self._accel_history) > self._MAX_HISTORY:
            self._accel_history.pop(0)

        smooth_accel = sum(self._accel_history) / len(self._accel_history)

        # Update the speedometer's acceleration display
        self.main_window.speedometer.update_acceleration(smooth_accel)

    def _on_pitch_changed(self, pitch):
        """
        Process pitch updates.

        Args:
            pitch: Pitch angle in degrees
        """
        # Update the attitude indicator
        self.main_window.attitude.set_pitch(pitch)

        # Update the Mapbox view
        self.main_window.mapbox.update_pitch(pitch)

    def _on_roll_changed(self, roll):
        """
        Process roll updates.

        Args:
            roll: Roll angle in degrees
        """
        # Update the attitude indicator
        self.main_window.attitude.set_roll(roll)

        # Update the Mapbox view
        self.main_window.mapbox.update_roll(roll)

    def _on_heading_changed(self, heading):
        """
        Process heading updates.

        Args:
            heading: Heading in degrees (0-360)
        """
        # Update the heading indicator
        self.main_window.heading.set_heading(heading)

        # Update the Mapbox view
        self.main_window.mapbox.update_heading(heading)

    def _on_tire_forces_changed(self, forces):
        """
        Process tire force updates.

        Args:
            forces: Dictionary with keys 'FL', 'FR', 'RL', 'RR' and force values in N
        """
        # Update each tire force widget
        for position, force in forces.items():
            if position in self.main_window.tire_forces:
                self.main_window.tire_forces[position].set_force(force)

    def start_recording(self):
        """Start recording trajectory data."""
        self._record_trajectory = True

    def stop_recording(self):
        """Stop recording trajectory data."""
        self._record_trajectory = False

    def clear_trajectory(self):
        """Clear the trajectory history."""
        self._position_history = []
        self.main_window.minimap.clear_trajectory()

    def set_update_rate(self, widget_type, rate_ms):
        """
        Set the update rate for a specific widget type.

        Args:
            widget_type: String identifying the widget type
            rate_ms: Update rate in milliseconds
        """
        # Implementation depends on specific widget requirements
        pass
