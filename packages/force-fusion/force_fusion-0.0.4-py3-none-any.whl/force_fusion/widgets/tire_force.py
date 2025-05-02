"""
Tire force widget for displaying normal force on each tire.
"""

import math

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPen, QRadialGradient
from PyQt5.QtWidgets import QSizePolicy, QWidget

from force_fusion import config


class TireForceWidget(QWidget):
    """
    Widget that displays a circle with radius proportional to tire normal force.

    Features:
    - Circle size indicates normal force
    - Color coding based on force level
    - Force value label
    - Tire position label (FL, FR, RL, RR)
    """

    def __init__(self, position="FL", parent=None):
        """
        Initialize the tire force widget.

        Args:
            position: Tire position code ("FL", "FR", "RL", "RR")
            parent: Parent widget
        """
        super().__init__(parent)

        # Current force value and position
        self._force = 0.0  # Start with 0 N
        self._position = position

        # Force visualization settings
        self._min_force = config.TIRE_FORCE_MIN  # Minimum force (N)
        self._max_force = config.TIRE_FORCE_MAX  # Maximum force (N)
        self._normal_force = config.TIRE_FORCE_NORMAL  # Reference for 100% force

        # Set widget properties
        self.setMinimumSize(150, 150)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(config.BACKGROUND_COLOR))
        self.setPalette(palette)

    def set_force(self, force):
        """
        Set the tire normal force value.

        Args:
            force: Normal force in Newtons
        """
        # Allow zero force by not clamping to min_force
        self._force = min(self._max_force, max(config.TIRE_FORCE_MIN, force))
        self.update()

    def paintEvent(self, event):
        """
        Paint the tire force indicator.

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

        # Calculate radius based on force value (using square root for better visual scaling)
        max_radius = min(width, height) // 2 - 20

        # Calculate normalized force (0.0 to 1.0)
        if self._max_force <= 0:
            normalized_force = 0
        else:
            normalized_force = self._force / self._max_force

        radius = max_radius * math.sqrt(normalized_force)

        # Draw background circle
        self._draw_background_circle(painter, center_x, center_y, max_radius)

        # Draw force circle
        self._draw_force_circle(painter, center_x, center_y, radius)

        # Draw position label
        self._draw_position_label(painter, center_x, center_y)

        # Draw force value
        self._draw_force_value(painter, center_x, center_y, max_radius)

    def _draw_background_circle(self, painter, center_x, center_y, max_radius):
        """Draw the background reference circle."""
        painter.setPen(QPen(QColor(60, 60, 60), 1))
        painter.setBrush(QColor(40, 40, 40))
        painter.drawEllipse(
            center_x - max_radius, center_y - max_radius, max_radius * 2, max_radius * 2
        )

        # Draw reference circles at 25%, 50%, 75% and 100% of max force
        painter.setPen(QPen(QColor(80, 80, 80), 0.5, Qt.DashLine))

        for percent in [0.25, 0.5, 0.75, 1.0]:
            ref_radius = max_radius * math.sqrt(percent)
            painter.drawEllipse(
                int(center_x - ref_radius),
                int(center_y - ref_radius),
                int(ref_radius * 2),
                int(ref_radius * 2),
            )

    def _draw_force_circle(self, painter, center_x, center_y, radius):
        """Draw the circle representing the current force."""
        # Calculate force percentage from 0 to 100%
        force_percent = (self._force / self._max_force) * 100

        # Determine color based on force level using config colors
        # Low force (0-33%): Green (TIRE_FORCE_COLOR_LOW)
        # Normal force (33-66%): Yellow (TIRE_FORCE_COLOR_NORMAL)
        # High force (66-100%): Red (TIRE_FORCE_COLOR_HIGH)

        # Convert hex color values to QColor
        low_color = QColor(config.TIRE_FORCE_COLOR_LOW)
        normal_color = QColor(config.TIRE_FORCE_COLOR_NORMAL)
        high_color = QColor(config.TIRE_FORCE_COLOR_HIGH)

        if force_percent <= 33:
            # Low force: interpolate from dark green to full green
            color = low_color
            factor = (force_percent / 33) * 30 + 100  # 100% to 130%
            color = color.lighter(int(factor))
        elif force_percent <= 66:
            # Normal force: interpolate from green to yellow
            t = (force_percent - 33) / 33  # 0 to 1 within this range
            color = QColor(
                int(low_color.red() + t * (normal_color.red() - low_color.red())),
                int(low_color.green() + t * (normal_color.green() - low_color.green())),
                int(low_color.blue() + t * (normal_color.blue() - low_color.blue())),
            )
        else:
            # High force: interpolate from yellow to red
            t = (force_percent - 66) / 34  # 0 to 1 within this range
            color = QColor(
                int(normal_color.red() + t * (high_color.red() - normal_color.red())),
                int(
                    normal_color.green()
                    + t * (high_color.green() - normal_color.green())
                ),
                int(
                    normal_color.blue() + t * (high_color.blue() - normal_color.blue())
                ),
            )

        # Create radial gradient with dynamic colors
        gradient = QRadialGradient(center_x, center_y, radius)
        gradient.setColorAt(0, color.lighter(130))
        gradient.setColorAt(1, color)

        # Draw the force circle
        painter.setPen(QPen(color, 2))
        painter.setBrush(gradient)
        painter.drawEllipse(
            int(center_x - radius),
            int(center_y - radius),
            int(radius * 2),
            int(radius * 2),
        )

    def _draw_position_label(self, painter, center_x, center_y):
        """Draw the tire position label (FL, FR, RL, RR)."""
        # Set up font
        position_font = QFont("Arial", 20, QFont.Bold)
        painter.setFont(position_font)

        # Draw centered position text
        painter.setPen(QColor(config.TEXT_COLOR))
        text_rect = QRectF(center_x - 40, center_y - 20, 80, 40)
        painter.drawText(text_rect, Qt.AlignCenter, self._position)

    def _draw_force_value(self, painter, center_x, center_y, max_radius):
        """Draw the numeric force value."""
        # Set up font
        value_font = QFont("Arial", 10)
        painter.setFont(value_font)

        # Create force value text
        force_text = f"{self._force:.0f} N"

        # Draw at bottom of widget
        text_rect = QRectF(center_x - 50, center_y + max_radius * 0.7, 100, 20)

        painter.setPen(QColor(config.TEXT_COLOR))
        painter.drawText(text_rect, Qt.AlignCenter, force_text)

        # Calculate and display percentage of normal force
        percent = (self._force / self._normal_force) * 100
        # Cap the percentage display at 100% for clarity
        display_percent = min(100, percent)
        percent_text = f"{display_percent:.0f}%"

        # Draw percentage below force value
        percent_rect = QRectF(center_x - 50, center_y + max_radius * 0.9, 100, 20)

        painter.drawText(percent_rect, Qt.AlignCenter, percent_text)
