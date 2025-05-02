"""
Sensor data provider that emits signals for all dashboard data channels.
"""

import math
from datetime import datetime

from PyQt5.QtCore import QObject, QTimer, pyqtSignal

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
    pitch_changed = pyqtSignal(float)  # degrees
    roll_changed = pyqtSignal(float)  # degrees
    heading_changed = pyqtSignal(float)  # degrees (0-360)
    tire_forces_changed = pyqtSignal(
        dict
    )  # {"FL": force, "FR": force, "RL": force, "RR": force} in N

    # Time signals
    current_time_changed = pyqtSignal(str)  # formatted time string
    elapsed_time_changed = pyqtSignal(str)  # formatted time string

    def __init__(self, data_source="simulated"):
        """
        Initialize the sensor provider.

        Args:
            data_source: Source of sensor data. Options:
                - "simulated": Generate fake data (default)
                - "file": Read from log file (not implemented)
                - "can": Read from CAN bus (not implemented)
        """
        super().__init__()

        self.data_source = data_source

        # Initialize simulated sensor values
        self._latitude = 37.7749  # San Francisco
        self._longitude = -122.4194
        self._speed = 0.0  # km/h
        self._acceleration = 0.0  # m/s²
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

        # Set up timer for each data channel
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

    def start(self):
        """Start all sensor update timers."""
        from force_fusion import config

        # Start timers with configured intervals
        self._position_timer.start(
            100
        )  # Update position more frequently (was config.GPS_UPDATE_INTERVAL which is 1000ms)
        self._speed_timer.start(config.SPEED_UPDATE_INTERVAL)
        self._attitude_timer.start(config.ATTITUDE_UPDATE_INTERVAL)
        self._tire_force_timer.start(config.TIRE_FORCE_UPDATE_INTERVAL)
        self._time_timer.start(100)  # Update time display every 100ms

        # Initial update to populate values
        self._update_position()
        self._update_speed()
        self._update_attitude()
        self._update_tire_forces()
        self._update_time()

    def stop(self):
        """Stop all sensor update timers."""
        self._position_timer.stop()
        self._speed_timer.stop()
        self._attitude_timer.stop()
        self._tire_force_timer.stop()
        self._time_timer.stop()

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
                self._acceleration = 2.0  # Positive acceleration when speed increasing
            else:
                ratio = (cycle_position - cycle_period / 2) / (cycle_period / 2)
                self._speed = (1 - ratio) * config.SPEED_MAX
                self._acceleration = -2.0  # Negative acceleration when speed decreasing

        # Emit the signals
        self.speed_changed.emit(self._speed)
        self.acceleration_changed.emit(self._acceleration)

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

            if heading_position < heading_cycle / 2:
                ratio = heading_position / (heading_cycle / 2)
                self._heading = ratio * 360
            else:
                ratio = (heading_position - heading_cycle / 2) / (heading_cycle / 2)
                self._heading = (1 - ratio) * 360

        # Emit the signals
        self.pitch_changed.emit(self._pitch)
        self.roll_changed.emit(self._roll)
        self.heading_changed.emit(self._heading)

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
                    self._tire_forces[position] = ratio * max_force
                # Second half of cycle: max force to 0 (monotonically decreasing)
                else:
                    ratio = (adjusted_counter - cycle_period / 2) / (cycle_period / 2)
                    self._tire_forces[position] = (1 - ratio) * max_force

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
            source: New data source ("simulated", "file", or "can")
        """
        self.stop()
        self.data_source = source
        self.start()
