"""
Configuration settings for Force-Fusion dashboard.
Contains constants for display ranges, units, update intervals, and styling.
"""

# Sensor update intervals (milliseconds)
GPS_UPDATE_INTERVAL = 1000
SPEED_UPDATE_INTERVAL = 100
ATTITUDE_UPDATE_INTERVAL = 100
TIRE_FORCE_UPDATE_INTERVAL = 200
MAP_UPDATE_INTERVAL = 1000

# Display ranges
SPEED_MIN = 0
SPEED_MAX = 160  # km/h
ACCEL_MIN = -10  # m/s²
ACCEL_MAX = 10  # m/s²
PITCH_MIN = -40  # degrees
PITCH_MAX = 40  # degrees
ROLL_MIN = -40  # degrees
ROLL_MAX = 40  # degrees
TIRE_FORCE_MIN = 0  # N
TIRE_FORCE_MAX = 2500  # N
TIRE_FORCE_NORMAL = 2500  # N

# Mapbox configuration
# Replace with your actual token when using the application
MAPBOX_TOKEN = "YOUR_MAPBOX_TOKEN_HERE"
DEFAULT_CENTER = [-81.04897348153887, 29.18825368942673]  # [longitude, latitude]
DEFAULT_ZOOM = 15

# Minimap configuration
TRAJECTORY_HISTORY_LENGTH = 5000  # Maximum number of points to keep
TRAJECTORY_LINE_WIDTH = 2

# UI colors
BACKGROUND_COLOR = "#1f1f1f"
TEXT_COLOR = "#eeeeee"
ACCENT_COLOR = "#3498db"
WARNING_COLOR = "#f1c40f"
DANGER_COLOR = "#e74c3c"
SUCCESS_COLOR = "#2ecc71"

# Gauge colors
SPEED_COLOR = "#4CAF50"
ACCEL_COLOR_POSITIVE = "#2ecc71"
ACCEL_COLOR_NEGATIVE = "#e74c3c"
HEADING_COLOR = "#ff0000"
TIRE_FORCE_COLOR_NORMAL = "#f1c40f"
TIRE_FORCE_COLOR_HIGH = "#e74c3c"
TIRE_FORCE_COLOR_LOW = "#2ecc71"
