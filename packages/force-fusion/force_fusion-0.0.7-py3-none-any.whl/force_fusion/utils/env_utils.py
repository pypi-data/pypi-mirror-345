"""
Configuration manager for Force-Fusion.
Handles loading default config values and overriding with .env file.
"""

import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Import the default config values
from force_fusion import config as default_config


class ConfigManager:
    """
    Manages configuration values with .env file override capability.
    """

    def __init__(self):
        """Initialize with default values from config.py."""
        # Store original config values
        self.config_vars: Dict[str, Any] = {}

        # Load default values from config.py
        for attr in dir(default_config):
            if not attr.startswith("__") and attr.isupper():
                self.config_vars[attr] = getattr(default_config, attr)

        # Load environment variables from .env if available
        self.load_env_file()

        # Override config values with environment variables
        self.override_from_env()

    def load_env_file(self) -> None:
        """
        Load environment variables from .env file.
        Looks for .env in current directory or parent directories.
        """
        # Check current directory and parents
        env_path = self._find_env_file()

        if not env_path:
            return

        try:
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    key, value = self._parse_env_line(line)
                    if key and key.startswith("FORCE_FUSION_"):
                        # Store in environment variables
                        os.environ[key] = value
        except Exception as e:
            print(f"Warning: Error reading .env file: {e}", file=sys.stderr)

    def _find_env_file(self) -> Optional[Path]:
        """
        Find .env file in current directory or parents.
        Returns the path to the .env file or None if not found.
        """
        current_dir = Path.cwd()

        # Check up to 3 parent directories
        for _ in range(4):
            env_path = current_dir / ".env"
            if env_path.exists():
                return env_path

            # Move up one directory
            parent = current_dir.parent
            if parent == current_dir:  # Reached root
                break
            current_dir = parent

        return None

    def _parse_env_line(self, line: str) -> tuple:
        """Parse a line from .env file into key-value pair."""
        # Handle common formats like KEY=value, KEY="value", etc.
        match = re.match(r'^([A-Za-z0-9_]+)=(?:"([^"]*)"|(\'([^\']*)\')|(.*))$', line)
        if match:
            key = match.group(1)
            # Find the first non-None value in the capture groups
            for i in range(2, 6):
                if match.group(i) is not None:
                    return key, match.group(i)
        return None, None

    def override_from_env(self) -> None:
        """
        Override config values from environment variables.
        Environment variables should be prefixed with FORCE_FUSION_.
        """
        for key in self.config_vars:
            env_key = f"FORCE_FUSION_{key}"
            if env_key in os.environ:
                env_value = os.environ[env_key]

                # Convert the environment variable to the appropriate type
                original_value = self.config_vars[key]
                converted_value = self._convert_value(
                    env_value, type(original_value), key
                )

                if converted_value is not None:
                    self.config_vars[key] = converted_value
                    # Also update the config module
                    setattr(default_config, key, converted_value)

    def _convert_value(self, value: str, target_type: type, key: str = None) -> Any:
        """Convert string value to the target type."""
        try:
            if target_type is bool:
                return value.lower() in ("true", "yes", "1", "y")
            elif target_type is int:
                return int(value)
            elif target_type is float:
                return float(value)
            elif target_type is list:
                # Handle lists of values
                items = [item.strip() for item in value.split(",")]

                # Try to detect the element type based on the original list
                if (
                    key
                    and key in self.config_vars
                    and self.config_vars[key]
                    and len(self.config_vars[key]) > 0
                ):
                    element_type = type(self.config_vars[key][0])
                    if element_type is float:
                        return [float(item) for item in items]
                    elif element_type is int:
                        return [int(item) for item in items]

                # Default to strings if we can't determine the type
                return items
            elif target_type is tuple:
                # Handle tuples of values
                items = [item.strip() for item in value.split(",")]

                # Try to detect the element type based on the original tuple
                if (
                    key
                    and key in self.config_vars
                    and self.config_vars[key]
                    and len(self.config_vars[key]) > 0
                ):
                    element_type = type(self.config_vars[key][0])
                    if element_type is float:
                        return tuple(float(item) for item in items)
                    elif element_type is int:
                        return tuple(int(item) for item in items)

                # Default to strings if we can't determine the type
                return tuple(items)
            elif target_type is str:
                return value
            else:
                # For complex types, try using eval (with appropriate caution)
                return eval(value)
        except Exception as e:
            print(
                f"Warning: Could not convert '{value}' to {target_type.__name__}: {e}",
                file=sys.stderr,
            )
            return None

    def export_to_env(self, output_path: str = ".env") -> None:
        """
        Export current config values to a .env file template.

        Args:
            output_path: Path to the output .env file
        """
        try:
            with open(output_path, "w") as f:
                f.write("# Force-Fusion Configuration\n")
                f.write("# This file was generated automatically\n\n")

                for key, value in sorted(self.config_vars.items()):
                    env_key = f"FORCE_FUSION_{key}"

                    # Convert value to string representation
                    if isinstance(value, str):
                        value_str = f'"{value}"'
                    elif isinstance(value, (list, tuple)):
                        # Format lists/tuples properly with element type preserved
                        if value and isinstance(value[0], (int, float)):
                            # Handle numeric lists
                            value_str = ",".join(str(item) for item in value)
                        else:
                            # Handle string lists or mixed type lists
                            value_str = ",".join(
                                f'"{item}"' if isinstance(item, str) else str(item)
                                for item in value
                            )
                    else:
                        value_str = str(value)

                    # Add a comment describing the setting if available
                    comment = self._get_config_comment(key)
                    if comment:
                        f.write(f"# {comment}\n")

                    f.write(f"{env_key}={value_str}\n\n")

                print(f"Config template exported to {output_path}")
        except Exception as e:
            print(f"Error exporting config: {e}", file=sys.stderr)

    def _get_config_comment(self, key: str) -> str:
        """Get the comment for a config variable from the config.py file."""
        # This is a simple implementation; for better comments, you could parse the config.py file
        if key == "ACCEL_COLOR_NEGATIVE":
            return "Color for negative acceleration display (red)"
        elif key == "ACCEL_COLOR_POSITIVE":
            return "Color for positive acceleration display (green)"
        elif key == "ACCEL_MAX":
            return "Maximum acceleration value in m/s² for displays"
        elif key == "ACCEL_MIN":
            return "Minimum acceleration value in m/s² for displays"
        elif key == "ACCENT_COLOR":
            return "Primary accent color for the UI (blue)"
        elif key == "ATTITUDE_UPDATE_INTERVAL":
            return "Update interval in milliseconds for attitude displays"
        elif key == "BACKGROUND_COLOR":
            return "Main application background color (dark gray)"
        elif key == "BEZEL_BORDER_COLOR":
            return "Border color for instrument bezels (darker gray)"
        elif key == "BEZEL_COLOR":
            return "Background color for instrument bezels (medium gray)"
        elif key == "CSV_PATH":
            return "Path for storing received vehicle data CSV file"
        elif key == "DANGER_COLOR":
            return "Color used for dangerous or critical values (red)"
        elif key == "DEBUG_MODE":
            return "Enable for development and debugging mode"
        elif key == "DEFAULT_CENTER":
            return "Default map center coordinates (longitude,latitude) - Kennedy Space Center area"
        elif key == "DEFAULT_DATA_SOURCE":
            return "Default data source for vehicle data (simulated or websocket)"
        elif key == "DEFAULT_ZOOM":
            return "Default zoom level for maps (1-19, higher means more zoomed in)"
        elif key == "DETAILMAP_DEFAULT_STYLE":
            return "Default map style for detailed map view (satellite or street)"
        elif key == "GG_DIAGRAM_MAX_G":
            return "Maximum G force to display in GG diagram (lateral/longitudinal acceleration)"
        elif key == "GG_DIAGRAM_MIN_G":
            return "Minimum G force to display in GG diagram (lateral/longitudinal acceleration)"
        elif key == "GG_DIAGRAM_UPDATE_INTERVAL":
            return "Update interval in milliseconds for GG diagram"
        elif key == "GPS_UPDATE_INTERVAL":
            return "GPS update interval in milliseconds"
        elif key == "HEADING_COLOR":
            return "Color for heading indicator (red)"
        elif key == "MAPBOX_TOKEN":
            return "Your Mapbox API token for map services"
        elif key == "MAP_BACKGROUND_COLOR":
            return "Background color for map displays (dark gray)"
        elif key == "MAP_BUTTON_ACTIVE_STYLE":
            return "CSS style for active map style button"
        elif key == "MAP_BUTTON_INACTIVE_STYLE":
            return "CSS style for inactive map style button"
        elif key == "MAP_GRID_COLOR":
            return "Grid line color for map overlays (light gray)"
        elif key == "MAP_GRID_OPACITY":
            return "Opacity value (0-255) for map grid overlay"
        elif key == "MAP_TILE_URLS":
            return "URLs for different map tile styles (OpenStreetMap for street, Bing Maps for satellite)"
        elif key == "MAP_UPDATE_INTERVAL":
            return "Update interval in milliseconds for maps"
        elif key == "MINIMAP_DEFAULT_STYLE":
            return "Default map style for minimap (satellite or street)"
        elif key == "PITCH_MAX":
            return "Maximum pitch angle in degrees"
        elif key == "PITCH_MIN":
            return "Minimum pitch angle in degrees"
        elif key == "PITCH_POINTER_COLOR":
            return "Color for pitch indicator pointer (amber)"
        elif key == "ROLL_MAX":
            return "Maximum roll angle in degrees"
        elif key == "ROLL_MIN":
            return "Minimum roll angle in degrees"
        elif key == "ROLL_POINTER_COLOR":
            return "Color for roll indicator pointer (cyan)"
        elif key == "SPEED_COLOR":
            return "Color for speed display (green)"
        elif key == "SPEED_MAX":
            return "Maximum speed value in display units (likely mph or km/h)"
        elif key == "SPEED_MIN":
            return "Minimum speed value in display units"
        elif key == "SPEED_UPDATE_INTERVAL":
            return "Speed update interval in milliseconds"
        elif key == "SUCCESS_COLOR":
            return "Color used for success indicators (green)"
        elif key == "TEXT_COLOR":
            return "Default text color (off-white)"
        elif key == "TILE_SIZE":
            return "Standard map tile size in pixels"
        elif key == "TIRE_FORCE_COLOR_HIGH":
            return "Color for high tire force values (red)"
        elif key == "TIRE_FORCE_COLOR_LIME":
            return "Color for lime tier tire force values (bright lime)"
        elif key == "TIRE_FORCE_COLOR_LOW":
            return "Color for low tire force values (green)"
        elif key == "TIRE_FORCE_COLOR_NORMAL":
            return "Color for normal tire force values (yellow)"
        elif key == "TIRE_FORCE_COLOR_ORANGE":
            return "Color for orange tier tire force values (orange)"
        elif key == "TIRE_FORCE_MAX":
            return "Maximum tire force value in Newtons"
        elif key == "TIRE_FORCE_MIN":
            return "Minimum tire force value in Newtons"
        elif key == "TIRE_FORCE_NORMAL":
            return "Normal/reference tire force value in Newtons"
        elif key == "TIRE_FORCE_UPDATE_INTERVAL":
            return "Update interval in milliseconds for tire force display"
        elif key == "TRAJECTORY_LINE_WIDTH":
            return "Width of trajectory lines on maps in pixels"
        elif key == "WARNING_COLOR":
            return "Color used for warning indicators (yellow)"
        elif key == "WS_HOST":
            return "Hostname for WebSocket server"
        elif key == "WS_PORT":
            return "Port for WebSocket server"
        elif key == "WS_RECONNECT_INTERVAL":
            return "Milliseconds between reconnection attempts for WebSocket"
        elif key == "WS_URI":
            return "Full WebSocket URI (usually ws://hostname:port)"
        # Add more comments as needed
        return ""


# Create global instance for easy import
config_manager = ConfigManager()


def get_config(key: str, default: Any = None) -> Any:
    """
    Get a configuration value.

    Args:
        key: The configuration key
        default: Default value if key doesn't exist

    Returns:
        The configuration value
    """
    return config_manager.config_vars.get(key, default)
