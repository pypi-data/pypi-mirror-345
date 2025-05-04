"""
Mapbox view widget with interactive map.
Uses Folium for interactive maps with native mouse drag, zoom, and pan.
"""

import folium
from folium import plugins
from PyQt5.QtCore import QDateTime, Qt, QTimer, QUrl
from PyQt5.QtWebEngineWidgets import (
    QWebEngineScript,
    QWebEngineSettings,
    QWebEngineView,
)
from PyQt5.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget

from force_fusion import config


class MapboxView(QWidget):
    """
    Widget that displays an interactive Mapbox map.

    Features:
    - Interactive map using Folium with native mouse controls
    - Vehicle position updating in real-time
    - Time display
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
        self._layout.setSpacing(5)

        # Initialize position variables
        self._current_lat = config.DEFAULT_CENTER[1]
        self._current_lon = config.DEFAULT_CENTER[0]
        self._current_heading = 0.0

        # Flag to track if map is ready
        self._map_ready = False

        # For performance tracking
        self._pos_update_count = 0

        # Create status panel
        self._status_panel = QLabel()
        self._status_panel.setStyleSheet(
            f"background-color: {config.BACKGROUND_COLOR}; "
            f"color: {config.TEXT_COLOR}; "
            "border: 1px solid #555; "
            "border-radius: 4px; "
            "padding: 8px; "
            "font-weight: bold;"
        )
        self._status_panel.setText("Loading map...")
        self._status_panel.setAlignment(Qt.AlignCenter)
        self._status_panel.setFixedHeight(50)  # Fixed height for status panel

        # Check if the token is set
        if config.MAPBOX_TOKEN == "YOUR_MAPBOX_TOKEN_HERE":
            # Token not set, show placeholder instead
            self._setup_placeholder(
                "Interactive Map View\n\n"
                "Please set your Mapbox token in a .env file to activate this feature."
            )
        else:
            self._setup_map()

        # Add status panel at the bottom
        self._layout.addWidget(self._status_panel)

        # Timer to update status
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._update_status_panel)
        self._update_timer.start(1000)  # Update every second

        # Store start time for elapsed time calculation
        self._start_time = QDateTime.currentMSecsSinceEpoch()

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

    def _update_status_panel(self):
        """Update the status panel with current information."""
        time_now = QDateTime.currentDateTime().toString("hh:mm:ss")

        # Format elapsed time
        elapsed_secs = (QDateTime.currentMSecsSinceEpoch() - self._start_time) / 1000
        hours = int(elapsed_secs // 3600)
        minutes = int((elapsed_secs % 3600) // 60)
        seconds = int(elapsed_secs % 60)
        elapsed = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        # Update status text - removed connection status since it's already shown in the top corner
        status_html = f"""
        <table width="100%">
            <tr>
                <td width="50%"><b>Position:</b> {self._current_lat:.6f}, {self._current_lon:.6f}</td>
                <td width="50%"><b>Time:</b> {time_now}</td>
            </tr>
            <tr>
                <td><b>Heading:</b> {self._current_heading:.1f}°</td>
                <td><b>Elapsed:</b> {elapsed}</td>
            </tr>
        </table>
        """
        self._status_panel.setText(status_html)

    def _setup_map(self):
        """Set up the interactive Folium map with Mapbox tiles."""
        # Create the WebEngineView if it doesn't exist yet
        if not hasattr(self, "_web_view"):
            # -------- Configure Warning Suppression --------
            # Inject script to suppress WebKit warnings before anything else
            script = QWebEngineScript()
            script.setName("WarningSuppressionScript")
            script.setSourceCode("""
            // Suppress WebKit storage deprecation warnings
            Object.defineProperty(window, 'webkitStorageInfo', {
                get: function() { 
                    return undefined; 
                },
                configurable: true
            });
            """)
            script.setWorldId(QWebEngineScript.MainWorld)
            script.setInjectionPoint(QWebEngineScript.DocumentCreation)
            script.setRunsOnSubFrames(True)

            # Create the WebEngineView
            self._web_view = QWebEngineView()
            self._web_view.setContextMenuPolicy(Qt.NoContextMenu)

            # Add the script to the page
            self._web_view.page().scripts().insert(script)

            # Configure WebEngine settings
            settings = self._web_view.settings()
            settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
            settings.setAttribute(
                QWebEngineSettings.LocalContentCanAccessRemoteUrls, True
            )
            settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
            settings.setAttribute(
                QWebEngineSettings.ErrorPageEnabled, False
            )  # Disable error pages

            # Connect to loadFinished signal
            self._web_view.loadFinished.connect(self._on_map_loaded)

            # Add WebView to layout
            self._layout.addWidget(self._web_view)

        # Create map HTML content
        map_html = self._generate_map_html()
        # Load HTML directly into the view
        self._web_view.setHtml(
            map_html, QUrl("qrc:/")
        )  # Use qrc:/ as base URL for local resources

    def _on_map_loaded(self, success):
        """Called when the map has finished loading."""
        if success:
            self._map_ready = True
            # Add a small delay to ensure DOM is ready
            QTimer.singleShot(100, self._inject_direct_update_function)
        else:
            print("Error: Map failed to load")

    def _inject_direct_update_function(self):
        """Inject a simple direct update function into the page."""
        if not hasattr(self, "_web_view"):
            return

        # Simple JavaScript to add a direct update function
        js_code = """
        // First find the map object - it's not directly exposed as a global variable
        window.getMapObject = function() {
            // In Folium, the map is typically stored in a variable controlled by an IIFE
            // We can find it by looking for the Leaflet map instance in the document
            var maps = [];
            for (var key in window) {
                if (window[key] && 
                    window[key] instanceof Object && 
                    window[key]._container && 
                    window[key] instanceof L.Map) {
                    maps.push(window[key]);
                }
            }
            
            // If we found exactly one map, return it
            if (maps.length === 1) {
                console.log("Found map object successfully");
                return maps[0];
            } else if (maps.length > 1) {
                console.log("Found multiple map objects, using first one");
                return maps[0];
            } else {
                console.error("No map object found");
                return null;
            }
        };
        
        // Cache references to important objects for better performance
        window.mapCache = {
            map: null,
            marker: null,
            vehicleDiv: null,
            markerElement: null,
            lastLat: 0,
            lastLon: 0,
            lastHeading: 0,  // Track the last heading
            initialized: false
        };
        
        // Initialize the cache
        window.initializeCache = function() {
            try {
                var map = window.getMapObject();
                if (!map) return false;
                
                window.mapCache.map = map;
                window.mapCache.initialized = true;
                
                // Find the marker
                map.eachLayer(function(layer) {
                    if (layer instanceof L.Marker) {
                        window.mapCache.marker = layer;
                        
                        // Get vehicle element for rotation
                        window.mapCache.markerElement = layer.getElement();
                        if (window.mapCache.markerElement) {
                            window.mapCache.vehicleDiv = window.mapCache.markerElement.querySelector("#vehicle-marker");
                            
                            // Add transition for smooth rotation if not already added
                            if (window.mapCache.vehicleDiv) {
                                window.mapCache.vehicleDiv.style.transition = "transform 0.5s ease-out";
                            }
                        }
                    }
                });
                
                console.log("Map cache initialized:", 
                    window.mapCache.map ? "Map ✓" : "Map ✗",
                    window.mapCache.marker ? "Marker ✓" : "Marker ✗",
                    window.mapCache.vehicleDiv ? "VehicleDiv ✓" : "VehicleDiv ✗"
                );
                
                return true;
            } catch (e) {
                console.error("Error initializing cache:", e);
                window.mapCache.initialized = false;
                return false;
            }
        };
        
        // Define a global updateVehicle function that directly manipulates the marker
        window.updateVehicle = function(lat, lon, heading) {
            try {
                // Initialize cache if needed
                if (!window.mapCache.initialized || !window.mapCache.map) {
                    if (!window.initializeCache()) {
                        return false;
                    }
                }
                
                // Skip update if there's no marker
                if (!window.mapCache.marker) {
                    return false;
                }
                
                // Update marker position if it has changed
                if (window.mapCache.lastLat !== lat || window.mapCache.lastLon !== lon) {
                    window.mapCache.marker.setLatLng([lat, lon]);
                    window.mapCache.lastLat = lat;
                    window.mapCache.lastLon = lon;
                }
                
                // Update rotation ONLY if heading has changed by at least 0.5 degrees
                // Using a higher threshold to reduce unnecessary rotations
                if (window.mapCache.vehicleDiv && Math.abs(window.mapCache.lastHeading - heading) > 0.5) {
                    window.mapCache.vehicleDiv.style.transform = "rotate(" + heading + "deg)";
                    window.mapCache.lastHeading = heading;
                }
                
                return true;
            } catch (e) {
                console.error("Error updating marker:", e);
                // Attempt to reinitialize if there was an error
                window.mapCache.initialized = false;
                return false;
            }
        };
        
        // Initialize cache immediately
        window.initializeCache();
        console.log("Direct update functions injected successfully");
        """

        self._web_view.page().runJavaScript(js_code)

        # Start a timer to update the vehicle position regularly
        self._update_position_timer = QTimer(self)
        self._update_position_timer.timeout.connect(self._update_vehicle_position)
        self._update_position_timer.start(
            50
        )  # Update very quickly for responsive movement

    def _update_vehicle_position(self):
        """Send the current position to the map."""
        if not self._map_ready or not hasattr(self, "_web_view"):
            return

        # Increment update counter for performance tracking
        self._pos_update_count += 1

        # Always update the vehicle position and rotation (fast updates)
        js_code = f"""
        if (typeof window.updateVehicle === 'function') {{
            window.updateVehicle({self._current_lat}, {self._current_lon}, {self._current_heading});
        }}
        """
        self._web_view.page().runJavaScript(js_code)

    def _generate_map_html(self):
        """Create a Folium map with the current position and return the HTML content."""
        # Create a Folium map
        m = folium.Map(
            location=[self._current_lat, self._current_lon],
            zoom_start=18,  # Closer zoom to better see the vehicle
            tiles=None,  # No default tiles, we'll add Mapbox tiles
            control_scale=True,
        )

        # Add map layers
        self._add_map_layers(m)

        # Add vehicle marker
        self._add_vehicle_marker(m)

        # Return the HTML representation of the map
        return m.get_root().render()

    def _add_map_layers(self, m):
        """Add map layers to the Folium map."""
        # Add all other layers first (not as default)
        folium.TileLayer(
            tiles=f"https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/{{z}}/{{x}}/{{y}}?access_token={config.MAPBOX_TOKEN}",
            attr="Mapbox",
            name="Streets",
            overlay=False,
            show=False,  # Not shown by default
            control=True,
        ).add_to(m)

        folium.TileLayer(
            tiles=f"https://api.mapbox.com/styles/v1/mapbox/dark-v11/tiles/{{z}}/{{x}}/{{y}}?access_token={config.MAPBOX_TOKEN}",
            attr="Mapbox",
            name="Dark",
            overlay=False,
            show=False,  # Not shown by default
            control=True,
        ).add_to(m)

        folium.TileLayer(
            tiles=f"https://api.mapbox.com/styles/v1/mapbox/light-v11/tiles/{{z}}/{{x}}/{{y}}?access_token={config.MAPBOX_TOKEN}",
            attr="Mapbox",
            name="Light",
            overlay=False,
            show=False,  # Not shown by default
            control=True,
        ).add_to(m)

        folium.TileLayer(
            tiles=f"https://api.mapbox.com/styles/v1/mapbox/navigation-day-v1/tiles/{{z}}/{{x}}/{{y}}?access_token={config.MAPBOX_TOKEN}",
            attr="Mapbox",
            name="Navigation Day",
            overlay=False,
            show=False,  # Not shown by default
            control=True,
        ).add_to(m)

        folium.TileLayer(
            tiles=f"https://api.mapbox.com/styles/v1/mapbox/navigation-night-v1/tiles/{{z}}/{{x}}/{{y}}?access_token={config.MAPBOX_TOKEN}",
            attr="Mapbox",
            name="Navigation Night",
            overlay=False,
            show=False,  # Not shown by default
            control=True,
        ).add_to(m)

        # Add Satellite LAST - this makes it the default visible layer
        satellite = folium.TileLayer(
            tiles=f"https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v12/tiles/{{z}}/{{x}}/{{y}}?access_token={config.MAPBOX_TOKEN}",
            attr="Mapbox",
            name="Satellite",
            overlay=False,
            control=True,
        )
        satellite.add_to(m)

        # Add layer control to switch between map styles
        folium.LayerControl().add_to(m)

        # Add measure tool for distance measurement
        plugins.MeasureControl(
            position="topright", primary_length_unit="meters"
        ).add_to(m)

        # Add fullscreen button
        plugins.Fullscreen(position="topright").add_to(m)

        # Add locate control to find user's location
        plugins.LocateControl().add_to(m)

    def _add_vehicle_marker(self, m):
        """Add a vehicle marker to the map."""
        # Create HTML for the marker with rotation
        rotation_style = f"transform: rotate({self._current_heading}deg); transition: transform 0.5s ease-out;"

        # Use the accent color from config
        marker_color = config.ACCENT_COLOR

        # Make the marker larger and more visible
        icon_html = f"""
            <div style="text-align:center;">
                <div id="vehicle-marker" style="
                    display: inline-block; 
                    width: 16px; 
                    height: 32px; 
                    background-color: {marker_color}; 
                    border: 2px solid white;
                    border-radius: 2px;
                    transform-origin: center; 
                    {rotation_style}">
                </div>
            </div>
        """

        # Create a DivIcon with the HTML content
        icon = folium.DivIcon(
            html=icon_html,
            icon_size=(30, 30),
            icon_anchor=(15, 15),
        )

        # Add marker to map
        folium.Marker(
            location=[self._current_lat, self._current_lon],
            icon=icon,
            tooltip=f"Position: {self._current_lat:.6f}, {self._current_lon:.6f}<br>Heading: {self._current_heading:.1f}°",
        ).add_to(m)

    def update_position(self, lat, lon):
        """
        Update the map to show a new position.

        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees
        """
        # Update stored position
        self._current_lat = lat
        self._current_lon = lon

    def update_heading(self, heading):
        """Update the vehicle heading on the map."""
        # Update stored heading
        self._current_heading = heading

    def update_pitch(self, pitch):
        """Update the vehicle pitch on the map."""
        # We don't use pitch for the map view, but store it for completeness
        self._current_pitch = pitch

    def update_roll(self, roll):
        """Update the vehicle roll on the map."""
        # We don't use roll for the map view, but store it for completeness
        self._current_roll = roll

    def update_pose(self, latitude, longitude, heading, pitch, roll):
        """Update all vehicle position and orientation parameters at once."""
        # Update stored values
        self._current_lat = latitude
        self._current_lon = longitude
        self._current_heading = heading
        self._current_pitch = pitch
        self._current_roll = roll

    def closeEvent(self, event):
        """Handle widget close event to clean up."""
        # Stop update timer
        if hasattr(self, "_update_timer"):
            self._update_timer.stop()

        # Stop position update timer
        if hasattr(self, "_update_position_timer"):
            self._update_position_timer.stop()

        super().closeEvent(event)
