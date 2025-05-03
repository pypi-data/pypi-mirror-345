"""
Mapbox view widget with 3D map and car model.
Uses Mapbox GL JS and ThreeBox for 3D visualization.
Includes WebSocket server to stream vehicle data.
"""

import asyncio
import json
import os
import random
from threading import Thread

# Set critical environment variables before importing Qt for WebGL support
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
    "--enable-webgl --ignore-gpu-blocklist --enable-gpu-rasterization "
    "--enable-native-gpu-memory-buffers --enable-zero-copy --no-sandbox"
)
os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
# Force OpenGL acceleration
os.environ["QT_OPENGL"] = "desktop"
# Debugging info
os.environ["QT_OPENGL_DEBUG"] = "1"

import websockets
from PyQt5.QtCore import QCoreApplication, Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineSettings, QWebEngineView
from PyQt5.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget

from force_fusion import config


def check_opengl():
    """Check if OpenGL is properly set up."""
    try:
        import subprocess

        subprocess.run(
            ["glxinfo", "|", "grep", "OpenGL"],
            shell=True,
            capture_output=True,
            text=True,
        )
        print("OpenGL check passed")
        return True
    except Exception as e:
        print(f"Failed to check OpenGL: {e}")
        return False


# Set QtWebEngine command line args for GPU and rendering via QCoreApplication
def set_webengine_args():
    """Set QWebEngine command line arguments for better GPU performance."""
    # Qt WebEngine args need to be set before QApplication is created
    # For PyQt5 versions that don't have setWebEngineArguments
    args = [
        "--enable-gpu-rasterization",
        "--enable-accelerated-2d-canvas",
        "--enable-zero-copy",
        "--ignore-gpu-blocklist",
        "--enable-hardware-overlays",
        "--enable-features=VaapiVideoDecoder",
        "--disable-features=UseOzonePlatform",
        "--disable-gpu-driver-bug-workarounds",
        "--no-sandbox",
        "--enable-webgl",
    ]

    # Check if we're running within an existing QApplication
    if QCoreApplication.instance():
        print("QApplication already exists, skipping WebEngine arguments")
    else:
        # Set args via environment variable as an alternative
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join(args)
        # Additional environment variables to enable WebGL
        os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"  # Disable sandbox for testing
        print("Set WebEngine args via environment variable")

    # Print WebGL support information
    print(f"OpenGL vendor string: {os.environ.get('QT_OPENGL_DEBUG')}")
    check_opengl()


# Call this function before creating any QWebEngineView
set_webengine_args()


class WebSocketServer:
    """WebSocket server to broadcast vehicle data to connected clients."""

    def __init__(self, port=8051):
        """Initialize the WebSocket server.

        Args:
            port: Port number for the WebSocket server
        """
        self.port = port
        self.connected_clients = set()
        self.server = None
        self.running = False

        # Ensure DEFAULT_CENTER is numeric
        default_center = config.DEFAULT_CENTER
        if isinstance(default_center, (list, tuple)) and len(default_center) >= 2:
            # Convert to float if they're strings
            lon = (
                float(default_center[0])
                if not isinstance(default_center[0], (int, float))
                else default_center[0]
            )
            lat = (
                float(default_center[1])
                if not isinstance(default_center[1], (int, float))
                else default_center[1]
            )
        else:
            # Default values if config is invalid
            lon, lat = -81.04897348153887, 29.18825368942673
            print("Warning: Invalid DEFAULT_CENTER config, using default values")

        # Lon/Lat boundaries for random data generation
        self.lon_min = lon - 0.01
        self.lon_max = lon + 0.01
        self.lat_min = lat - 0.01
        self.lat_max = lat + 0.01

        # Initial position and orientation
        self.latitude = self.lat_min + (self.lat_max - self.lat_min) / 2
        self.longitude = self.lon_min + (self.lon_max - self.lon_min) / 2
        self.heading = 0.0
        self.pitch = 0.0
        self.roll = 0.0

        # Create a thread for the asyncio event loop
        self.loop = asyncio.new_event_loop()
        self.thread = Thread(target=self._run_server, daemon=True)

    def _run_server(self):
        """Run the asyncio event loop in a separate thread."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _handler(self, websocket):
        """Handle new WebSocket connections.

        Args:
            websocket: WebSocket connection
        """
        remote_address = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        print(f"[WS] New client connected: {remote_address}")
        self.connected_clients.add(websocket)

        try:
            # Send initial data right away to this client
            await self._send_data(websocket)

            # Keep connection open
            await websocket.wait_closed()
        except websockets.exceptions.ConnectionClosedError:
            print(f"[WS] Connection closed with error: {remote_address}")
        except Exception as e:
            print(f"[WS] Error with client {remote_address}: {e}")
        finally:
            print(f"[WS] Client disconnected: {remote_address}")
            self.connected_clients.remove(websocket)

    async def _start_server(self):
        """Start the WebSocket server."""
        self.server = await websockets.serve(self._handler, "0.0.0.0", self.port)
        self.running = True
        print(f"[WS] Server started on port {self.port}")

    async def _broadcast_data(self):
        """Generate and broadcast vehicle data to all connected clients."""
        while self.running:
            if not self.connected_clients:
                await asyncio.sleep(0.1)
                continue

            # Send data to all clients
            broadcast_tasks = [
                self._send_data(client) for client in self.connected_clients
            ]
            if broadcast_tasks:
                await asyncio.gather(*broadcast_tasks)

            # Wait before next update
            await asyncio.sleep(1)

    async def _send_data(self, websocket):
        """Send vehicle data to a specific client."""
        try:
            # Generate random movement within bounds
            self.longitude += random.uniform(-0.00005, 0.00005)
            self.latitude += random.uniform(-0.00005, 0.00005)

            # Keep within bounds
            self.longitude = max(self.lon_min, min(self.lon_max, self.longitude))
            self.latitude = max(self.lat_min, min(self.lat_max, self.latitude))

            # Update heading, pitch, and roll with small changes
            self.heading = (self.heading + random.uniform(-1, 1)) % 360
            self.pitch = max(-10, min(10, self.pitch + random.uniform(-0.5, 0.5)))
            self.roll = max(-10, min(10, self.roll + random.uniform(-0.5, 0.5)))

            # Format data in the expected format for map.html
            data = {
                "droneCoords": [[f"{self.longitude},{self.latitude},0"]],
                "droneNames": [["Vehicle"]],
                "dronePitch": [[str(self.pitch)]],
                "droneYaw": [[str(self.heading)]],
                "droneRoll": [[str(self.roll)]],
            }

            # Convert to JSON and send to client
            json_data = json.dumps(data)
            await websocket.send(json_data)
            print(f"[WS] Sent: {self.latitude:.6f}, {self.longitude:.6f}")

        except Exception as e:
            print(f"[WS] Error sending data: {e}")

    def start(self):
        """Start the WebSocket server and data broadcasting."""
        self.thread.start()
        self.server_task = asyncio.run_coroutine_threadsafe(
            self._start_server(), self.loop
        )
        self.broadcast_task = asyncio.run_coroutine_threadsafe(
            self._broadcast_data(), self.loop
        )

    def stop(self):
        """Stop the WebSocket server."""
        if self.running:
            self.running = False
            if hasattr(self, "broadcast_task") and self.broadcast_task:
                self.broadcast_task.cancel()
            if self.server:
                self.server.close()
            self.loop.call_soon_threadsafe(self.loop.stop)


class MapboxView(QWidget):
    """
    Widget that displays a 3D Mapbox map with a car model.

    Features:
    - Interactive 3D map using Mapbox GL JS
    - Vehicle position updating in real-time over WebSocket
    - Vehicle model with correct orientation (heading, pitch, roll)
    - Terrain-based visualization
    """

    def __init__(self, parent=None):
        """
        Initialize the Mapbox view widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Set widget properties
        self.setMinimumSize(400, 300)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        # Initialize WebSocket server
        self.ws_server = WebSocketServer()

        # Check if the token is set
        if config.MAPBOX_TOKEN == "YOUR_MAPBOX_TOKEN_HERE":
            # Token not set, show placeholder instead
            self._setup_placeholder(
                "3D Live Mapbox Map with 3D Car Model\n\n"
                "Please set your Mapbox token in config.py to activate this feature."
            )
        else:
            # Token is set, initialize the Mapbox view
            self._setup_mapbox_view()

            # Start WebSocket server
            self.ws_server.start()

    def _setup_placeholder(self, message):
        """Set up a placeholder for when the Mapbox token is not set or error occurred."""
        self._placeholder = QLabel(message)
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._placeholder.setStyleSheet(
            f"color: {config.TEXT_COLOR}; "
            f"background-color: {config.BACKGROUND_COLOR}; "
            "border: 1px solid #555; "
            "border-radius: 4px; "
            "padding: 10px;"
        )
        self._layout.addWidget(self._placeholder)

    def _setup_mapbox_view(self):
        """Set up the Mapbox WebEngineView with the map."""
        # Create the WebEngineView
        self._web_view = QWebEngineView()

        # Set window flags for better rendering
        self._web_view.setContextMenuPolicy(Qt.NoContextMenu)

        # Configure WebEngine settings for maximum performance
        settings = self._web_view.settings()

        # Enable WebGL and other required settings
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        settings.setAttribute(QWebEngineSettings.SpatialNavigationEnabled, True)

        # Enhanced WebGL support
        try:
            settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
            settings.setAttribute(
                QWebEngineSettings.AcceleratedCompositingEnabled, True
            )
            settings.setAttribute(QWebEngineSettings.XSSAuditingEnabled, False)
        except AttributeError:
            # Some attributes might not be available in all PyQt versions
            pass

        # Try to set additional settings that might not be available in all PyQt versions
        for attr_name, attr_value in [
            ("PluginsEnabled", True),
            ("FullScreenSupportEnabled", True),
            ("ShowScrollBars", False),
        ]:
            try:
                attr = getattr(QWebEngineSettings, attr_name)
                settings.setAttribute(attr, attr_value)
            except AttributeError:
                pass

        # Get the path to the HTML file
        CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))  # widgets/
        RESOURCE_DIR = os.path.abspath(
            os.path.join(CURRENT_DIR, "..", "resources")
        )  # force_fusion/resources
        html_path = os.path.join(RESOURCE_DIR, "map.html")

        try:
            # Read the HTML content
            with open(html_path, "r") as f:
                html_content = f.read()

            # Replace only the token if needed - no style replacement
            if "YOUR_MAPBOX_TOKEN_HERE" in html_content:
                html_content = html_content.replace(
                    "YOUR_MAPBOX_TOKEN_HERE", config.MAPBOX_TOKEN
                )

                # Write the modified HTML back to the file
                with open(html_path, "w") as f:
                    f.write(html_content)

            # Get absolute path and convert to proper URL
            absolute_path = os.path.abspath(html_path)
            file_url = QUrl.fromLocalFile(absolute_path)

            # Set up JavaScript error handler
            self._web_view.page().javaScriptConsoleMessage = self._handle_js_console

            # Load the HTML file directly using the file URL
            self._web_view.load(file_url)

            print(f"Loading map content directly from file: {absolute_path}")

            # Register callback to check WebGL initialization after page load
            self._web_view.loadFinished.connect(self._check_webgl_initialization)

            # Add to layout
            self._layout.addWidget(self._web_view)

        except Exception as e:
            print(f"Error loading map.html: {e}")
            self._setup_placeholder(f"Error loading map: {e}")

    def _check_webgl_initialization(self, success):
        """Check if WebGL initialization was successful, show error if not."""
        if success:
            # Run JavaScript to check if WebGL initialization succeeded
            script = """
            (function() {
                try {
                    // Try to create a WebGL context
                    var canvas = document.createElement('canvas');
                    var gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
                    if (!gl) {
                        return "WebGL is not supported by your browser/hardware";
                    }
                    
                    // Check if map initialized
                    if (!window.map) {
                        return "MapboxGL failed to initialize";
                    }
                    
                    // Return WebGL information for debugging
                    var debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                    if (debugInfo) {
                        return "WebGL OK: " + 
                            gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) + " - " + 
                            gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                    }
                    
                    // All good
                    return "";
                } catch (e) {
                    return "WebGL error: " + e.message;
                }
            })();
            """

            self._web_view.page().runJavaScript(script, self._handle_webgl_check_result)

    def _handle_webgl_check_result(self, result):
        """Handle the result of WebGL initialization check."""
        if result:
            if result.startswith("WebGL OK"):
                print(f"WebGL initialization successful: {result}")
            else:
                print(f"WebGL initialization failed: {result}")

                # Remove the web view
                if hasattr(self, "_web_view"):
                    self._web_view.setVisible(False)
                    self._layout.removeWidget(self._web_view)
                    self._web_view.deleteLater()
                    self._web_view = None

                # Show error message
                self._setup_placeholder(
                    f"3D Map Error\n\nWebGL initialization failed: {result}\n\nPlease ensure your system supports hardware-accelerated graphics."
                )

    def _handle_js_console(self, level, message, line, source):
        """Handle JavaScript console messages."""
        print(f"JS: {message}")

        # Check for WebGL errors
        if "WebGL" in message and (
            "error" in message.lower() or "fail" in message.lower()
        ):
            print(f"WebGL error detected: {message}")
            # The _check_webgl_initialization will handle this

    def update_position(self, latitude, longitude):
        """
        Update the vehicle position on the map.

        Args:
            latitude: Latitude in degrees
            longitude: Longitude in degrees
        """
        self.ws_server.latitude = latitude
        self.ws_server.longitude = longitude

    def update_heading(self, heading):
        """
        Update the vehicle heading on the map.

        Args:
            heading: Heading in degrees (0-360)
        """
        self.ws_server.heading = heading

    def update_pitch(self, pitch):
        """
        Update the vehicle pitch on the map.

        Args:
            pitch: Pitch angle in degrees
        """
        self.ws_server.pitch = pitch

    def update_roll(self, roll):
        """
        Update the vehicle roll on the map.

        Args:
            roll: Roll angle in degrees
        """
        self.ws_server.roll = roll

    def update_pose(self, latitude, longitude, heading, pitch, roll):
        """
        Update all vehicle position and orientation parameters at once.

        Args:
            latitude: Latitude in degrees
            longitude: Longitude in degrees
            heading: Heading in degrees (0-360)
            pitch: Pitch angle in degrees
            roll: Roll angle in degrees
        """
        self.ws_server.latitude = latitude
        self.ws_server.longitude = longitude
        self.ws_server.heading = heading
        self.ws_server.pitch = pitch
        self.ws_server.roll = roll

    def closeEvent(self, event):
        """Handle widget close event to stop WebSocket server and clean up."""
        # Stop WebSocket server
        if hasattr(self, "ws_server"):
            self.ws_server.stop()

        super().closeEvent(event)
