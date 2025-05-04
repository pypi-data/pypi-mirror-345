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
        self._lateral_accel_history = []  # New for lateral acceleration
        self._position_history = []
        self._MAX_HISTORY = 2  # Reduced for less smoothing lag

        # Flag to accumulate position history for the minimap
        self._record_trajectory = True

        # Configure GG diagram update interval
        if hasattr(self.main_window, "gg_diagram") and hasattr(
            self.main_window.gg_diagram, "set_update_interval"
        ):
            self.main_window.gg_diagram.set_update_interval(
                config.GG_DIAGRAM_UPDATE_INTERVAL
            )

        # Connect UI data source selector to data source change logic
        self.main_window.data_source_selector.currentIndexChanged.connect(
            self._on_data_source_changed
        )

        # Start the sensor provider
        self.sensor_provider.start()

        # Force an immediate update when starting
        self._force_initial_update()

    def _connect_signals(self):
        """Connect sensor signals to widget update methods."""
        if config.DEBUG_MODE:
            print("\nCONNECTING SIGNALS FROM SENSOR PROVIDER TO WIDGETS")

        # Connect position signals
        self.sensor_provider.position_changed.connect(self._on_position_changed)
        if config.DEBUG_MODE:
            print("✓ Connected position signals")

        # Connect speed signals
        self.sensor_provider.speed_changed.connect(self._on_speed_changed)
        self.sensor_provider.acceleration_changed.connect(self._on_acceleration_changed)
        if config.DEBUG_MODE:
            print("✓ Connected speed and acceleration signals")

        # Connect lateral acceleration signal
        self.sensor_provider.lateral_accel_changed.connect(
            self._on_lateral_accel_changed
        )
        if config.DEBUG_MODE:
            print("✓ Connected lateral acceleration signals")

        # Connect attitude signals
        self.sensor_provider.pitch_changed.connect(self._on_pitch_changed)
        self.sensor_provider.roll_changed.connect(self._on_roll_changed)
        if config.DEBUG_MODE:
            print("✓ Connected attitude signals")

        # Connect heading for the mapbox view only
        self.sensor_provider.heading_changed.connect(self._on_heading_changed)
        if config.DEBUG_MODE:
            print("✓ Connected heading signals")

        # Connect tire force signals
        self.sensor_provider.tire_forces_changed.connect(self._on_tire_forces_changed)
        if config.DEBUG_MODE:
            print("✓ Connected tire force signals")

        # Connect time signals
        self.sensor_provider.current_time_changed.connect(self._on_current_time_changed)
        self.sensor_provider.elapsed_time_changed.connect(self._on_elapsed_time_changed)
        if config.DEBUG_MODE:
            print("✓ Connected time signals")

        # Connect connection status signal
        self.sensor_provider.connection_status_changed.connect(
            self._on_connection_status_changed
        )
        if config.DEBUG_MODE:
            print("✓ Connected status signals")
            print("ALL SIGNALS CONNECTED SUCCESSFULLY\n")

    def _on_data_source_changed(self, index):
        """
        Handle data source changed in the UI.

        Args:
            index: Current index of the data source selector combobox
        """
        # Get the data source ID from the combo box
        data_source = self.main_window.data_source_selector.itemData(index)

        # Print debugging information
        print(f"Data source changed to: {data_source} (index: {index})")
        print(
            f"Available data sources: {[self.main_window.data_source_selector.itemData(i) for i in range(self.main_window.data_source_selector.count())]}"
        )

        # Update the sensor provider's data source
        if data_source:
            print(f"Setting sensor provider data source to: {data_source}")

            # Clear old status first
            if data_source == "simulated":
                # Update status bar immediately when switching to simulated data
                self.main_window.status_bar.showMessage("Using Simulated Data")
            elif data_source == "websocket":
                # When switching to WebSocket, initially show connecting status
                self.main_window.status_bar.showMessage(
                    "Connecting to WebSocket server..."
                )

            # Now change the data source
            self.sensor_provider.set_data_source(data_source)
        else:
            print("Warning: No data source selected")

    def _on_connection_status_changed(self, status, message):
        """
        Update connection status in the UI.

        Args:
            status: Connection status ("Active", "Connecting", "Error", etc.)
            message: Detailed status message
        """
        # Update the UI to show connection status
        self.main_window.update_connection_status(status, message)

    def _on_current_time_changed(self, time_str):
        """
        Process current time updates.

        Args:
            time_str: Formatted time string
        """
        # Update time display in the UI if needed
        if hasattr(self.main_window.mapbox, "update_time"):
            self.main_window.mapbox.update_time(time_str)

    def _on_elapsed_time_changed(self, elapsed_str):
        """
        Process elapsed time updates.

        Args:
            elapsed_str: Formatted elapsed time string
        """
        # Update elapsed time display in the UI if needed
        if hasattr(self.main_window.mapbox, "update_elapsed_time"):
            self.main_window.mapbox.update_elapsed_time(elapsed_str)

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

    def _on_speed_changed(self, speed):
        """
        Process speed updates.

        Args:
            speed: Speed in km/h
        """
        # For WebSocket data, update immediately without smoothing
        if self.sensor_provider.data_source == "websocket":
            self.main_window.speedometer.update_speed(speed)
            return

        # For simulated data, use smoothing
        # Apply moving average for smoother updates with smaller changes
        self._speed_history.append(speed)
        if len(self._speed_history) > self._MAX_HISTORY:
            self._speed_history.pop(0)

        # Calculate smoothed value
        smooth_speed = sum(self._speed_history) / len(self._speed_history)

        # Update the speedometer with smoothed value for small changes
        self.main_window.speedometer.update_speed(smooth_speed)

    def _on_acceleration_changed(self, acceleration):
        """
        Process acceleration updates.

        Args:
            acceleration: Acceleration in m/s²
        """
        # For WebSocket data, update immediately without smoothing
        if self.sensor_provider.data_source == "websocket":
            # Store x-axis acceleration
            if not hasattr(self, "_accel_history"):
                self._accel_history = []
            self._accel_history.append(acceleration)

            # If we have lateral acceleration data, update with both values
            if hasattr(self, "_lateral_accel_history") and self._lateral_accel_history:
                lateral_accel = self._lateral_accel_history[-1]
                self.main_window.speedometer.update_acceleration(
                    acceleration, lateral_accel
                )
            else:
                # Just update with longitudinal acceleration until we get lateral data
                self.main_window.speedometer.update_acceleration(acceleration)

            # Convert from m/s² to G (1G = 9.81 m/s²) for GG diagram
            accel_g = acceleration / 9.81

            # Update the GG diagram if lateral accel data is available
            if hasattr(self, "_lateral_accel_history") and self._lateral_accel_history:
                # Use latest lateral acceleration
                lateral_accel = self._lateral_accel_history[-1]
                lateral_accel_g = lateral_accel / 9.81
                self.main_window.gg_diagram.setAccel(accel_g, lateral_accel_g)
            return

        # For simulated data, use smoothing
        # Apply moving average for smoothing
        self._accel_history.append(acceleration)
        if len(self._accel_history) > self._MAX_HISTORY:
            self._accel_history.pop(0)

        smooth_accel = sum(self._accel_history) / len(self._accel_history)

        # Get smoothed lateral acceleration if available
        if hasattr(self, "_smooth_lateral_accel"):
            self.main_window.speedometer.update_acceleration(
                smooth_accel, self._smooth_lateral_accel
            )
        else:
            self.main_window.speedometer.update_acceleration(smooth_accel)

        # Convert from m/s² to G (1G = 9.81 m/s²) for GG diagram
        accel_g = smooth_accel / 9.81

        # Update the GG diagram if lateral accel data is available
        if hasattr(self, "_smooth_lateral_accel"):
            self.main_window.gg_diagram.setAccel(accel_g, self._smooth_lateral_accel)

    def _on_lateral_accel_changed(self, lateral_accel):
        """
        Process lateral acceleration updates.

        Args:
            lateral_accel: Lateral acceleration in m/s²
        """
        # For WebSocket data, update immediately without smoothing
        if self.sensor_provider.data_source == "websocket":
            # Convert from m/s² to G
            lateral_accel_g = lateral_accel / 9.81

            # Store the lateral acceleration
            if not hasattr(self, "_lateral_accel_history"):
                self._lateral_accel_history = []
            self._lateral_accel_history.append(lateral_accel)

            # Get current longitudinal acceleration and update speedometer with both values
            if hasattr(self, "_accel_history") and self._accel_history:
                accel = self._accel_history[-1]
                self.main_window.speedometer.update_acceleration(accel, lateral_accel)

                # Update GG diagram
                accel_g = accel / 9.81
                self.main_window.gg_diagram.setAccel(accel_g, lateral_accel_g)
            return

        # For simulated data, use smoothing
        # Apply moving average for smoothing
        self._lateral_accel_history.append(lateral_accel)
        if len(self._lateral_accel_history) > self._MAX_HISTORY:
            self._lateral_accel_history.pop(0)

        self._smooth_lateral_accel = sum(self._lateral_accel_history) / len(
            self._lateral_accel_history
        )

        # Update speedometer with both acceleration components if available
        if hasattr(self, "_accel_history") and self._accel_history:
            smooth_accel = sum(self._accel_history) / len(self._accel_history)
            self.main_window.speedometer.update_acceleration(
                smooth_accel, self._smooth_lateral_accel
            )

        # Convert from m/s² to G (1G = 9.81 m/s²) for GG diagram
        lateral_accel_g = self._smooth_lateral_accel / 9.81

        # Get current longitudinal acceleration
        if hasattr(self, "_accel_history") and self._accel_history:
            # Calculate average of acceleration history
            smooth_accel = sum(self._accel_history) / len(self._accel_history)
            # Convert to G
            accel_g = smooth_accel / 9.81
            # Update the GG diagram
            self.main_window.gg_diagram.setAccel(accel_g, lateral_accel_g)

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
        # Update the mapbox view only (heading widget was replaced with gg_diagram)
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
        if widget_type == "gg_diagram" and hasattr(self.main_window, "gg_diagram"):
            if hasattr(self.main_window.gg_diagram, "set_update_interval"):
                self.main_window.gg_diagram.set_update_interval(rate_ms)
        # Implementation for other widget types can be added here

    def _force_initial_update(self):
        """Force an initial update of the UI with current data."""
        print("Forcing initial update of UI")
        if self.sensor_provider.data_source == "websocket":
            # Display active connection status while we wait for real data
            self.main_window.update_connection_status(
                "Connecting", "Waiting for WebSocket data..."
            )
