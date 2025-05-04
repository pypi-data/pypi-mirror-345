"""
Sensor data provider that emits signals for all dashboard data channels.
"""

import csv
import json
import math
import os
from datetime import datetime

from PyQt5.QtCore import QObject, QTimer, QUrl, pyqtSignal
from PyQt5.QtNetwork import QAbstractSocket
from PyQt5.QtWebSockets import QWebSocket

from force_fusion import config


class SensorProvider(QObject):
    """
    Provides sensor data to the dashboard by emitting Qt signals.

    In a real application, this would connect to actual vehicle sensors.
    For demonstration purposes, it generates simulated data.
    """

    # Define signals for each data channel
    position_changed = pyqtSignal(float, float)  # lat, lon
    speed_changed = pyqtSignal(float)  # km/h
    acceleration_changed = pyqtSignal(float)  # m/s²
    lateral_accel_changed = pyqtSignal(float)  # m/s²
    pitch_changed = pyqtSignal(float)  # degrees
    roll_changed = pyqtSignal(float)  # degrees
    heading_changed = pyqtSignal(float)  # degrees (0-360)
    tire_forces_changed = pyqtSignal(
        dict
    )  # {"FL": force, "FR": force, "RL": force, "RR": force} in N

    # Time signals
    current_time_changed = pyqtSignal(str)  # formatted time string
    elapsed_time_changed = pyqtSignal(str)  # formatted time string

    # Status signals
    connection_status_changed = pyqtSignal(str, str)  # status, message

    def __init__(self, data_source="simulated"):
        """
        Initialize the sensor provider.

        Args:
            data_source: Source of sensor data. Options:
                - "simulated": Generate fake data (default)
                - "websocket": Connect to WebSocket server
                - "file": Read from log file (not implemented)
                - "can": Read from CAN bus (not implemented)
        """
        super().__init__()

        self.data_source = data_source
        print(f"Initializing SensorProvider with data source: {data_source}")

        # Show detailed startup info only in DEBUG_MODE
        if config.DEBUG_MODE:
            print(f"WebSocket URI: {config.WS_URI}")
            print("=" * 50)
            print("   STARTING FORCE-FUSION SENSOR PROVIDER")
            print(f"   Mode: {data_source}")
            print(f"   WebSocket: {config.WS_URI}")
            print("=" * 50)

        # Initialize simulated sensor values
        self._latitude = config.DEFAULT_CENTER[1]  # Default latitude
        self._longitude = config.DEFAULT_CENTER[0]  # Default longitude
        self._speed = 0.0  # km/h
        self._acceleration = 0.0  # m/s²
        self._lateral_accel = 0.0  # m/s², positive = right
        self._pitch = 0.0  # degrees
        self._roll = 0.0  # degrees
        self._heading = 0.0  # degrees
        self._tire_forces = {
            "FL": config.TIRE_FORCE_NORMAL,  # N
            "FR": config.TIRE_FORCE_NORMAL,
            "RL": config.TIRE_FORCE_NORMAL,
            "RR": config.TIRE_FORCE_NORMAL,
        }

        # For animations
        self._animation_counter = 0
        self._phase_offsets = {
            "FL": 0,
            "FR": 25,
            "RL": 50,
            "RR": 75,
        }  # Offset percentages
        self._animation_cycle_period = 150  # Make animation faster (was 300)

        # Speed and attitude animation
        self._speed_animation_cycle = 180  # 18 seconds at 100ms timer
        self._attitude_animation_cycle = 200  # 20 seconds at 100ms timer
        self._heading_animation_cycle = 240  # 24 seconds at 100ms timer

        # Start time tracking
        self._start_time = datetime.now()
        self._last_data_time = datetime.now()

        # Set up timer for each data channel (simulated data)
        self._position_timer = QTimer(self)
        self._speed_timer = QTimer(self)
        self._attitude_timer = QTimer(self)
        self._tire_force_timer = QTimer(self)
        self._time_timer = QTimer(self)

        # Connect timers to update methods
        self._position_timer.timeout.connect(self._update_position)
        self._speed_timer.timeout.connect(self._update_speed)
        self._attitude_timer.timeout.connect(self._update_attitude)
        self._tire_force_timer.timeout.connect(self._update_tire_forces)
        self._time_timer.timeout.connect(self._update_time)

        # WebSocket client (for real data)
        self._websocket = QWebSocket()
        self._websocket.connected.connect(self._on_websocket_connected)
        self._websocket.disconnected.connect(self._on_websocket_disconnected)
        self._websocket.textMessageReceived.connect(self._on_websocket_message)
        self._websocket.error.connect(self._on_websocket_error)
        self._messages_received = 0

        # WebSocket reconnection timer
        self._reconnect_timer = QTimer(self)
        self._reconnect_timer.timeout.connect(self._try_reconnect)

        # CSV data logging
        self._csv_file = None
        self._csv_writer = None
        self._setup_csv_logging()

    def start(self):
        """Start the sensor data feed based on the selected source."""
        print(f"Starting sensor provider with data source: {self.data_source}")

        # Make sure any previous timers are stopped
        self.stop()

        # Start the appropriate data source
        if self.data_source == "simulated":
            self._start_simulated_data()
        elif self.data_source == "websocket":
            # First try to connect to WebSocket
            self._start_websocket_client()

            # Start reconnect timer right away in case server isn't running yet
            if not self._reconnect_timer.isActive():
                # First connection can take a bit longer, use a different initial interval
                # This allows time for the server to start
                initial_reconnect_interval = 500  # 0.5 seconds
                print(
                    f"Starting initial connection attempt timer ({initial_reconnect_interval}ms)"
                )
                self._reconnect_timer.start(initial_reconnect_interval)

                # Set up a one-time longer reconnect after a bit more time
                # This helps ensure we eventually connect to the server
                from PyQt5.QtCore import QTimer

                QTimer.singleShot(3000, self._try_reconnect)

            # Don't fall back to simulated data, just show Waiting status
            self.connection_status_changed.emit(
                "Connecting", f"Waiting for WebSocket ({config.WS_URI})"
            )
        else:
            print(f"Unsupported data source: {self.data_source}")
            # Fall back to simulated data
            self.data_source = "simulated"
            self._start_simulated_data()

        # Start time update timer (always active regardless of data source)
        self._time_timer.start(config.SPEED_UPDATE_INTERVAL)

        # Initial update to populate values
        self._update_time()

    def stop(self):
        """Stop all sensor update timers and connections."""
        # Stop timers
        print("Stopping all sensor timers")
        if hasattr(self, "_position_timer"):
            self._position_timer.stop()
        if hasattr(self, "_speed_timer"):
            self._speed_timer.stop()
        if hasattr(self, "_attitude_timer"):
            self._attitude_timer.stop()
        if hasattr(self, "_tire_force_timer"):
            self._tire_force_timer.stop()
        if hasattr(self, "_time_timer"):
            self._time_timer.stop()
        if hasattr(self, "_reconnect_timer"):
            self._reconnect_timer.stop()

        # Close WebSocket connection
        if hasattr(self, "_websocket"):
            state = self._websocket.state()
            if state == QAbstractSocket.ConnectedState:
                print("Closing active WebSocket connection")
                self._websocket.close()
            else:
                print(f"WebSocket not connected (state: {state})")

        # Close CSV file if open
        if hasattr(self, "_csv_file") and self._csv_file and not self._csv_file.closed:
            print("Closing CSV log file")
            self._csv_file.close()
            self._csv_file = None
            self._csv_writer = None

    def _setup_csv_logging(self):
        """Set up CSV file for logging data."""
        try:
            # Create directory if it doesn't exist
            data_dir = os.path.dirname(config.CSV_PATH)
            if data_dir:
                os.makedirs(data_dir, exist_ok=True)

            # Debug message
            if config.DEBUG_MODE:
                print(f"Setting up CSV logging to: {os.path.abspath(config.CSV_PATH)}")

            # Open CSV file in append mode
            self._csv_file = open(config.CSV_PATH, "a", newline="")

            # Define CSV fields
            fieldnames = [
                "timestamp",
                "latitude",
                "longitude",
                "heading",
                "speed",
                "acceleration",
                "lateral_accel",
                "pitch",
                "roll",
                "tire_force_FL",
                "tire_force_FR",
                "tire_force_RL",
                "tire_force_RR",
            ]

            # Create CSV writer
            self._csv_writer = csv.DictWriter(self._csv_file, fieldnames=fieldnames)

            # Write header if file is empty
            if self._csv_file.tell() == 0:
                self._csv_writer.writeheader()
                if config.DEBUG_MODE:
                    print("Added CSV header (new file)")

        except Exception as e:
            print(f"Error setting up CSV logging: {e}")
            self._csv_file = None
            self._csv_writer = None

    def _log_to_csv(self):
        """Log current data to CSV file."""
        if not self._csv_writer:
            # Try to set up the CSV writer if it doesn't exist
            self._setup_csv_logging()
            # If it still doesn't exist, return
            if not self._csv_writer:
                return

        try:
            # Create data row
            data = {
                "timestamp": datetime.now().isoformat(),
                "latitude": self._latitude,
                "longitude": self._longitude,
                "heading": self._heading,
                "speed": self._speed,
                "acceleration": self._acceleration,
                "lateral_accel": self._lateral_accel,
                "pitch": self._pitch,
                "roll": self._roll,
                "tire_force_FL": self._tire_forces["FL"],
                "tire_force_FR": self._tire_forces["FR"],
                "tire_force_RL": self._tire_forces["RL"],
                "tire_force_RR": self._tire_forces["RR"],
            }

            # Write to CSV
            self._csv_writer.writerow(data)
            self._csv_file.flush()  # Ensure data is written immediately

            # Log occasional entries for debugging
            if config.DEBUG_MODE and self._messages_received % 50 == 0:
                print(f"Logged data to CSV: {config.CSV_PATH}")

        except Exception as e:
            print(f"Error logging to CSV: {e}")
            # Try to recreate the CSV writer
            self._csv_file = None
            self._csv_writer = None
            self._setup_csv_logging()

    def _start_simulated_data(self):
        """Start all sensor update timers for simulated data."""
        self.connection_status_changed.emit("Active", "Using Simulated Data")

        # Start timers with configured intervals
        self._position_timer.start(config.GPS_UPDATE_INTERVAL)
        self._speed_timer.start(config.SPEED_UPDATE_INTERVAL)
        self._attitude_timer.start(config.ATTITUDE_UPDATE_INTERVAL)
        self._tire_force_timer.start(config.TIRE_FORCE_UPDATE_INTERVAL)

        # Initial update to populate values
        self._update_position()
        self._update_speed()
        self._update_attitude()
        self._update_tire_forces()

    def _start_websocket_client(self):
        """Connect to the WebSocket server."""
        # Make sure we're not already connected
        if self._websocket.state() == QAbstractSocket.ConnectedState:
            if config.DEBUG_MODE:
                print("Already connected to WebSocket server, disconnecting first")
            self._websocket.close()

        # Debug info
        if config.DEBUG_MODE:
            print(
                f"WebSocket URL is: {config.WS_URI} (host={config.WS_HOST}, port={config.WS_PORT})"
            )

        # Update UI status
        self.connection_status_changed.emit("Connecting", f"WebSocket: {config.WS_URI}")

        if config.DEBUG_MODE:
            print(f"Opening WebSocket connection to: {config.WS_URI}")
        else:
            print(f"Connecting to: {config.WS_URI}")

        # Debug timer disabled - was causing 5-second update issue
        # self._debug_timer = QTimer()
        # self._debug_timer.timeout.connect(self._simulate_websocket_message)
        # self._debug_timer.start(5000)  # Test message every 5 seconds

        # Open the connection
        # Convert string URL to QUrl
        import re

        if not re.match(r"^ws://|^wss://", config.WS_URI):
            url = QUrl(f"ws://{config.WS_URI}")
        else:
            url = QUrl(config.WS_URI)

        if config.DEBUG_MODE:
            print(f"Opening connection to: {url.toString()}")

            # Explicitly set the WebSocket version and protocols
            self._websocket.version()
            print(f"WebSocket version: {self._websocket.version()}")

        # Open the connection
        self._websocket.open(url)

    def _simulate_websocket_message(self):
        """Simulate a WebSocket message for debugging."""
        print("Debug simulation disabled")
        return

        # Only run this if in WebSocket mode
        if self.data_source != "websocket":
            self._debug_timer.stop()
            return

        # Simulate a received message
        print("\n=== SIMULATING WEBSOCKET MESSAGE ===")
        test_data = {
            "timestamp": datetime.now().isoformat(),
            "test": True,
            "latitude": 29.18 + (self._messages_received * 0.001),
            "longitude": -81.04 - (self._messages_received * 0.001),
            "speed": 50.0 + (self._messages_received * 2.0),
            "heading": (self._messages_received * 10) % 360,
            "acceleration_x": 1.0,
            "acceleration_y": 0.5,
            "pitch": 2.0,
            "roll": 1.0,
            "tire_forces": {"FL": 2000, "FR": 2000, "RL": 2000, "RR": 2000},
        }

        # Convert to JSON and process
        test_msg = json.dumps(test_data)
        print(f"Simulated message: {test_msg[:100]}...")

        # Call the message handler directly
        self._on_websocket_message(test_msg)

        # Check if the message was handled correctly
        print("=== END SIMULATED MESSAGE ===\n")

    def _try_reconnect(self):
        """Attempt to reconnect to the WebSocket server."""
        if self.data_source != "websocket":
            if config.DEBUG_MODE:
                print("Not in WebSocket mode, stopping reconnection timer")
            self._reconnect_timer.stop()
            return

        if self._websocket.state() != QAbstractSocket.ConnectedState:
            self.connection_status_changed.emit(
                "Reconnecting", f"WebSocket: {config.WS_URI}"
            )

            if config.DEBUG_MODE:
                print(f"Attempting to reconnect to WebSocket server: {config.WS_URI}")

            # Close any existing connection first
            if self._websocket.state() != QAbstractSocket.UnconnectedState:
                if config.DEBUG_MODE:
                    print(
                        f"WebSocket in state {self._websocket.state()}, closing first"
                    )
                self._websocket.close()

            # Try to open a new connection
            self._websocket.open(QUrl(config.WS_URI))
        else:
            if config.DEBUG_MODE:
                print("WebSocket already connected, stopping reconnection timer")
            self._reconnect_timer.stop()

    def _on_websocket_connected(self):
        """Handle WebSocket connection success."""
        if config.DEBUG_MODE:
            print("\n=== WEBSOCKET CONNECTED SUCCESSFULLY ===")
            print(f"Socket state: {self._websocket.state()}")
        else:
            print("WebSocket Connected")

        self.connection_status_changed.emit("Active", "WebSocket Data Active")
        self._reconnect_timer.stop()  # Stop reconnection attempts
        self._messages_received = 0

        # Force UI to update
        self._update_time()

        # Reset sensor values to zero to clear any cached data
        self._speed = 0.0
        self.speed_changed.emit(self._speed)
        self._acceleration = 0.0
        self.acceleration_changed.emit(self._acceleration)
        self._lateral_accel = 0.0
        self.lateral_accel_changed.emit(self._lateral_accel)
        self._pitch = 0.0
        self.pitch_changed.emit(self._pitch)
        self._roll = 0.0
        self.roll_changed.emit(self._roll)

        # Don't reset position and heading to prevent map jumping

        # Log the connection
        if config.DEBUG_MODE:
            print("=== READY TO RECEIVE DATA ===\n")
        else:
            print("Ready to receive data")

    def _on_websocket_disconnected(self):
        """Handle WebSocket disconnection."""
        if config.DEBUG_MODE:
            print("WebSocket disconnected")

        self.connection_status_changed.emit("Inactive", "WebSocket Disconnected")

        # Don't show any data when disconnected in WebSocket mode
        # Reset all values to make it clear we're not receiving data
        if self.data_source == "websocket":
            # Emit zero values for all sensors
            self._speed = 0.0
            self.speed_changed.emit(self._speed)

            self._acceleration = 0.0
            self.acceleration_changed.emit(self._acceleration)

            self._lateral_accel = 0.0
            self.lateral_accel_changed.emit(self._lateral_accel)

            self._pitch = 0.0
            self.pitch_changed.emit(self._pitch)

            self._roll = 0.0
            self.roll_changed.emit(self._roll)

            self._heading = 0.0
            self.heading_changed.emit(self._heading)

            # Don't change position to keep minimap centered

        # Start reconnection timer
        if self.data_source == "websocket" and not self._reconnect_timer.isActive():
            if config.DEBUG_MODE:
                print(
                    f"Starting reconnection timer (interval: {config.WS_RECONNECT_INTERVAL}ms)"
                )
            self._reconnect_timer.start(config.WS_RECONNECT_INTERVAL)

    def _on_websocket_error(self, error_code):
        """Handle WebSocket errors."""
        error_message = self._websocket.errorString()

        if config.DEBUG_MODE:
            print(f"WebSocket error: {error_message} (code: {error_code})")
        else:
            print(f"WebSocket error: {error_message}")

        self.connection_status_changed.emit(
            "Error", f"WebSocket Error: {error_message}"
        )

        # Start reconnection timer
        if self.data_source == "websocket" and not self._reconnect_timer.isActive():
            if config.DEBUG_MODE:
                print(
                    f"Starting reconnection timer after error (interval: {config.WS_RECONNECT_INTERVAL}ms)"
                )
            self._reconnect_timer.start(config.WS_RECONNECT_INTERVAL)

    def _on_websocket_message(self, message):
        """Process incoming WebSocket messages."""
        self._messages_received += 1

        # Only show verbose output if DEBUG_MODE is enabled
        if config.DEBUG_MODE:
            print("\n" + "=" * 50)
            print(f"WEBSOCKET MESSAGE RECEIVED: {message[:100]}...")
            print("=" * 50 + "\n")
            print(f"\n### WEBSOCKET MESSAGE RECEIVED ({self._messages_received}) ###")

        try:
            # Parse JSON data from WebSocket message
            import json

            data = json.loads(message)

            # Record the time the data was received
            self._last_data_time = datetime.now()

            # Print a preview of received data for debugging
            if config.DEBUG_MODE:
                debug_message = str(data)
                if len(debug_message) > 100:
                    debug_message = debug_message[:100] + "..."
                print(f"WebSocket data received: {debug_message}")

            # Process data and update UI
            has_valid_data = False

            # Always emit all signals even if the values haven't changed much
            # This ensures the UI updates at 10Hz when we receive 10Hz data

            # Update position
            if "latitude" in data and "longitude" in data:
                self._latitude = data["latitude"]
                self._longitude = data["longitude"]
                self.position_changed.emit(self._latitude, self._longitude)

                if config.DEBUG_MODE:
                    print(f"POSITION: {self._latitude}, {self._longitude}")

                has_valid_data = True

            # Update speed
            if "speed" in data:
                self._speed = data["speed"]
                self.speed_changed.emit(self._speed)

                if config.DEBUG_MODE:
                    print(f"SPEED: {self._speed}")

                has_valid_data = True

            # Update longitudinal acceleration
            if "acceleration_x" in data:
                self._acceleration = data["acceleration_x"]
                self.acceleration_changed.emit(self._acceleration)
                has_valid_data = True

            # Update lateral acceleration
            if "acceleration_y" in data:
                self._lateral_accel = data["acceleration_y"]
                self.lateral_accel_changed.emit(self._lateral_accel)
                has_valid_data = True

            # Update pitch
            if "pitch" in data:
                self._pitch = data["pitch"]
                self.pitch_changed.emit(self._pitch)
                has_valid_data = True

            # Update roll
            if "roll" in data:
                self._roll = data["roll"]
                self.roll_changed.emit(self._roll)
                has_valid_data = True

            # Update heading
            if "heading" in data:
                self._heading = data["heading"]
                self.heading_changed.emit(self._heading)

                if config.DEBUG_MODE:
                    print(f"HEADING: {self._heading}")

                has_valid_data = True

            # Update tire forces
            if "tire_forces" in data:
                # Ensure all four tire positions are present
                tire_data = data["tire_forces"]
                if all(key in tire_data for key in ["FL", "FR", "RL", "RR"]):
                    self._tire_forces = tire_data
                    self.tire_forces_changed.emit(self._tire_forces)
                    has_valid_data = True

            # Update connection status if we received valid data
            if has_valid_data:
                self.connection_status_changed.emit("Active", "WebSocket Data Active")

                if config.DEBUG_MODE:
                    print("Valid data received - letting Qt handle UI update")

            elif config.DEBUG_MODE:
                print("No valid data found in message")

            # Log data to CSV
            self._log_to_csv()

        except json.JSONDecodeError as e:
            print(f"Error parsing WebSocket message: {e}")
        except Exception as e:
            print(f"Error processing WebSocket data: {e}")
            import traceback

            traceback.print_exc()

    def _update_position(self):
        """Update GPS position and emit signal."""
        if self.data_source == "simulated":
            # Simulate vehicle movement based on current heading and speed
            speed_mps = self._speed / 3.6  # Convert km/h to m/s

            # Calculate distance moved since last update (m)
            distance = speed_mps * (self._position_timer.interval() / 1000.0)

            # Convert heading to radians
            heading_rad = math.radians(self._heading)

            # Calculate changes in longitude and latitude
            # Simplified model, not accounting for Earth's curvature accurately
            lat_change = (
                distance * math.cos(heading_rad) / 111000
            )  # 1 degree lat ≈ 111 km
            # Longitude distance depends on latitude
            lon_change = (
                distance
                * math.sin(heading_rad)
                / (111000 * math.cos(math.radians(self._latitude)))
            )

            # Update position
            self._latitude += lat_change
            self._longitude += lon_change

            # Emit the position signal
            self.position_changed.emit(self._latitude, self._longitude)

            # Also update heading as we move
            self.heading_changed.emit(self._heading)

            # Log simulated data
            self._log_to_csv()

    def _update_speed(self):
        """Update speed and acceleration values and emit signals."""
        if self.data_source == "simulated":
            # Use animation counter for smooth oscillation
            self._animation_counter += 1
            counter = self._animation_counter

            # Animate speed to go up and down smoothly
            cycle_period = self._speed_animation_cycle
            cycle_position = counter % cycle_period

            # Sinusoidal variation for smoother transitions
            # First half: accelerating, Second half: decelerating
            if cycle_position < cycle_period / 2:
                ratio = cycle_position / (cycle_period / 2)
                self._speed = ratio * config.SPEED_MAX
                self._acceleration = (
                    config.ACCEL_MAX
                )  # Use full positive acceleration range
            else:
                ratio = (cycle_position - cycle_period / 2) / (cycle_period / 2)
                self._speed = (1 - ratio) * config.SPEED_MAX
                self._acceleration = (
                    config.ACCEL_MIN
                )  # Use full negative acceleration range

            # Generate lateral acceleration value (simulated)
            # Create a sinusoidal value that varies independently of the forward accel
            lateral_cycle = int(
                self._speed_animation_cycle * 0.6
            )  # Different period for variety
            lateral_position = counter % lateral_cycle
            lateral_ratio = lateral_position / lateral_cycle
            lateral_sin = math.sin(lateral_ratio * math.pi * 2)

            # Scale based on speed (more speed = more potential lateral G)
            speed_factor = self._speed / config.SPEED_MAX
            self._lateral_accel = lateral_sin * config.ACCEL_MAX * 0.5 * speed_factor

        # Emit the signals
        self.speed_changed.emit(self._speed)
        self.acceleration_changed.emit(self._acceleration)
        # Also emit lateral acceleration signal
        self.lateral_accel_changed.emit(self._lateral_accel)

    def _update_attitude(self):
        """Update pitch and roll values and emit signals."""
        if self.data_source == "simulated":
            # Use animation counter for smooth oscillation
            counter = self._animation_counter

            # Animate pitch - full range from min to max and back
            pitch_cycle = self._attitude_animation_cycle
            pitch_position = counter % pitch_cycle

            if pitch_position < pitch_cycle / 2:
                ratio = pitch_position / (pitch_cycle / 2)
                self._pitch = config.PITCH_MIN + ratio * (
                    config.PITCH_MAX - config.PITCH_MIN
                )
            else:
                ratio = (pitch_position - pitch_cycle / 2) / (pitch_cycle / 2)
                self._pitch = config.PITCH_MAX - ratio * (
                    config.PITCH_MAX - config.PITCH_MIN
                )

            # Animate roll - alternate between min and max
            roll_cycle = (
                self._attitude_animation_cycle * 0.7
            )  # Different period for variety
            roll_position = counter % roll_cycle

            if roll_position < roll_cycle / 2:
                ratio = roll_position / (roll_cycle / 2)
                self._roll = config.ROLL_MIN + ratio * (
                    config.ROLL_MAX - config.ROLL_MIN
                )
            else:
                ratio = (roll_position - roll_cycle / 2) / (roll_cycle / 2)
                self._roll = config.ROLL_MAX - ratio * (
                    config.ROLL_MAX - config.ROLL_MIN
                )

            # Animate heading - full 360 rotation
            heading_cycle = self._heading_animation_cycle
            heading_position = counter % heading_cycle

            heading_range = 360  # Full circle rotation
            if heading_position < heading_cycle / 2:
                ratio = heading_position / (heading_cycle / 2)
                self._heading = ratio * heading_range
            else:
                ratio = (heading_position - heading_cycle / 2) / (heading_cycle / 2)
                self._heading = (1 - ratio) * heading_range

            # Generate lateral acceleration based on roll angle and speed
            # In real vehicles, lateral acceleration is correlated with roll
            # Simulate this relationship: more roll = more lateral G
            lateral_accel_factor = 0.25  # m/s² per degree of roll
            speed_factor = (
                self._speed / 100.0
            )  # More speed = more lateral G for same roll

            # Calculate lateral acceleration based on roll
            # Scale by speed to make it more realistic
            self._lateral_accel = (
                self._roll * lateral_accel_factor * (1.0 + speed_factor)
            )

            # Add some variation to make it less directly correlated
            # In a real car, lateral accel leads to roll, not the other way around
            variation_cycle = self._attitude_animation_cycle * 0.3
            variation_position = counter % variation_cycle
            variation_ratio = variation_position / variation_cycle
            variation = (variation_ratio - 0.5) * 2.0  # -1.0 to 1.0

            # Add variation to lateral acceleration
            self._lateral_accel += variation * config.ACCEL_MAX * 0.2

        # Emit the signals
        self.pitch_changed.emit(self._pitch)
        self.roll_changed.emit(self._roll)
        self.heading_changed.emit(self._heading)
        self.lateral_accel_changed.emit(self._lateral_accel)

    def _update_tire_forces(self):
        """Update tire normal forces and emit signal."""
        if self.data_source == "simulated":
            # Update animation counter
            self._animation_counter += 1
            counter = self._animation_counter

            # Maximum force and cycle period
            max_force = config.TIRE_FORCE_MAX  # Maximum force in Newtons
            cycle_period = self._animation_cycle_period

            # Update each tire with proper phase offset
            for position in ["FL", "FR", "RL", "RR"]:
                # Apply phase offset for each tire
                offset = self._phase_offsets[position]
                adjusted_counter = (
                    counter + offset * cycle_period / 100
                ) % cycle_period

                # First half of cycle: 0 to max force (monotonically increasing)
                if adjusted_counter < cycle_period / 2:
                    ratio = adjusted_counter / (cycle_period / 2)
                    self._tire_forces[position] = config.TIRE_FORCE_MIN + ratio * (
                        max_force - config.TIRE_FORCE_MIN
                    )
                # Second half of cycle: max force to 0 (monotonically decreasing)
                else:
                    ratio = (adjusted_counter - cycle_period / 2) / (cycle_period / 2)
                    self._tire_forces[position] = max_force - ratio * (
                        max_force - config.TIRE_FORCE_MIN
                    )

        # Emit the signal
        self.tire_forces_changed.emit(self._tire_forces.copy())

    def _update_time(self):
        """Update time displays and emit signals."""
        # Get current time
        current_time = datetime.now()

        # Format current time
        current_time_str = current_time.strftime("%Hh:%Mmin:%Ssec")

        # Calculate elapsed time
        elapsed = current_time - self._start_time
        total_seconds = int(elapsed.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        elapsed_time_str = f"{hours:02d}h:{minutes:02d}min:{seconds:02d}sec"

        # Emit signals
        self.current_time_changed.emit(current_time_str)
        self.elapsed_time_changed.emit(elapsed_time_str)

    def set_data_source(self, source):
        """
        Change the data source.

        Args:
            source: New data source ("simulated", "websocket", "file", or "can")
        """
        print(f"Setting data source from {self.data_source} to {source}")
        # Only restart if the source is actually different
        if source != self.data_source:
            # First stop current data source
            print(f"Stopping current data source: {self.data_source}")
            self.stop()

            # Clean up any existing connections
            if hasattr(self, "_websocket") and self._websocket:
                print("Forcing WebSocket cleanup")
                try:
                    # Disconnect all signals to avoid callbacks during cleanup
                    self._websocket.connected.disconnect()
                    self._websocket.disconnected.disconnect()
                    self._websocket.textMessageReceived.disconnect()
                    self._websocket.error.disconnect()
                except Exception as e:
                    print(f"Error disconnecting signals: {e}")

                # Close and delete the socket
                self._websocket.close()
                self._websocket.deleteLater()

                # Create a new socket object
                from PyQt5.QtWebSockets import QWebSocket

                self._websocket = QWebSocket()
                print("Creating new WebSocket with signal connections:")

                # Connect the signals with explicit checks
                self._websocket.connected.connect(self._on_websocket_connected)
                print("  - connected signal connected")

                self._websocket.disconnected.connect(self._on_websocket_disconnected)
                print("  - disconnected signal connected")

                self._websocket.textMessageReceived.connect(self._on_websocket_message)
                print("  - textMessageReceived signal connected")

                self._websocket.error.connect(self._on_websocket_error)
                print("  - error signal connected")

                # Add a local test signal connection to verify signal handling is working
                def test_websocket_signals():
                    print("Testing WebSocket message signal...")
                    self._on_websocket_message('{"test":"Testing signal connection"}')

                # Schedule a test message after 2 seconds
                test_timer = QTimer()
                test_timer.setSingleShot(True)
                test_timer.timeout.connect(test_websocket_signals)
                test_timer.start(2000)

            # Set the new data source
            self.data_source = source

            # Start with the new source
            print(f"Starting new data source: {self.data_source}")
            self.start()
        else:
            print(f"Data source already set to {source}, forcing restart")
            # Force a restart of the same source for reconnection
            self.stop()
            self.start()
