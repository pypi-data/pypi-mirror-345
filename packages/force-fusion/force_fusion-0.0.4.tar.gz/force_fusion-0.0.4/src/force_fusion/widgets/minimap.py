"""
Minimap widget that displays a 2D trajectory of the vehicle's path.
"""

import math
import os
from threading import Lock

from PyQt5.QtCore import QObject, QRectF, Qt, QTimer, QUrl, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QImage, QPainter, QPainterPath, QPen
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from force_fusion import config


class TileManager(QObject):
    """
    Manages loading and caching map tiles from various providers.
    """

    tileLoaded = pyqtSignal(int, int, int, QImage)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.network_manager = QNetworkAccessManager(self)
        self.cache = {}  # Cache for loaded tiles
        self.pending_requests = {}
        self.cache_lock = Lock()

        # Tile server URLs - we'll use OpenStreetMap by default
        # Use http instead of https to avoid SSL/TLS issues
        self.tile_url_template = "http://tile.openstreetmap.org/{z}/{x}/{y}.png"

        # Create cache directory if it doesn't exist
        self.cache_dir = os.path.join(
            os.path.expanduser("~"), ".force_fusion", "tile_cache"
        )
        os.makedirs(self.cache_dir, exist_ok=True)

        # Use a placeholder image to avoid repeated network errors
        self.use_placeholder = True
        self.placeholder_image = None
        self._create_placeholder_image()

    def _create_placeholder_image(self):
        """Create a placeholder image to use when network is unavailable"""
        try:
            image = QImage(256, 256, QImage.Format_ARGB32)
            image.fill(QColor(config.BACKGROUND_COLOR))

            # Draw a simple grid pattern
            painter = QPainter(image)
            painter.setPen(QPen(QColor(80, 80, 80), 1))

            # Draw horizontal lines
            for y in range(0, 256, 32):
                painter.drawLine(0, y, 256, y)

            # Draw vertical lines
            for x in range(0, 256, 32):
                painter.drawLine(x, 0, x, 256)

            painter.end()

            self.placeholder_image = image
        except Exception as e:
            print(f"Error creating placeholder image: {e}")

    def get_tile(self, zoom, x, y):
        """
        Get a map tile for the specified coordinates.

        Args:
            zoom: Zoom level
            x: Tile x coordinate
            y: Tile y coordinate

        Returns:
            QImage of the tile if available in cache, None otherwise
            and starts loading the tile
        """
        # If using placeholder, return it immediately
        if self.use_placeholder and self.placeholder_image:
            return self.placeholder_image

        tile_key = f"{zoom}_{x}_{y}"

        # Check cache first
        with self.cache_lock:
            if tile_key in self.cache:
                return self.cache[tile_key]

        # Check if tile exists on disk
        tile_path = os.path.join(self.cache_dir, f"{tile_key}.png")
        if os.path.exists(tile_path):
            try:
                image = QImage(tile_path)
                if not image.isNull():
                    with self.cache_lock:
                        self.cache[tile_key] = image
                    return image
            except Exception as e:
                print(f"Error loading cached tile: {e}")

        # Tile not in cache, request it if not already pending
        if not self.use_placeholder and tile_key not in self.pending_requests:
            try:
                url = self.tile_url_template.format(z=zoom, x=x, y=y)
                request = QNetworkRequest(QUrl(url))
                reply = self.network_manager.get(request)

                # Store the reply and connect to its signals
                self.pending_requests[tile_key] = (reply, zoom, x, y)
                reply.finished.connect(
                    lambda: self._handle_tile_response(reply, zoom, x, y, tile_key)
                )
            except Exception as e:
                print(f"Error requesting tile: {e}")

        # Return placeholder if we have one
        if self.placeholder_image:
            return self.placeholder_image

        return None

    def _handle_tile_response(self, reply, zoom, x, y, tile_key):
        """Handle the network response for a tile request."""
        try:
            if reply.error() == QNetworkReply.NoError:
                # Read the image data
                image_data = reply.readAll()

                # Create a QImage from the data
                image = QImage()
                if image.loadFromData(image_data):
                    # Save to disk cache
                    tile_path = os.path.join(self.cache_dir, f"{tile_key}.png")
                    image.save(tile_path, "PNG")

                    # Update memory cache
                    with self.cache_lock:
                        self.cache[tile_key] = image

                    # Emit signal that tile is loaded
                    self.tileLoaded.emit(zoom, x, y, image)
            else:
                print(f"Error downloading tile: {reply.errorString()}")

            # Clean up
            if tile_key in self.pending_requests:
                del self.pending_requests[tile_key]

            reply.deleteLater()
        except Exception as e:
            print(f"Error handling tile response: {e}")


class MapDetailDialog(QDialog):
    """
    Dialog for showing a detailed map view.

    Opened when the user clicks on the minimap.
    """

    def __init__(self, parent=None, latitude=0, longitude=0, trajectory=None):
        super().__init__(parent)

        # Store parent reference for updates
        self._parent_widget = parent

        # Position data
        self.latitude = latitude
        self.longitude = longitude
        self.trajectory = trajectory if trajectory else []
        self.heading = 0

        # Set up dialog
        self.setWindowTitle("Detailed Map View")
        self.setMinimumSize(600, 500)
        self.setModal(False)

        # Main layout
        layout = QVBoxLayout(self)

        # Create map widget
        self.map_widget = QWidget()
        self.map_widget.setMinimumSize(580, 400)
        self.map_widget.paintEvent = self._paint_map
        layout.addWidget(self.map_widget)

        # Add controls below map
        control_layout = QHBoxLayout()

        # Zoom slider
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(10)
        self.zoom_slider.setMaximum(18)
        self.zoom_slider.setValue(config.DEFAULT_ZOOM)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        control_layout.addWidget(QLabel("Zoom:"))
        control_layout.addWidget(self.zoom_slider)

        # Add layout to main layout
        layout.addLayout(control_layout)

        # Map settings
        self.zoom = config.DEFAULT_ZOOM
        self.tile_manager = TileManager(self)
        self.tile_manager.tileLoaded.connect(self.update)

        # Timer to periodically update the dialog
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._update_from_parent)
        self._update_timer.start(config.MAP_UPDATE_INTERVAL)

        # Center the dialog on the screen
        center_point = parent.mapToGlobal(parent.rect().center())
        self.move(center_point.x() - 300, center_point.y() - 250)

    def on_zoom_changed(self, zoom):
        """Handle zoom slider value change."""
        self.zoom = zoom
        self.update()

    def _update_from_parent(self):
        """Update position and trajectory data from parent widget."""
        if self._parent_widget:
            self.latitude = self._parent_widget._latitude
            self.longitude = self._parent_widget._longitude
            self.trajectory = self._parent_widget._trajectory.copy()
            self.heading = self._parent_widget._heading
            self.update()

    def _paint_map(self, event):
        """Paint the detailed map view."""
        painter = QPainter(self.map_widget)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Get widget dimensions
        width = self.map_widget.width()
        height = self.map_widget.height()

        # Draw background
        painter.fillRect(0, 0, width, height, QColor(40, 40, 40))

        # Calculate tile coordinates for current view
        tiles = self._get_visible_tiles(width, height)

        # Draw tiles
        for tile_info in tiles:
            tile_zoom, tile_x, tile_y, screen_x, screen_y = tile_info

            # Try to get tile from cache
            tile_image = self.tile_manager.get_tile(tile_zoom, tile_x, tile_y)

            if tile_image:
                # Draw tile at specified position
                painter.drawImage(int(screen_x), int(screen_y), tile_image)
            else:
                # Draw placeholder for tiles not yet loaded
                painter.fillRect(
                    int(screen_x), int(screen_y), 256, 256, QColor(60, 60, 60)
                )
                painter.setPen(QColor(100, 100, 100))
                painter.drawRect(int(screen_x), int(screen_y), 256, 256)
                painter.drawText(
                    QRectF(screen_x, screen_y, 256, 256), Qt.AlignCenter, "Loading..."
                )

        # Draw trajectory
        if self.trajectory and len(self.trajectory) > 1:
            painter.setPen(QPen(QColor(config.ACCENT_COLOR), 3, Qt.SolidLine))

            path = QPainterPath()
            first = True

            for lat, lon in self.trajectory:
                px, py = self._geo_to_screen(lat, lon, width, height)

                if first:
                    path.moveTo(px, py)
                    first = False
                else:
                    path.lineTo(px, py)

            painter.drawPath(path)

        # Draw current position marker
        if self.latitude and self.longitude:
            px, py = self._geo_to_screen(self.latitude, self.longitude, width, height)

            # Draw circle for current position
            painter.setPen(QPen(Qt.white, 2))
            painter.setBrush(QColor(config.ACCENT_COLOR))
            painter.drawEllipse(int(px - 8), int(py - 8), 16, 16)

            # Draw direction arrow if we have trajectory points
            if len(self.trajectory) >= 2:
                # Calculate heading from last two points
                last = self.trajectory[-1]
                prev = self.trajectory[-2]

                # Calculate heading
                dx = last[1] - prev[1]  # longitude difference
                dy = last[0] - prev[0]  # latitude difference
                heading = math.degrees(math.atan2(dx, dy))

                # Draw arrow
                painter.save()
                painter.translate(px, py)
                painter.rotate(heading)  # Align rotation with HeadingWidget

                # Draw triangle
                arrow_path = QPainterPath()
                arrow_path.moveTo(0, -16)  # Top point
                arrow_path.lineTo(-8, 0)  # Bottom left
                arrow_path.lineTo(8, 0)  # Bottom right
                arrow_path.closeSubpath()

                painter.setBrush(QColor(255, 255, 255))
                painter.setPen(QPen(QColor(config.ACCENT_COLOR), 2))
                painter.drawPath(arrow_path)

                painter.restore()

        # Draw scale indicator
        self._draw_scale(painter, width, height)

        # Draw coordinates
        text = f"Lat: {self.latitude:.6f}  Lon: {self.longitude:.6f}  Zoom: {self.zoom}"
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(10, height - 10, text)

    def _geo_to_screen(self, lat, lon, width, height):
        """Convert geographic coordinates to screen coordinates."""
        # Calculate tile coordinates for the center of the screen
        center_tile_x, center_tile_y = self._geo_to_tile(lat, lon, self.zoom)

        # Calculate pixel offset within the center tile
        center_pixel_x = (center_tile_x - math.floor(center_tile_x)) * 256
        center_pixel_y = (center_tile_y - math.floor(center_tile_y)) * 256

        # Calculate screen coordinates
        screen_x = width / 2 - center_pixel_x
        screen_y = height / 2 - center_pixel_y

        return screen_x, screen_y

    def _get_visible_tiles(self, width, height):
        """
        Calculate which tiles are visible in the current view.

        Returns:
            List of (zoom, tile_x, tile_y, screen_x, screen_y) tuples
        """
        # Calculate the tile coordinates for the center of the view
        center_tile_x, center_tile_y = self._geo_to_tile(
            self.latitude, self.longitude, self.zoom
        )

        # Calculate the center tile's screen position
        center_tile_screen_x = (
            width / 2 - (center_tile_x - math.floor(center_tile_x)) * 256
        )
        center_tile_screen_y = (
            height / 2 - (center_tile_y - math.floor(center_tile_y)) * 256
        )

        # Calculate number of tiles needed to cover the view
        tiles_x = int(width / 256) + 2  # +2 to handle partial tiles at edges
        tiles_y = int(height / 256) + 2

        # Calculate the top-left tile coordinates
        start_tile_x = math.floor(center_tile_x) - tiles_x // 2
        start_tile_y = math.floor(center_tile_y) - tiles_y // 2

        # Calculate the screen position of the top-left tile
        start_screen_x = (
            center_tile_screen_x - (math.floor(center_tile_x) - start_tile_x) * 256
        )
        start_screen_y = (
            center_tile_screen_y - (math.floor(center_tile_y) - start_tile_y) * 256
        )

        # Generate the list of visible tiles
        visible_tiles = []

        for y in range(tiles_y):
            for x in range(tiles_x):
                tile_x = start_tile_x + x
                tile_y = start_tile_y + y

                # Skip invalid tile coordinates
                if (
                    tile_x < 0
                    or tile_y < 0
                    or tile_x >= 2**self.zoom
                    or tile_y >= 2**self.zoom
                ):
                    continue

                screen_x = start_screen_x + x * 256
                screen_y = start_screen_y + y * 256

                visible_tiles.append((self.zoom, tile_x, tile_y, screen_x, screen_y))

        return visible_tiles

    def _geo_to_tile(self, lat, lon, zoom):
        """
        Convert geographic coordinates to tile coordinates.

        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees
            zoom: Zoom level

        Returns:
            (tile_x, tile_y) as floating point
        """
        lat_rad = math.radians(lat)
        n = 2.0**zoom
        tile_x = (lon + 180.0) / 360.0 * n
        tile_y = (
            (1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi)
            / 2.0
            * n
        )

        return tile_x, tile_y

    def _draw_scale(self, painter, width, height):
        """Draw a scale indicator on the map."""
        # Calculate the length of 100 meters at current latitude and zoom
        meters_per_pixel = (
            156543.03392 * math.cos(math.radians(self.latitude)) / (2**self.zoom)
        )
        scale_width_pixels = 100 / meters_per_pixel

        # Adjust scale length to be a nice round number
        if scale_width_pixels < 20:
            scale_meters = 1000  # 1 km
        elif scale_width_pixels < 100:
            scale_meters = 500
        elif scale_width_pixels < 200:
            scale_meters = 200
        else:
            scale_meters = 100

        # Recalculate width in pixels for the chosen scale
        scale_width_pixels = int(scale_meters / meters_per_pixel)  # Convert to int

        # Draw scale bar
        scale_y = height - 30
        scale_x = 10

        painter.setPen(QPen(Qt.white, 2))
        painter.drawLine(scale_x, scale_y, scale_x + scale_width_pixels, scale_y)
        painter.drawLine(scale_x, scale_y - 5, scale_x, scale_y + 5)
        painter.drawLine(
            scale_x + scale_width_pixels,
            scale_y - 5,
            scale_x + scale_width_pixels,
            scale_y + 5,
        )

        # Draw label
        if scale_meters >= 1000:
            label = f"{scale_meters / 1000:.1f} km"
        else:
            label = f"{scale_meters} m"

        painter.drawText(scale_x + scale_width_pixels // 2 - 20, scale_y - 10, label)


class MinimapWidget(QWidget):
    """
    Widget that displays a 2D trajectory of the vehicle's path.

    Features:
    - Scrolling/zooming 2D map showing the vehicle's trajectory
    - Current position marker
    - Direction indicator
    - Satellite map background
    - Click to open detailed map view
    """

    def __init__(self, parent=None):
        """
        Initialize the minimap widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Current position
        self._latitude = config.DEFAULT_CENTER[1]  # Default latitude
        self._longitude = config.DEFAULT_CENTER[0]  # Default longitude
        self._heading = 0.0  # Heading in degrees

        # Trajectory history (list of lat/lon points)
        self._trajectory = []
        self._max_points = config.TRAJECTORY_HISTORY_LENGTH

        # Map view settings
        self._zoom = 1.0  # Zoom level
        self._center_on_vehicle = True  # Whether to keep vehicle centered

        # Cached data for efficient rendering
        self._map_scale = 0.0001  # Degrees per pixel
        self._centerx = 0
        self._centery = 0
        self._radius = 0

        # Set widget properties
        self.setMinimumSize(200, 200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(config.BACKGROUND_COLOR))
        self.setPalette(palette)

        # Create tile manager for satellite background
        self._tile_manager = TileManager(self)
        self._tile_manager.tileLoaded.connect(self.update)

        # Cache for the current background tiles
        self._background_tiles = []
        self._map_zoom = (
            config.DEFAULT_ZOOM
        )  # Map zoom level for tiles (different from widget zoom)

        # Set up cursor to indicate it's clickable
        self.setCursor(Qt.PointingHandCursor)

        # Detailed map dialog (created when needed)
        self._detail_dialog = None

    def update_position(self, latitude, longitude, heading=None):
        """
        Update the current position and add it to the trajectory.

        Args:
            latitude: Current latitude in degrees
            longitude: Current longitude in degrees
            heading: Heading angle in degrees (0-360, 0=North, 90=East)
        """
        self._latitude = latitude
        self._longitude = longitude

        if heading is not None:
            self._heading = heading

        # Add to trajectory
        self._trajectory.append((latitude, longitude))

        # Limit number of trajectory points
        if len(self._trajectory) > self._max_points:
            self._trajectory.pop(0)

        # If detail dialog is open, update it
        if self._detail_dialog and self._detail_dialog.isVisible():
            self._detail_dialog._update_from_parent()

        # Request a repaint
        self.update()

    def clear_trajectory(self):
        """Clear the trajectory history."""
        self._trajectory = []
        self.update()

    def set_zoom(self, zoom):
        """
        Set the zoom level.

        Args:
            zoom: Zoom level (1.0 = standard zoom)
        """
        self._zoom = max(0.1, min(10.0, zoom))
        self.update()

    def set_center_on_vehicle(self, center):
        """
        Set whether to keep the vehicle centered in the view.

        Args:
            center: True to center on vehicle, False to allow free panning
        """
        self._center_on_vehicle = center
        self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse click events to open detailed map view."""
        # Check if click was inside the minimap circle
        dx = event.x() - self._centerx
        dy = event.y() - self._centery
        distance = math.sqrt(dx * dx + dy * dy)

        if distance <= self._radius:
            # Open the detailed map dialog
            self._show_detail_map()

        super().mouseReleaseEvent(event)

    def _show_detail_map(self):
        """Show the detailed map dialog."""
        if not self._detail_dialog:
            self._detail_dialog = MapDetailDialog(
                self, self._latitude, self._longitude, self._trajectory.copy()
            )
        else:
            # Update position and trajectory
            self._detail_dialog.latitude = self._latitude
            self._detail_dialog.longitude = self._longitude
            self._detail_dialog.trajectory = self._trajectory.copy()

        self._detail_dialog.show()
        self._detail_dialog.raise_()
        self._detail_dialog.activateWindow()

    def paintEvent(self, event):
        """
        Paint the minimap.

        Args:
            event: Paint event
        """
        # Create painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get widget dimensions and calculate drawing area
        width = self.width()
        height = self.height()
        # Use the smaller dimension to define the diameter for a perfect circle
        diameter = min(width, height)
        radius = diameter // 2 - 10  # Subtract padding
        self._radius = radius  # Store for mouse event handling

        # Calculate the center based on the actual widget size
        widget_center_x = width // 2
        widget_center_y = height // 2

        # Define the drawing area (square centered in the widget)
        draw_rect = QRectF(
            widget_center_x - radius - 5,
            widget_center_y - radius - 5,
            diameter - 10,
            diameter - 10,
        )
        self._centerx = draw_rect.center().x()
        self._centery = draw_rect.center().y()

        # Draw background with satellite imagery
        self._draw_satellite_background(painter, self._centerx, self._centery, radius)

        # Draw coordinate grid within the circle
        self._draw_grid(painter, self._centerx, self._centery, radius)

        # Calculate map scale based on zoom
        self._map_scale = 0.0001 / self._zoom

        # Draw trajectory
        self._draw_trajectory(painter, width, height)

        # Draw current position marker
        self._draw_position_marker(painter, width, height)

        # Draw title
        painter.setPen(QColor(config.TEXT_COLOR))
        painter.setFont(QFont("Arial", 10))
        painter.drawText(QRectF(0, 5, width, 20), Qt.AlignCenter, "2D Minimap")

    def _draw_satellite_background(self, painter, center_x, center_y, radius):
        """Draw satellite imagery in the background circle."""
        # Create circular clipping path
        circle_path = QPainterPath()
        circle_path.addEllipse(
            center_x - radius, center_y - radius, radius * 2, radius * 2
        )

        painter.save()
        painter.setClipPath(circle_path)

        # Draw a basic background first
        painter.fillRect(
            QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2),
            QColor(30, 30, 30),
        )

        # Calculate tile coordinates for the current view
        if self._latitude != 0 and self._longitude != 0:
            # Calculate visible tile range
            tile_x, tile_y = self._geo_to_tile(
                self._latitude, self._longitude, self._map_zoom
            )

            # The span depends on the zoom and radius in pixels
            # Approximate tiles needed based on pixel radius
            meters_per_pixel = (
                156543.03392
                * math.cos(math.radians(self._latitude))
                / (2**self._map_zoom)
            )
            radius_meters = radius * meters_per_pixel

            # Approximate tile span (very rough approximation)
            # At equator, 1 degree is approx 111km
            degree_span = radius_meters / 111000

            # Convert degree span to tile span
            tile_span = degree_span * (2**self._map_zoom) / 360.0

            # Need at least 1 tile
            tile_span = max(1, tile_span)

            # Calculate screen position for the center tile
            center_tile_screen_x = center_x - (tile_x - math.floor(tile_x)) * 256
            center_tile_screen_y = center_y - (tile_y - math.floor(tile_y)) * 256

            # Calculate tile range
            start_tile_x = math.floor(tile_x - tile_span)
            start_tile_y = math.floor(tile_y - tile_span)
            end_tile_x = math.ceil(tile_x + tile_span)
            end_tile_y = math.ceil(tile_y + tile_span)

            # Limit to valid tile range
            max_tile = 2**self._map_zoom
            start_tile_x = max(0, start_tile_x)
            start_tile_y = max(0, start_tile_y)
            end_tile_x = min(max_tile - 1, end_tile_x)
            end_tile_y = min(max_tile - 1, end_tile_y)

            # Draw tiles
            for y in range(start_tile_y, end_tile_y + 1):
                for x in range(start_tile_x, end_tile_x + 1):
                    # Calculate screen position
                    screen_x = center_tile_screen_x - (math.floor(tile_x) - x) * 256
                    screen_y = center_tile_screen_y - (math.floor(tile_y) - y) * 256

                    # Get the tile
                    tile_image = self._tile_manager.get_tile(self._map_zoom, x, y)

                    if tile_image:
                        # Draw the tile
                        painter.drawImage(int(screen_x), int(screen_y), tile_image)

        # Draw dark overlay to make other elements more visible
        painter.fillRect(
            QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2),
            QColor(0, 0, 0, 100),
        )

        painter.restore()

    def _draw_grid(self, painter, center_x, center_y, radius):
        """Draw the coordinate grid."""
        painter.setPen(QPen(QColor(100, 100, 100, 170), 0.75))

        # Draw concentric circles
        # Use the passed radius which is based on min dimension
        radius_step = radius / 5  # Divide the actual radius into steps
        for i in range(1, 5):
            current_radius = i * radius_step
            painter.drawEllipse(
                int(center_x - current_radius),
                int(center_y - current_radius),
                int(current_radius * 2),
                int(current_radius * 2),
            )

        # Draw crosshairs based on the calculated center and radius
        painter.drawLine(
            int(center_x), int(center_y - radius), int(center_x), int(center_y + radius)
        )
        painter.drawLine(
            int(center_x - radius), int(center_y), int(center_x + radius), int(center_y)
        )

        # Draw cardinal direction indicators (N, E, S, W)
        font = QFont("Arial", 8, QFont.Bold)
        painter.setFont(font)

        # North indicator
        painter.drawText(
            QRectF(center_x - 5, center_y - radius + 5, 10, 10), Qt.AlignCenter, "N"
        )

        # East indicator
        painter.drawText(
            QRectF(center_x + radius - 15, center_y - 5, 10, 10), Qt.AlignCenter, "E"
        )

        # South indicator
        painter.drawText(
            QRectF(center_x - 5, center_y + radius - 15, 10, 10), Qt.AlignCenter, "S"
        )

        # West indicator
        painter.drawText(
            QRectF(center_x - radius + 5, center_y - 5, 10, 10), Qt.AlignCenter, "W"
        )

    def _draw_trajectory(self, painter, width, height):
        """Draw the vehicle's trajectory path."""
        if len(self._trajectory) < 2:
            return

        # Save painter state before applying clipping
        painter.save()

        # Create a circular clipping path
        clip_path = QPainterPath()
        clip_path.addEllipse(
            self._centerx - self._radius,
            self._centery - self._radius,
            self._radius * 2,
            self._radius * 2,
        )
        painter.setClipPath(clip_path)

        # Create path for the trajectory
        path = QPainterPath()

        # Get reference point (either current position or first trajectory point)
        ref_lat = self._latitude if self._center_on_vehicle else self._trajectory[0][0]
        ref_lon = self._longitude if self._center_on_vehicle else self._trajectory[0][1]

        # Start the path
        first_point = self._trajectory[0]
        x, y = self._geo_to_screen(first_point[0], first_point[1], ref_lat, ref_lon)
        path.moveTo(x, y)

        # Add all points to the path
        for point in self._trajectory[1:]:
            x, y = self._geo_to_screen(point[0], point[1], ref_lat, ref_lon)
            path.lineTo(x, y)

        # Draw the path - make it more visible over satellite imagery
        pen = QPen(QColor(config.ACCENT_COLOR), config.TRAJECTORY_LINE_WIDTH + 1)
        pen.setStyle(Qt.SolidLine)
        painter.setPen(pen)
        painter.drawPath(path)

        # Restore painter state
        painter.restore()

    def _draw_position_marker(self, painter, width, height):
        """Draw the current position marker with improved direction arrow."""
        if self._center_on_vehicle:
            x, y = self._centerx, self._centery
        else:
            x, y = self._geo_to_screen(
                self._latitude,
                self._longitude,
                self._trajectory[0][0] if self._trajectory else self._latitude,
                self._trajectory[0][1] if self._trajectory else self._longitude,
            )

        # Draw vehicle marker (enlarged for better visibility)
        painter.setPen(QPen(Qt.white, 2))
        painter.setBrush(QColor(config.ACCENT_COLOR))
        painter.drawEllipse(int(x - 6), int(y - 6), 12, 12)

        # Determine heading - prioritize directly set heading value
        heading = (
            self._heading
            if hasattr(self, "_heading") and self._heading is not None
            else 0
        )

        # If no direct heading is available, calculate from trajectory
        if (heading == 0 or heading is None) and len(self._trajectory) >= 2:
            # Calculate heading from last two points
            last = self._trajectory[-1]
            prev = self._trajectory[-2]

            # Calculate heading
            dx = last[1] - prev[1]  # longitude
            dy = last[0] - prev[0]  # latitude
            heading = math.degrees(math.atan2(dx, dy))

        # Draw arrow using the heading
        painter.save()
        painter.translate(x, y)

        # Use same heading logic as the CoG compass rose
        # In CoG gauge, 0° is North, 90° is East, etc.
        painter.rotate(heading)  # Align rotation with HeadingWidget

        # Draw a triangle for the direction
        path = QPainterPath()
        path.moveTo(0, -15)  # Tip of the arrow
        path.lineTo(-7, 0)  # Left corner
        path.lineTo(7, 0)  # Right corner
        path.closeSubpath()

        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)

        # Add outline for better visibility
        painter.setPen(QPen(QColor(config.ACCENT_COLOR), 1.5))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        painter.restore()

    def _geo_to_screen(self, lat, lon, ref_lat, ref_lon):
        """
        Convert geographic coordinates to screen coordinates.

        Args:
            lat: Latitude to convert
            lon: Longitude to convert
            ref_lat: Reference latitude (center of view)
            ref_lon: Reference longitude (center of view)

        Returns:
            (x, y) tuple of screen coordinates
        """
        # Convert lat/lon to x/y
        # Note: This is a simplified projection, not accurate for large areas
        x = self._centerx + (lon - ref_lon) / self._map_scale
        y = self._centery - (lat - ref_lat) / self._map_scale

        return x, y

    def _geo_to_tile(self, lat, lon, zoom):
        """Convert geographic coordinates to tile coordinates."""
        lat_rad = math.radians(lat)
        n = 2.0**zoom
        tile_x = (lon + 180.0) / 360.0 * n
        tile_y = (
            (1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi)
            / 2.0
            * n
        )

        return tile_x, tile_y
