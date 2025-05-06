"""
Configuration settings for Force-Fusion dashboard.
Contains constants for display ranges, units, update intervals, and styling.
"""

# Debug settings
DEBUG_MODE = False  # Enable for development and debugging

# Sensor update intervals (milliseconds)
GPS_UPDATE_INTERVAL = 20  # Faster update
SPEED_UPDATE_INTERVAL = 20  # Faster update
ATTITUDE_UPDATE_INTERVAL = 20  # Faster update
TIRE_FORCE_UPDATE_INTERVAL = 20  # Faster update
MAP_UPDATE_INTERVAL = 20  # Faster update
GG_DIAGRAM_UPDATE_INTERVAL = 20  # Faster update

# Data source configuration
DEFAULT_DATA_SOURCE = "websocket"  # Options: "simulated", "websocket"

# WebSocket configuration
WS_HOST = "localhost"  # Hostname for WebSocket server
WS_PORT = 8765  # Port for WebSocket server
WS_URI = f"ws://{WS_HOST}:{WS_PORT}"  # Full WebSocket URI
WS_RECONNECT_INTERVAL = 1000  # Milliseconds between reconnection attempts (1 second)
CSV_PATH = "data/vehicle_data.csv"  # Path for storing received data

# Mapbox configuration
# Replace with your actual token when using the application
MAPBOX_TOKEN = "YOUR_MAPBOX_TOKEN_HERE"
DEFAULT_CENTER = [-81.04897348153887, 29.18825368942673]  # [longitude, latitude]
DEFAULT_ZOOM = 17

# Minimap configuration
TRAJECTORY_LINE_WIDTH = 2

# Map tile configuration
TILE_SIZE = 256  # Standard map tile size in pixels
MAP_TILE_URLS = {
    "street": "http://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
    "satellite": "http://ecn.t0.tiles.virtualearth.net/tiles/a{q}.jpeg?g=1",
}
MINIMAP_DEFAULT_STYLE = "satellite"
DETAILMAP_DEFAULT_STYLE = "satellite"

# Map UI styles
MAP_BUTTON_ACTIVE_STYLE = "background-color: #3498db; padding: 8px 15px; border-radius: 4px; color: white; margin-right: 10px;"
MAP_BUTTON_INACTIVE_STYLE = "background-color: #34495e; padding: 8px 15px; border-radius: 4px; color: white; margin-right: 10px;"
MAP_BACKGROUND_COLOR = "#282828"
MAP_GRID_COLOR = "#aaaaaa"
MAP_GRID_OPACITY = 100  # 0-255

# Speedometer configuration
SPEED_MIN = 0
SPEED_MAX = 60  # mi/h
ACCEL_MIN = -10  # m/s²
ACCEL_MAX = 10  # m/s²

# Attitude indicator configuration
PITCH_MIN = -40  # degrees
PITCH_MAX = 40  # degrees
ROLL_MIN = -40  # degrees
ROLL_MAX = 40  # degrees

# GG Diagram configuration
GG_DIAGRAM_MIN_G = -1.5  # Minimum G force
GG_DIAGRAM_MAX_G = 1.5  # Maximum G force

# Tire force configuration
TIRE_FORCE_MIN = 0  # N
TIRE_FORCE_MAX = 2500  # N
TIRE_FORCE_NORMAL = 2500  # N

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
TIRE_FORCE_COLOR_LIME = "#b4ff32"
TIRE_FORCE_COLOR_ORANGE = "#ff7800"
ROLL_POINTER_COLOR = "#00ffff"
PITCH_POINTER_COLOR = "#ffbf00"
BEZEL_COLOR = "#3c3c3c"
BEZEL_BORDER_COLOR = "#323232"
