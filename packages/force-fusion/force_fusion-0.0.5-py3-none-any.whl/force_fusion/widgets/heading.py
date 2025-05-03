"""
Heading widget for displaying the vehicle's course over ground.
"""

import math

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPen, QPolygonF
from PyQt5.QtWidgets import QSizePolicy, QWidget

from force_fusion import config


class HeadingWidget(QWidget):
    """
    Widget that displays a compass showing the vehicle's heading.

    Features:
    - 360° compass rose
    - Direction labels (N, E, S, W)
    - Current heading pointer
    - Digital heading display
    """

    def __init__(self, parent=None):
        """
        Initialize the heading widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Current heading
        self._heading = 0.0  # degrees (0-360)

        # Set widget properties
        self.setMinimumSize(200, 200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(config.BACKGROUND_COLOR))
        self.setPalette(palette)

    def set_heading(self, heading):
        """
        Set the current heading.

        Args:
            heading: Heading in degrees (0-360)
        """
        # Normalize heading to 0-360 range
        self._heading = heading % 360.0
        self.update()

    def paintEvent(self, event):
        """
        Paint the heading indicator.

        Args:
            event: Paint event
        """
        # Create painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get widget dimensions
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) // 2 - 10

        # Draw background circle
        painter.setPen(QPen(QColor(config.BEZEL_BORDER_COLOR), 1))
        painter.setBrush(QColor(config.BEZEL_COLOR))
        painter.drawEllipse(
            center_x - radius, center_y - radius, radius * 2, radius * 2
        )

        # Draw compass rose
        self._draw_compass_rose(painter, center_x, center_y, radius)

        # Draw heading pointer
        self._draw_heading_pointer(painter, center_x, center_y, radius)

        # Draw digital heading
        self._draw_digital_heading(painter, center_x, center_y, radius)

        # Draw title
        painter.setPen(QColor(config.TEXT_COLOR))
        painter.setFont(QFont("Arial", 10))
        painter.drawText(QRectF(0, 5, width, 20), Qt.AlignCenter, "Course over Ground")

    def _draw_compass_rose(self, painter, center_x, center_y, radius):
        """Draw the compass rose with tick marks and cardinal directions."""
        # Set up fonts
        cardinal_font = QFont("Arial", 12, QFont.Bold)
        ordinal_font = QFont("Arial", 8)
        tick_font = QFont("Arial", 7)

        # Draw the outer ring
        painter.setPen(QPen(QColor(150, 150, 150), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(
            int(center_x - radius * 0.9),
            int(center_y - radius * 0.9),
            int(radius * 1.8),
            int(radius * 1.8),
        )

        # Draw tick marks and labels for each degree
        for angle in range(0, 360, 5):
            # Calculate tick positions
            inner_radius = radius * 0.8
            outer_radius = radius * 0.9

            # Determine tick length and label based on angle
            if angle % 90 == 0:
                # Cardinal directions (N, E, S, W)
                inner_radius = radius * 0.7
                painter.setPen(QPen(QColor(config.TEXT_COLOR), 2))
                painter.setFont(cardinal_font)

                # Determine label text
                if angle == 0:
                    label = "N"
                elif angle == 90:
                    label = "E"
                elif angle == 180:
                    label = "S"
                else:  # angle == 270
                    label = "W"

            elif angle % 45 == 0:
                # Ordinal directions (NE, SE, SW, NW)
                inner_radius = radius * 0.75
                painter.setPen(QPen(QColor(220, 220, 220), 1.5))
                painter.setFont(ordinal_font)

                # Determine label text
                if angle == 45:
                    label = "NE"
                elif angle == 135:
                    label = "SE"
                elif angle == 225:
                    label = "SW"
                else:  # angle == 315
                    label = "NW"

            elif angle % 15 == 0:
                # Medium ticks with degree labels
                inner_radius = radius * 0.8
                painter.setPen(QPen(QColor(180, 180, 180), 1))
                painter.setFont(tick_font)
                label = str(angle)
            else:
                # Minor ticks without labels
                painter.setPen(QPen(QColor(120, 120, 120), 0.5))
                label = None

            # Calculate tick line positions
            # Note: compass coordinate system (0° at North, increasing clockwise)
            # differs from the mathematical one, so we adjust the angle
            adjusted_angle = 90 - angle
            adjusted_angle_rad = math.radians(adjusted_angle)

            inner_x = center_x + inner_radius * math.cos(adjusted_angle_rad)
            inner_y = center_y - inner_radius * math.sin(adjusted_angle_rad)
            outer_x = center_x + outer_radius * math.cos(adjusted_angle_rad)
            outer_y = center_y - outer_radius * math.sin(adjusted_angle_rad)

            # Draw tick
            painter.drawLine(int(inner_x), int(inner_y), int(outer_x), int(outer_y))

            # Draw label if applicable
            if label:
                label_radius = inner_radius - 15
                label_x = center_x + label_radius * math.cos(adjusted_angle_rad)
                label_y = center_y - label_radius * math.sin(adjusted_angle_rad)

                # Adjust for text metrics
                metrics = painter.fontMetrics()
                text_width = metrics.horizontalAdvance(label)
                text_height = metrics.height()

                # Center text on calculated position
                text_rect = QRectF(
                    label_x - text_width / 2,
                    label_y - text_height / 2,
                    text_width,
                    text_height,
                )

                painter.drawText(text_rect, Qt.AlignCenter, label)

    def _draw_heading_pointer(self, painter, center_x, center_y, radius):
        """Draw the pointer indicating the current heading."""
        # Draw a triangle pointer at the top of the compass
        pointer_height = radius * 0.15
        pointer_width = radius * 0.1

        triangle = QPolygonF(
            [
                QPointF(center_x, center_y - radius * 0.9 - pointer_height),
                QPointF(center_x - pointer_width / 2, center_y - radius * 0.9),
                QPointF(center_x + pointer_width / 2, center_y - radius * 0.9),
            ]
        )

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(config.HEADING_COLOR))
        painter.drawPolygon(triangle)

        # Draw pointer base line
        painter.setPen(QPen(QColor(config.HEADING_COLOR), 2))
        painter.drawLine(
            int(center_x - pointer_width),
            int(center_y - radius * 0.9),
            int(center_x + pointer_width),
            int(center_y - radius * 0.9),
        )

        # Rotate the compass rose to show the current heading
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self._heading)

        # Draw a semi-transparent heading indicator
        painter.setPen(QPen(QColor(config.DANGER_COLOR), 2))
        painter.drawLine(0, 0, 0, int(-radius * 0.7))

        painter.restore()

    def _draw_digital_heading(self, painter, center_x, center_y, radius):
        """Draw the digital heading display."""
        # Set up font
        heading_font = QFont("Arial", 16, QFont.Bold)
        painter.setFont(heading_font)
        heading_metrics = painter.fontMetrics()

        # Format heading text
        heading_text = f"{self._heading:.1f}°"

        # Calculate text position - centered below the compass
        heading_rect = QRectF(
            center_x - radius * 0.5,
            center_y + radius * 0.2,
            radius * 1.0,
            heading_metrics.height(),
        )

        # Draw heading text
        painter.setPen(QColor(config.TEXT_COLOR))
        painter.drawText(heading_rect, Qt.AlignCenter, heading_text)

        # Add compass direction label
        direction_text = self._get_direction_text(self._heading)

        # Position the direction text below the heading
        direction_rect = QRectF(
            heading_rect.x(),
            heading_rect.bottom() + 5,
            heading_rect.width(),
            heading_metrics.height(),
        )

        painter.setFont(QFont("Arial", 10))
        painter.drawText(direction_rect, Qt.AlignCenter, direction_text)

    def _get_direction_text(self, heading):
        """
        Convert heading in degrees to a cardinal direction text.

        Args:
            heading: Heading in degrees (0-360)

        Returns:
            String with the cardinal/ordinal direction name
        """
        # Define direction ranges (each 22.5 degrees wide)
        directions = [
            "N",
            "NNE",
            "NE",
            "ENE",
            "E",
            "ESE",
            "SE",
            "SSE",
            "S",
            "SSW",
            "SW",
            "WSW",
            "W",
            "WNW",
            "NW",
            "NNW",
        ]

        # Calculate the direction index
        index = round(heading / 22.5) % 16

        return directions[index]
