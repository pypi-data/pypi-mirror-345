"""
Minimap widget that displays a 2D trajectory of the vehicle's path.
"""

import logging
import math
import os
from threading import Lock

from PyQt5.QtCore import QDateTime, QObject, QRectF, Qt, QTimer, QUrl, pyqtSignal
from PyQt5.QtGui import (
    QColor,
    QFont,
    QGuiApplication,
    QImage,
    QPainter,
    QPainterPath,
    QPen,
)
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
from force_fusion.utils.geo_utils import (
    geo_to_screen,
    geo_to_tile,
    get_visible_tiles,
    tile_to_geo,
    tile_to_quadkey,
)

# Set up logging
logger = logging.getLogger(__name__)


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

        # Configure network manager
        self.network_manager.setNetworkAccessible(QNetworkAccessManager.Accessible)

        # Set up tile URLs from config
        self.tile_urls = config.MAP_TILE_URLS

        # Default style
        self.style_id = config.MINIMAP_DEFAULT_STYLE
        self.current_url_template = self.tile_urls[self.style_id]

        # Create cache directory if it doesn't exist
        self.cache_dir = os.path.join(
            os.path.expanduser("~"), ".force_fusion", "map_tile_cache"
        )
        os.makedirs(self.cache_dir, exist_ok=True)

        # Create placeholder image
        self.placeholder_image = self._create_placeholder_image()

    def _create_placeholder_image(self):
        """Create a placeholder image to use when network is unavailable"""
        try:
            image = QImage(config.TILE_SIZE, config.TILE_SIZE, QImage.Format_ARGB32)
            image.fill(QColor(config.MAP_BACKGROUND_COLOR))

            # Draw a simple grid pattern
            painter = QPainter(image)
            painter.setPen(QPen(QColor(80, 80, 80), 1))

            # Draw horizontal and vertical lines
            for i in range(0, config.TILE_SIZE, 32):
                painter.drawLine(0, i, config.TILE_SIZE, i)
                painter.drawLine(i, 0, i, config.TILE_SIZE)

            # Add a label to indicate it's a placeholder
            painter.setPen(QColor(180, 180, 180))
            painter.setFont(QFont("Arial", 10))
            painter.drawText(
                QRectF(0, 0, config.TILE_SIZE, config.TILE_SIZE),
                Qt.AlignCenter,
                "Map Tile\nUnavailable",
            )

            painter.end()
            return image
        except Exception as e:
            logger.error(f"Error creating placeholder image: {e}")
            return QImage(config.TILE_SIZE, config.TILE_SIZE, QImage.Format_ARGB32)

    def set_style(self, style_name):
        """Set the map style to use"""
        if style_name in self.tile_urls:
            self.style_id = style_name
            # Update URL template for the selected style
            self.current_url_template = self.tile_urls[style_name]
            # Clear cache when changing styles
            with self.cache_lock:
                self.cache.clear()
            return True
        return False

    def get_tile(self, zoom, x, y):
        """
        Get a map tile for the specified coordinates.

        Args:
            zoom: Zoom level
            x: Tile x coordinate
            y: Tile y coordinate

        Returns:
            QImage of the tile if available in cache, placeholder otherwise
        """
        # Create unique key for this tile
        tile_key = f"{self.style_id}_{zoom}_{x}_{y}"

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
                logger.error(f"Error loading cached tile: {e}")

        # Tile not in cache, request it if not already pending
        if tile_key not in self.pending_requests:
            self._request_tile(zoom, x, y, tile_key)

        # Return placeholder while loading
        return self.placeholder_image

    def _request_tile(self, zoom, x, y, tile_key):
        """Request a tile from the server."""
        try:
            # Check if this tile is already being requested
            if tile_key in self.pending_requests:
                return

            # Process URL template based on style
            url_template = self.current_url_template

            # Handle special case for Bing Maps (quadkey)
            if self.style_id == "satellite" and "{q}" in url_template:
                quadkey = tile_to_quadkey(x, y, zoom)
                url = url_template.replace("{q}", quadkey)
            else:
                # Standard URL format with {z}, {x}, {y}
                url = url_template.format(z=zoom, x=x, y=y)

            request = QNetworkRequest(QUrl(url))

            # Set request priority to high for faster loading
            request.setPriority(QNetworkRequest.HighPriority)

            # Add proper headers
            request.setRawHeader(b"User-Agent", b"Force-Fusion/1.0")
            request.setRawHeader(b"Accept", b"image/*")

            # Set a timeout to prevent stalled requests
            request.setAttribute(
                QNetworkRequest.CacheLoadControlAttribute, QNetworkRequest.PreferCache
            )

            # Make the request
            reply = self.network_manager.get(request)

            # Store the reply and connect to its signals
            self.pending_requests[tile_key] = (reply, zoom, x, y)
            reply.finished.connect(
                lambda: self._handle_tile_response(reply, zoom, x, y, tile_key)
            )
        except Exception as e:
            logger.error(f"Error requesting tile: {e}")
            # Use placeholder for this tile when request fails
            self._use_placeholder(zoom, x, y, tile_key)

    def _use_placeholder(self, zoom, x, y, tile_key):
        """Set placeholder image for a tile and emit signal."""
        with self.cache_lock:
            self.cache[tile_key] = self.placeholder_image
        self.tileLoaded.emit(zoom, x, y, self.placeholder_image)

    def _handle_tile_response(self, reply, zoom, x, y, tile_key):
        """Handle the network response for a tile request."""
        try:
            if reply.error() == QNetworkReply.NoError:
                # Read the image data
                image_data = reply.readAll()

                # Create a QImage from the data
                image = QImage()
                if (
                    image.loadFromData(image_data)
                    and not image.isNull()
                    and image.width() > 1
                ):
                    # Save to disk cache
                    tile_path = os.path.join(self.cache_dir, f"{tile_key}.png")
                    image.save(tile_path, "PNG")

                    # Update memory cache
                    with self.cache_lock:
                        self.cache[tile_key] = image

                    # Emit signal that tile is loaded
                    self.tileLoaded.emit(zoom, x, y, image)
                else:
                    logger.warning(f"Invalid image received for tile {zoom}/{x}/{y}")
                    self._use_placeholder(zoom, x, y, tile_key)
                    # Schedule a retry after a delay
                    QTimer.singleShot(
                        2000, lambda: self._retry_tile_request(zoom, x, y, tile_key)
                    )
            else:
                logger.warning(f"Error downloading tile: {reply.errorString()}")
                self._use_placeholder(zoom, x, y, tile_key)
                # Schedule a retry after a delay
                QTimer.singleShot(
                    2000, lambda: self._retry_tile_request(zoom, x, y, tile_key)
                )

            # Clean up
            if tile_key in self.pending_requests:
                del self.pending_requests[tile_key]

            reply.deleteLater()
        except Exception as e:
            logger.error(f"Error handling tile response: {e}")
            self._use_placeholder(zoom, x, y, tile_key)
            # Schedule a retry after a delay
            QTimer.singleShot(
                2000, lambda: self._retry_tile_request(zoom, x, y, tile_key)
            )

    def _retry_tile_request(self, zoom, x, y, tile_key):
        """Retry loading a tile after a failure."""
        try:
            # Only retry if we don't already have this tile in cache
            with self.cache_lock:
                if (
                    tile_key in self.cache
                    and self.cache[tile_key] != self.placeholder_image
                ):
                    return

            # And if it's not already being requested
            if tile_key in self.pending_requests:
                return

            # Request the tile again
            self._request_tile(zoom, x, y, tile_key)
        except Exception as e:
            logger.error(f"Error retrying tile request: {e}")


class DetailMapView(QDialog):
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

        # Flag to control position updates
        self._follow_vehicle = True  # Start by following the vehicle

        # Tile loading flag
        self._tiles_loaded = False

        # Set up dialog
        self.setWindowTitle("Detailed Map View")
        self.setMinimumSize(800, 600)
        self.setModal(False)

        # Create UI components
        self._create_ui()

        # Set map settings
        self.zoom = config.DEFAULT_ZOOM
        self.tile_manager = TileManager(self)
        self.tile_manager.tileLoaded.connect(self._on_tile_loaded)

        # Set initial style
        self.map_style = config.DETAILMAP_DEFAULT_STYLE
        self.set_map_style(config.DETAILMAP_DEFAULT_STYLE)

        # Add panning support
        self.drag_enabled = False
        self.drag_start_pos = None
        self.center_offset_x = 0
        self.center_offset_y = 0

        # Timer to periodically update the dialog
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._update_from_parent)
        self._update_timer.start(config.MAP_UPDATE_INTERVAL)

        # Tile loading check timer
        self._tile_load_timer = QTimer(self)
        self._tile_load_timer.setSingleShot(True)
        self._tile_load_timer.timeout.connect(self.update)

        # Update coordinates display
        self._update_status_bar()

        # Center the dialog on the screen
        screen_rect = QGuiApplication.primaryScreen().geometry()
        self.move(
            int((screen_rect.width() - self.width()) / 2),
            int((screen_rect.height() - self.height()) / 2),
        )

    def _on_tile_loaded(self, zoom, x, y, image):
        """Handle a tile that has finished loading."""
        # Only update if the zoom level still matches our current zoom
        if zoom == self.zoom:
            self._tiles_loaded = True
            self.update()  # Trigger a repaint to show the new tile

    def _create_ui(self):
        """Create and set up the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Create map widget
        self.map_widget = QWidget()
        self.map_widget.setMinimumSize(780, 500)
        self.map_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.map_widget.paintEvent = self._paint_map
        layout.addWidget(self.map_widget)

        # Bottom controls layout
        bottom_layout = QVBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(5)

        # Zoom slider
        zoom_layout = QHBoxLayout()
        zoom_label = QLabel("Zoom:")
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(1)
        self.zoom_slider.setMaximum(19)
        self.zoom_slider.setValue(config.DEFAULT_ZOOM)
        self.zoom_slider.setFixedWidth(600)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        zoom_layout.addWidget(zoom_label)
        zoom_layout.addWidget(self.zoom_slider)
        zoom_layout.addStretch(1)
        bottom_layout.addLayout(zoom_layout)

        # Info and style selection in one row
        info_style_layout = QHBoxLayout()

        # Info label (left-aligned)
        self.status_bar = QLabel()
        self.status_bar.setStyleSheet("color: white;")
        info_style_layout.addWidget(self.status_bar)

        # Add flexible space between info and buttons
        info_style_layout.addStretch(1)

        # Map style buttons (right-aligned)
        self.style_buttons = self._create_style_buttons()

        # Add buttons to layout
        for button in self.style_buttons.values():
            info_style_layout.addWidget(button)

        # Add to bottom layout
        bottom_layout.addLayout(info_style_layout)

        # Add bottom layout to main layout
        layout.addLayout(bottom_layout)

    def _create_style_buttons(self):
        """Create style selection buttons."""
        buttons = {}

        # Create buttons for each style
        for style_name in config.MAP_TILE_URLS.keys():
            buttons[style_name] = QLabel(style_name.capitalize())
            buttons[style_name].setStyleSheet(config.MAP_BUTTON_INACTIVE_STYLE)
            buttons[style_name].setCursor(Qt.PointingHandCursor)
            # Use a lambda with default argument to capture the style_name
            buttons[style_name].mousePressEvent = (
                lambda e, s=style_name: self.set_map_style(s)
            )

        return buttons

    def mousePressEvent(self, event):
        """Handle mouse press for dragging the map"""
        if event.button() == Qt.LeftButton:
            self.drag_enabled = True
            self.drag_start_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            # When user starts dragging, stop following the vehicle
            self._follow_vehicle = False

    def mouseMoveEvent(self, event):
        """Handle mouse movement for dragging the map"""
        if self.drag_enabled and self.drag_start_pos:
            # Calculate the movement delta
            delta = event.pos() - self.drag_start_pos
            self.center_offset_x += delta.x()
            self.center_offset_y += delta.y()

            # Update the drag start position for next move
            self.drag_start_pos = event.pos()

            # Redraw the map
            self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release for dragging the map"""
        if event.button() == Qt.LeftButton and self.drag_enabled:
            self.drag_enabled = False
            self.setCursor(Qt.ArrowCursor)

            # Update the map center based on the drag offset
            if self.center_offset_x != 0 or self.center_offset_y != 0:
                # Convert the center offset to geo coordinates
                center_tile_x, center_tile_y = geo_to_tile(
                    self.latitude, self.longitude, self.zoom
                )

                # Calculate new tile coordinates after offset
                new_center_tile_x = (
                    center_tile_x - self.center_offset_x / config.TILE_SIZE
                )
                new_center_tile_y = (
                    center_tile_y - self.center_offset_y / config.TILE_SIZE
                )

                # Convert back to geo coordinates
                self.latitude, self.longitude = tile_to_geo(
                    new_center_tile_x, new_center_tile_y, self.zoom
                )

                # Reset the center offset
                self.center_offset_x = 0
                self.center_offset_y = 0

                # Update the status bar
                self._update_status_bar()

                # Redraw the map
                self.update()

    def wheelEvent(self, event):
        """Handle mouse wheel for zooming the map"""
        # Get the current position under the cursor
        cursor_pos = event.pos()

        # Calculate tile coordinates at cursor
        old_center_tile_x, old_center_tile_y = geo_to_tile(
            self.latitude, self.longitude, self.zoom
        )
        cursor_tile_x = (
            old_center_tile_x
            + (cursor_pos.x() - self.map_widget.width() / 2) / config.TILE_SIZE
        )
        cursor_tile_y = (
            old_center_tile_y
            + (cursor_pos.y() - self.map_widget.height() / 2) / config.TILE_SIZE
        )

        # Convert cursor position to geo coordinates
        cursor_lat, cursor_lon = tile_to_geo(cursor_tile_x, cursor_tile_y, self.zoom)

        # Calculate new zoom level
        old_zoom = self.zoom
        if event.angleDelta().y() > 0:
            # Zoom in
            self.zoom = min(19, self.zoom + 1)
        else:
            # Zoom out
            self.zoom = max(1, self.zoom - 1)

        # Update the slider
        self.zoom_slider.setValue(self.zoom)

        # If zoom level changed, recalculate center to keep cursor position fixed
        if old_zoom != self.zoom:
            # Prefetch tiles for the new zoom level
            self._prefetch_tiles_for_zoom(cursor_lat, cursor_lon)

            # Reset tile loading flag
            self._tiles_loaded = False

            # Calculate new tile coordinates after zoom
            new_cursor_tile_x, new_cursor_tile_y = geo_to_tile(
                cursor_lat, cursor_lon, self.zoom
            )

            # Calculate where the cursor should be relative to center in tiles
            cursor_offset_x = (
                cursor_pos.x() - self.map_widget.width() / 2
            ) / config.TILE_SIZE
            cursor_offset_y = (
                cursor_pos.y() - self.map_widget.height() / 2
            ) / config.TILE_SIZE

            # Calculate the new center tile
            new_center_tile_x = new_cursor_tile_x - cursor_offset_x
            new_center_tile_y = new_cursor_tile_y - cursor_offset_y

            # Convert back to geo coordinates
            self.latitude, self.longitude = tile_to_geo(
                new_center_tile_x, new_center_tile_y, self.zoom
            )

            # Update the status bar
            self._update_status_bar()

            # Schedule additional update to load more tiles
            self._tile_load_timer.start(100)

            # Redraw the map
            self.update()

    def _prefetch_tiles_for_zoom(self, lat, lon):
        """Prefetch tiles for the new zoom level around the specified position."""
        try:
            # Calculate the visible tile range at the new zoom level
            tiles = get_visible_tiles(
                lat, lon, self.zoom, self.map_widget.width(), self.map_widget.height()
            )

            # Request each tile (will get from cache if already loaded)
            for tile_info in tiles:
                tile_zoom, tile_x, tile_y, _, _ = tile_info
                # This will queue a network request if the tile isn't cached
                self.tile_manager.get_tile(tile_zoom, tile_x, tile_y)
        except Exception as e:
            logger.error(f"Error prefetching tiles: {e}")

    def set_map_style(self, style):
        """Switch to the specified map style"""
        # Update style
        self.map_style = style
        self.tile_manager.set_style(style)

        # Update button styles
        for style_name, btn in self.style_buttons.items():
            if style_name == style:
                btn.setStyleSheet(config.MAP_BUTTON_ACTIVE_STYLE)
            else:
                btn.setStyleSheet(config.MAP_BUTTON_INACTIVE_STYLE)

        # Update map
        self.update()

    def _update_status_bar(self):
        """Update the status bar with current coordinates and zoom level"""
        text = f"Lat: {self.latitude:.6f}  Lon: {self.longitude:.6f}  Zoom: {self.zoom}"
        if self._follow_vehicle:
            text += " | Following vehicle (press Space to unlock map)"
        else:
            text += " | Map unlocked (press Space to follow vehicle)"
        self.status_bar.setText(text)

    def _update_from_parent(self):
        """Update position and trajectory data from parent widget."""
        if self._parent_widget:
            # Always update the trajectory and heading
            self.trajectory = self._parent_widget._trajectory.copy()
            self.heading = self._parent_widget._heading

            # Only update lat/lon if following the vehicle
            if self._follow_vehicle:
                self.latitude = self._parent_widget._latitude
                self.longitude = self._parent_widget._longitude
                self._update_status_bar()

            self.update()

    def on_zoom_changed(self, zoom):
        """Handle zoom slider value change."""
        self.zoom = zoom
        self._update_status_bar()
        self.update()

    def keyPressEvent(self, event):
        """Handle key press events."""
        # Toggle vehicle following with spacebar
        if event.key() == Qt.Key_Space:
            self._follow_vehicle = not self._follow_vehicle
            if self._follow_vehicle:
                # When re-enabling following, snap back to vehicle position
                self.latitude = self._parent_widget._latitude
                self.longitude = self._parent_widget._longitude
                self._update_status_bar()
                self.update()
        super().keyPressEvent(event)

    def _paint_map(self, event):
        """Paint the detailed map view."""
        painter = QPainter(self.map_widget)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Get widget dimensions
        width = self.map_widget.width()
        height = self.map_widget.height()

        # Draw background
        painter.fillRect(0, 0, width, height, QColor(config.MAP_BACKGROUND_COLOR))

        # Make sure zoom is within valid range
        self.zoom = max(1, min(19, self.zoom))

        # Draw tiles
        self._draw_map_tiles(painter, width, height)

        # Draw trajectory
        self._draw_trajectory(painter, width, height)

        # Draw current position marker
        self._draw_position_marker(painter, width, height)

        # Draw scale indicator
        self._draw_scale(painter, width, height)

    def _draw_map_tiles(self, painter, width, height):
        """Draw map tiles on the canvas."""
        # Calculate tile coordinates for current view
        tiles = get_visible_tiles(
            self.latitude, self.longitude, self.zoom, width, height
        )

        # Check if we need to trigger a repaint for loading tiles
        trigger_update = False

        # Draw tiles
        for tile_info in tiles:
            tile_zoom, tile_x, tile_y, screen_x, screen_y = tile_info

            # Apply panning offset
            screen_x += self.center_offset_x
            screen_y += self.center_offset_y

            # Try to get tile from cache
            tile_image = self.tile_manager.get_tile(tile_zoom, tile_x, tile_y)

            # If we got a placeholder, mark for update later
            if tile_image == self.tile_manager.placeholder_image:
                trigger_update = True

            if tile_image and not tile_image.isNull():
                # Draw tile at specified position
                painter.drawImage(int(screen_x), int(screen_y), tile_image)

        # If any tiles are still loading, schedule an update to check if they're ready
        if trigger_update and not self._tile_load_timer.isActive():
            # Use a timer to trigger an update after a short delay
            self._tile_load_timer.start(100)

    def _draw_trajectory(self, painter, width, height):
        """Draw the vehicle trajectory path."""
        if self.trajectory and len(self.trajectory) > 1:
            painter.setPen(QPen(QColor(config.ACCENT_COLOR), 3, Qt.SolidLine))

            path = QPainterPath()
            first = True

            for lat, lon in self.trajectory:
                px, py = geo_to_screen(
                    lat, lon, self.latitude, self.longitude, self.zoom, width, height
                )

                # Apply panning offset
                px += self.center_offset_x
                py += self.center_offset_y

                if first:
                    path.moveTo(px, py)
                    first = False
                else:
                    path.lineTo(px, py)

            painter.drawPath(path)

    def _draw_position_marker(self, painter, width, height):
        """Draw the current position marker with direction arrow."""
        if self.latitude and self.longitude:
            # Get vehicle position coordinates
            vehicle_lat = (
                self._parent_widget._latitude if self._parent_widget else self.latitude
            )
            vehicle_lon = (
                self._parent_widget._longitude
                if self._parent_widget
                else self.longitude
            )
            vehicle_heading = (
                self._parent_widget._heading if self._parent_widget else self.heading
            )

            # Get screen coordinates for current view center
            px, py = geo_to_screen(
                vehicle_lat,
                vehicle_lon,
                self.latitude,
                self.longitude,
                self.zoom,
                width,
                height,
            )

            # Apply panning offset
            px += self.center_offset_x
            py += self.center_offset_y

            # Draw circle for current position
            painter.setPen(QPen(Qt.white, 2))
            painter.setBrush(QColor(config.ACCENT_COLOR))
            painter.drawEllipse(int(px - 8), int(py - 8), 16, 16)

            # Draw direction arrow using the vehicle heading
            if vehicle_heading is not None:
                # Draw arrow
                painter.save()
                painter.translate(px, py)
                painter.rotate(vehicle_heading)  # Align rotation with vehicle heading

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

    def _draw_scale(self, painter, width, height):
        """Draw a scale indicator on the map."""
        # Calculate the length of 100 meters at current latitude and zoom
        meters_per_pixel = (
            156543.03392 * math.cos(math.radians(self.latitude)) / (2**self.zoom)
        )

        # Scale is for 256px tiles
        meters_per_pixel = meters_per_pixel / 2

        # Adjust scale length to be a nice round number
        if meters_per_pixel * 100 < 10:
            scale_meters = 10  # 10 meters
        elif meters_per_pixel * 100 < 50:
            scale_meters = 50  # 50 meters
        elif meters_per_pixel * 100 < 100:
            scale_meters = 100  # 100 meters
        elif meters_per_pixel * 100 < 500:
            scale_meters = 500  # 500 meters
        elif meters_per_pixel * 100 < 1000:
            scale_meters = 1000  # 1 km
        else:
            scale_meters = (
                math.ceil(meters_per_pixel * 100 / 1000) * 1000
            )  # Round to nearest km

        # Calculate scale width in pixels
        scale_width_pixels = int(scale_meters / meters_per_pixel)

        # Draw scale bar
        scale_y = height - 35
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
    """

    def __init__(self, parent=None):
        """Initialize the minimap widget."""
        super().__init__(parent)

        # Current position
        self._latitude = config.DEFAULT_CENTER[1]  # Default latitude
        self._longitude = config.DEFAULT_CENTER[0]  # Default longitude
        self._heading = 0.0  # Heading in degrees

        # Previous position for calculating heading
        self._prev_latitude = self._latitude
        self._prev_longitude = self._longitude
        self._auto_calculate_heading = True  # Auto-calculate heading if not provided

        # Trajectory history (unlimited)
        self._trajectory = []

        # Map view settings
        self._zoom = config.DEFAULT_ZOOM
        self._center_on_vehicle = True
        self._auto_zoom = True  # Auto-adjust zoom to fit trajectory

        # Zoom stability parameters
        self._last_zoom_change_time = 0
        self._zoom_change_cooldown_ms = 1000  # Min milliseconds between zoom changes
        self._min_zoom_change = (
            1  # Only change zoom if difference is at least this much
        )

        # Cached data for efficient rendering
        self._centerx = 0
        self._centery = 0
        self._radius = 0

        # Flag to track if we've loaded at least one good set of tiles
        self._tiles_loaded = False

        # Tile preloading timer
        self._tile_load_timer = QTimer(self)
        self._tile_load_timer.setSingleShot(True)
        self._tile_load_timer.timeout.connect(self.update)

        # Set widget properties
        self.setMinimumSize(200, 200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(config.BACKGROUND_COLOR))
        self.setPalette(palette)

        # Create tile manager for map tiles - always satellite for the minimap
        self._tile_manager = TileManager(self)
        self._tile_manager.set_style(config.MINIMAP_DEFAULT_STYLE)
        self._tile_manager.tileLoaded.connect(self._on_tile_loaded)

        # Set up cursor to indicate it's clickable
        self.setCursor(Qt.PointingHandCursor)

        # Detailed map dialog (created when needed)
        self._detail_dialog = None

    def _on_tile_loaded(self, zoom, x, y, image):
        """Handle a tile that has finished loading."""
        # Only update if the zoom level still matches our current zoom
        if zoom == self._zoom:
            self._tiles_loaded = True
            self.update()  # Trigger a repaint to show the new tile

    def update_position(self, latitude, longitude, heading=None):
        """Update the current position and add it to the trajectory."""
        # Store previous position for heading calculation
        self._prev_latitude = self._latitude
        self._prev_longitude = self._longitude

        # Update current position
        self._latitude = latitude
        self._longitude = longitude

        # Handle heading
        if heading is not None:
            # Use provided heading
            self._heading = heading
            self._auto_calculate_heading = False
        elif self._auto_calculate_heading:
            # Calculate heading from position change
            self._calculate_heading()

        # Add to trajectory
        self._trajectory.append((latitude, longitude))

        # No limit on trajectory points - removed TRAJECTORY_HISTORY_LENGTH check

        # Auto-adjust zoom to fit entire trajectory if enabled
        if self._auto_zoom and len(self._trajectory) > 1:
            self._adjust_zoom_to_fit_trajectory()

        # If detail dialog is open, update it
        if self._detail_dialog and self._detail_dialog.isVisible():
            self._detail_dialog._update_from_parent()

        # Request a repaint
        self.update()

    def _adjust_zoom_to_fit_trajectory(self):
        """Calculate optimal zoom level to fit the entire trajectory."""
        if not self._trajectory or len(self._trajectory) < 2:
            return

        # Check if we're in the cooldown period for zoom changes
        current_time = QDateTime.currentMSecsSinceEpoch()
        if current_time - self._last_zoom_change_time < self._zoom_change_cooldown_ms:
            return  # Skip this adjustment

        # Find the bounding box of the trajectory
        min_lat = max_lat = self._trajectory[0][0]
        min_lon = max_lon = self._trajectory[0][1]

        for lat, lon in self._trajectory:
            min_lat = min(min_lat, lat)
            max_lat = max(max_lat, lat)
            min_lon = min(min_lon, lon)
            max_lon = max(max_lon, lon)

        # Add a buffer around the bounding box (10% of the range)
        lat_range = max_lat - min_lat
        lon_range = max_lon - min_lon

        # Ensure there's at least some range
        lat_range = max(lat_range, 0.001)
        lon_range = max(lon_range, 0.001)

        buffer_lat = lat_range * 0.1
        buffer_lon = lon_range * 0.1

        min_lat -= buffer_lat
        max_lat += buffer_lat
        min_lon -= buffer_lon
        max_lon += buffer_lon

        # Calculate the center of the bounding box
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2

        # Determine the size of the bounding box in terms of lat/lon span
        lat_span = max_lat - min_lat
        lon_span = max_lon - min_lon

        # Adjust for the fact the minimap is a circle, so we need to fit within the smallest dimension
        # We're working with a circular viewport
        # Use the size of the widget to determine available space
        viewport_size = (
            min(self.width(), self.height()) * 0.8
        )  # 80% of the size to account for padding

        # Find the best zoom level
        best_zoom = None

        # Calculate the zoom level needed to fit both lat and lon spans
        # We need to find the zoom level where the entire trajectory fits within our viewport
        for zoom in range(19, 0, -1):  # Start from max zoom and decrease
            # Calculate tile spans at this zoom level
            world_tiles = 2**zoom

            # Convert lat/lon spans to pixel spans at this zoom
            tile_size = config.TILE_SIZE
            lat_pixels = (
                (lat_span / 170) * world_tiles * tile_size
            )  # Approx 170 degrees of latitude visible
            lon_pixels = (
                (lon_span / 360) * world_tiles * tile_size
            )  # 360 degrees of longitude in total

            # Choose the larger of the two spans
            max_pixels = max(lat_pixels, lon_pixels)

            # If the trajectory fits within our viewport at this zoom level, use it
            if max_pixels <= viewport_size:
                best_zoom = zoom
                break

        # Set a reasonable minimum zoom
        if best_zoom is None:
            best_zoom = 10
        best_zoom = max(best_zoom, 10)

        # Only change the zoom if it's different enough from the current zoom
        if abs(best_zoom - self._zoom) >= self._min_zoom_change:
            # Pre-fetch tiles at the new zoom level before actually changing the zoom
            self._prefetch_tiles_for_zoom(best_zoom, center_lat, center_lon)

            # Update the zoom level
            self._zoom = best_zoom

            # Record the time of the zoom change
            self._last_zoom_change_time = current_time

            # If we're not centering on the vehicle, update the center position
            if not self._center_on_vehicle:
                self._latitude = center_lat
                self._longitude = center_lon

            # Reset the tile loading flag since we're changing zoom
            self._tiles_loaded = False

            # Update now but also schedule another update in a short time to load more tiles
            self.update()
            self._tile_load_timer.start(100)  # Check for more tiles in 100ms

    def _prefetch_tiles_for_zoom(self, zoom, center_lat, center_lon):
        """Pre-fetch tiles for a new zoom level before switching to it."""
        # Calculate the visible tile range at the new zoom level
        if self.width() > 0 and self.height() > 0:
            diameter = min(self.width(), self.height())
            radius = diameter // 2 - 10

            # Get visible tiles using the center lat/lon
            tiles = get_visible_tiles(
                center_lat, center_lon, zoom, radius * 2, radius * 2
            )

            # Request each tile (will get from cache if already loaded)
            for tile_info in tiles:
                tile_zoom, tile_x, tile_y, _, _ = tile_info
                # This will queue a network request if the tile isn't cached
                self._tile_manager.get_tile(tile_zoom, tile_x, tile_y)

    def _calculate_heading(self):
        """Calculate heading from the current and previous positions."""
        # Only calculate if we have valid previous coordinates
        if (
            self._prev_latitude != self._latitude
            or self._prev_longitude != self._longitude
        ):
            # Convert to radians
            lat1 = math.radians(self._prev_latitude)
            lon1 = math.radians(self._prev_longitude)
            lat2 = math.radians(self._latitude)
            lon2 = math.radians(self._longitude)

            # Calculate heading using the Haversine formula
            dlon = lon2 - lon1
            y = math.sin(dlon) * math.cos(lat2)
            x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(
                lat2
            ) * math.cos(dlon)
            heading = math.degrees(math.atan2(y, x))

            # Convert to 0-360 degrees
            self._heading = (heading + 360) % 360

    def clear_trajectory(self):
        """Clear the trajectory history."""
        self._trajectory = []
        self.update()

    def set_zoom(self, zoom):
        """Set the zoom level."""
        self._zoom = max(1, min(19, zoom))
        self.update()

    def set_center_on_vehicle(self, center):
        """Set whether to keep the vehicle centered in the view."""
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
            self._detail_dialog = DetailMapView(
                self, self._latitude, self._longitude, self._trajectory.copy()
            )
        else:
            # Update position and trajectory
            self._detail_dialog.latitude = self._latitude
            self._detail_dialog.longitude = self._longitude
            self._detail_dialog.trajectory = self._trajectory.copy()
            self._detail_dialog.heading = self._heading

            # Ensure the detail map is centered at the current position
            self._detail_dialog._update_status_bar()
            self._detail_dialog.update()

        self._detail_dialog.show()
        self._detail_dialog.raise_()
        self._detail_dialog.activateWindow()

    def paintEvent(self, event):
        """Paint the minimap."""
        # Create painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get widget dimensions and calculate drawing area
        width = self.width()
        height = self.height()
        diameter = min(width, height)
        radius = diameter // 2 - 10  # Subtract padding
        self._radius = radius  # Store for mouse event handling

        # Calculate center
        widget_center_x = width // 2
        widget_center_y = height // 2

        # Define drawing area
        draw_rect = QRectF(
            widget_center_x - radius - 5,
            widget_center_y - radius - 5,
            diameter - 10,
            diameter - 10,
        )
        self._centerx = draw_rect.center().x()
        self._centery = draw_rect.center().y()

        # Draw map background within circle
        self._draw_map_background(painter, self._centerx, self._centery, radius)

        # Draw coordinate grid
        self._draw_grid(painter, self._centerx, self._centery, radius)

        # Draw trajectory
        self._draw_trajectory(painter, width, height)

        # Draw current position marker
        self._draw_position_marker(painter, width, height)

    def _draw_map_background(self, painter, center_x, center_y, radius):
        """Draw map tiles in the background circle."""
        # Create circular clipping path
        circle_path = QPainterPath()
        circle_path.addEllipse(
            center_x - radius, center_y - radius, radius * 2, radius * 2
        )

        painter.save()
        painter.setClipPath(circle_path)

        # Draw basic background
        painter.fillRect(
            QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2),
            QColor(config.MAP_BACKGROUND_COLOR),
        )

        # Calculate visible tile range based on current position
        if self._latitude != 0 and self._longitude != 0:
            # To ensure complete coverage with a circular view, we need to
            # expand the area slightly to cover all tiles that might be visible
            extended_radius = radius * 1.5  # Extend the radius to ensure full coverage

            # Get visible tiles for a wider area (using common utility)
            tiles = get_visible_tiles(
                self._latitude,
                self._longitude,
                self._zoom,
                extended_radius * 2,
                extended_radius * 2,
            )

            # Check if we need to trigger a repaint for loading tiles
            tile_count = len(tiles)
            loaded_count = 0

            # Sort tiles by distance from center for better visual loading
            center_tile_x, center_tile_y = geo_to_tile(
                self._latitude, self._longitude, self._zoom
            )
            sorted_tiles = sorted(
                tiles,
                key=lambda t: (
                    (t[1] - center_tile_x) ** 2 + (t[2] - center_tile_y) ** 2
                ),
            )

            # Draw tiles
            for tile_info in sorted_tiles:
                tile_zoom, tile_x, tile_y, screen_x, screen_y = tile_info

                # Adjust to center of circle
                adjusted_x = center_x - extended_radius + screen_x
                adjusted_y = center_y - extended_radius + screen_y

                # Get the tile
                tile_image = self._tile_manager.get_tile(tile_zoom, tile_x, tile_y)

                if tile_image != self._tile_manager.placeholder_image:
                    loaded_count += 1

                if tile_image and not tile_image.isNull():
                    # Draw tile
                    painter.drawImage(int(adjusted_x), int(adjusted_y), tile_image)

            # Force immediate loading of missing tiles
            if loaded_count < tile_count:
                # If less than 80% of tiles loaded, schedule a quicker update
                if loaded_count < tile_count * 0.8:
                    self._tile_load_timer.start(50)  # Very quick update
                else:
                    self._tile_load_timer.start(100)  # Slightly longer update

            # Log loading progress for debugging
            if loaded_count < tile_count:
                logger.debug(f"Loaded {loaded_count}/{tile_count} tiles")

        # Draw a slight darkening overlay to make other elements more visible
        painter.fillRect(
            QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2),
            QColor(0, 0, 0, 50),  # Semi-transparent black
        )

        painter.restore()

    def _draw_grid(self, painter, center_x, center_y, radius):
        """Draw the coordinate grid overlay."""
        painter.setPen(QPen(QColor(200, 200, 200, config.MAP_GRID_OPACITY), 0.75))

        # Draw concentric circles
        radius_step = radius / 5  # Divide radius into steps
        for i in range(1, 5):
            current_radius = i * radius_step
            painter.drawEllipse(
                int(center_x - current_radius),
                int(center_y - current_radius),
                int(current_radius * 2),
                int(current_radius * 2),
            )

        # Draw crosshairs
        painter.drawLine(
            int(center_x), int(center_y - radius), int(center_x), int(center_y + radius)
        )
        painter.drawLine(
            int(center_x - radius), int(center_y), int(center_x + radius), int(center_y)
        )

        # Draw cardinal direction indicators (N, E, S, W)
        font = QFont("Arial", 8, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255, 180))  # More visible white

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
        """Draw the vehicle trajectory path."""
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

        # Get reference point
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

        # Draw the path
        pen = QPen(QColor(config.ACCENT_COLOR), config.TRAJECTORY_LINE_WIDTH + 1)
        pen.setStyle(Qt.SolidLine)
        painter.setPen(pen)
        painter.drawPath(path)

        # Restore painter state
        painter.restore()

    def _draw_position_marker(self, painter, width, height):
        """Draw the current position marker with direction arrow."""
        if self._center_on_vehicle:
            x, y = self._centerx, self._centery
        else:
            x, y = self._geo_to_screen(
                self._latitude,
                self._longitude,
                self._trajectory[0][0] if self._trajectory else self._latitude,
                self._trajectory[0][1] if self._trajectory else self._longitude,
            )

        # Draw vehicle marker
        painter.setPen(QPen(Qt.white, 2))
        painter.setBrush(QColor(config.ACCENT_COLOR))
        painter.drawEllipse(int(x - 6), int(y - 6), 12, 12)

        # Draw arrow using the heading
        painter.save()
        painter.translate(x, y)
        painter.rotate(self._heading)

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
        """Convert geographic coordinates to screen coordinates."""
        # Calculate tile coordinates
        ref_tile_x, ref_tile_y = geo_to_tile(ref_lat, ref_lon, self._zoom)
        point_tile_x, point_tile_y = geo_to_tile(lat, lon, self._zoom)

        # Convert tile difference to screen coordinates
        x = self._centerx + (point_tile_x - ref_tile_x) * config.TILE_SIZE
        y = self._centery + (point_tile_y - ref_tile_y) * config.TILE_SIZE

        return x, y

    def toggle_auto_zoom(self):
        """Toggle automatic zoom adjustment."""
        self._auto_zoom = not self._auto_zoom
        if self._auto_zoom:
            self._adjust_zoom_to_fit_trajectory()
            self.update()
        return self._auto_zoom
