"""
G-G Diagram widget for displaying lateral vs. longitudinal acceleration.
"""

import math

from PyQt5.QtCore import QRectF, Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QPainter, QPen
from PyQt5.QtWidgets import QSizePolicy, QWidget

from force_fusion import config


class GgDiagramWidget(QWidget):
    """
    Widget that displays a G-G diagram showing lateral vs. longitudinal acceleration.

    Features:
    - Circular envelope showing maximum G limits
    - Grid lines at regular G intervals
    - Moving dot that shows current G forces
    - Numeric display of current values
    - Point traces showing acceleration history
    """

    def __init__(self, parent=None):
        """
        Initialize the G-G diagram widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Current acceleration values
        self._ax = 0.0  # longitudinal acceleration (G), positive = forward
        self._ay = 0.0  # lateral acceleration (G), positive = right

        # G force limits from config
        self._min_g = config.GG_DIAGRAM_MIN_G  # Minimum G force to display
        self._max_g = config.GG_DIAGRAM_MAX_G  # Maximum G force to display
        self._g_range = self._max_g - self._min_g  # Total range of G forces

        # History of points for traces (no limit - keep all points)
        self._history = []
        # We'll only add points every N updates to reduce clutter
        self._update_counter = 0
        self._update_frequency = 3  # Only add a point every 3 updates

        # Set up update timer
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._update_plot)

        # Set widget properties
        self.setMinimumSize(200, 200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(config.BACKGROUND_COLOR))
        self.setPalette(palette)

        # Latest acceleration values to be processed by timer
        self._latest_ax = 0.0
        self._latest_ay = 0.0
        self._needs_update = False

        # Debug flag
        self._debug = False

        # Start the update timer
        self._update_timer.start(config.GG_DIAGRAM_UPDATE_INTERVAL)

    def setAccel(self, ax, ay):
        """
        Set the acceleration values.

        Args:
            ax: Longitudinal acceleration in G, positive = forward
            ay: Lateral acceleration in G, positive = right
        """
        # Store the latest values to be processed by the timer
        self._latest_ax = ax
        self._latest_ay = ay
        self._needs_update = True

    def _update_plot(self):
        """Update the plot based on the latest acceleration values."""
        # Only process if there's a pending update
        if not self._needs_update:
            return

        # Update the actual values used for drawing
        self._ax = self._latest_ax
        self._ay = self._latest_ay
        self._needs_update = False

        # Add current point to history only every few updates
        self._update_counter += 1
        if self._update_counter >= self._update_frequency:
            self._update_counter = 0
            # Only add if within display range
            if (
                self._min_g <= self._ax <= self._max_g
                and self._min_g <= self._ay <= self._max_g
            ):
                # Only add if this is a new point (avoid duplicates)
                if not self._history or (self._ax, self._ay) != self._history[-1]:
                    self._history.append((self._ax, self._ay))

        # Trigger repaint
        self.update()

    def paintEvent(self, event):
        """
        Paint the G-G diagram.

        Args:
            event: Paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get widget dimensions
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) * 0.45  # 45% of smaller dimension

        # Draw background and bezel
        self._draw_background(painter, center_x, center_y, radius)

        # Draw grid
        self._draw_grid(painter, center_x, center_y, radius)

        # Draw axes labels and ticks
        self._draw_axes_labels_and_ticks(painter, center_x, center_y, radius)

        # Draw acceleration traces (points only, no lines)
        self._draw_accel_points(painter, center_x, center_y, radius)

        # Draw current acceleration dot
        self._draw_accel_dot(painter, center_x, center_y, radius)

        # Draw numeric display
        self._draw_numeric_display(painter, width, height)

    def _draw_background(self, painter, center_x, center_y, radius):
        """Draw the background and maximum G envelope."""
        # Draw outer circle (bezel) using QRectF
        painter.setPen(QPen(QColor(60, 60, 60), 2))
        painter.setBrush(QColor(30, 30, 30))
        painter.drawEllipse(
            QRectF(
                center_x - radius - 5,
                center_y - radius - 5,
                (radius + 5) * 2,
                (radius + 5) * 2,
            )
        )

        # Draw inner black background using QRectF
        painter.setPen(QPen(QColor(50, 50, 50), 1))
        painter.setBrush(QColor(0, 0, 0))
        painter.drawEllipse(
            QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2)
        )

    def _draw_grid(self, painter, center_x, center_y, radius):
        """Draw the grid lines showing G force intervals."""
        # Major and minor grid circles
        major_g_step = 0.5  # Major grid circles (0.5G, 1.0G, etc.)
        minor_g_step = 0.1  # Minor grid circles (0.1G, 0.2G, etc.)

        # Draw minor grid circles first (so they're behind major ones)
        g = minor_g_step
        while g <= self._max_g:
            # Skip major grid values as they'll be drawn later with different style
            if g % major_g_step != 0:
                # Calculate radius scaling based on the range
                circle_radius = (g / self._max_g) * radius

                # Set pen style for minor grid
                painter.setPen(QPen(QColor(50, 50, 50), 0.5, Qt.DotLine))

                # Draw the circle using QRectF
                painter.drawEllipse(
                    QRectF(
                        center_x - circle_radius,
                        center_y - circle_radius,
                        circle_radius * 2,
                        circle_radius * 2,
                    )
                )
            g += minor_g_step

        # Draw major grid circles
        g = major_g_step
        while g <= self._max_g:
            # Calculate radius scaling based on the range
            # Make sure the max G value maps to the full radius
            circle_radius = (g / self._max_g) * radius

            # Set pen style based on G value
            if g == 1.0:
                # Highlight the 1G circle if present
                painter.setPen(QPen(QColor(100, 100, 255), 1.5))
            else:
                painter.setPen(QPen(QColor(80, 80, 80), 1, Qt.DashLine))

            # Draw the circle using QRectF
            painter.drawEllipse(
                QRectF(
                    center_x - circle_radius,
                    center_y - circle_radius,
                    circle_radius * 2,
                    circle_radius * 2,
                )
            )

            # Add G value label at 45 degrees (northeast)
            label_x = center_x + circle_radius * 0.7071  # 45 degrees
            label_y = center_y - circle_radius * 0.7071
            painter.setPen(Qt.white)
            painter.setFont(QFont("Arial", 8))
            painter.drawText(int(label_x), int(label_y), f"{g}G")

            g += major_g_step

        # Draw radial lines every 30 degrees (major) and 15 degrees (minor)
        # Major radial lines
        painter.setPen(QPen(QColor(60, 60, 60), 1, Qt.DashLine))
        for angle in range(0, 360, 30):
            rad_angle = math.radians(angle)
            end_x = center_x + radius * math.cos(rad_angle)
            end_y = center_y - radius * math.sin(rad_angle)
            painter.drawLine(center_x, center_y, int(end_x), int(end_y))

        # Minor radial lines (at 15-degree intervals)
        painter.setPen(QPen(QColor(40, 40, 40), 0.5, Qt.DotLine))
        for angle in range(
            15, 360, 30
        ):  # Start at 15 and step by 30 to get 15, 45, 75, etc.
            rad_angle = math.radians(angle)
            end_x = center_x + radius * math.cos(rad_angle)
            end_y = center_y - radius * math.sin(rad_angle)
            painter.drawLine(center_x, center_y, int(end_x), int(end_y))

    def _draw_axes_labels_and_ticks(self, painter, center_x, center_y, radius):
        """Draw the axes labels and ticks."""
        # Set font and color
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 9))

        # X-axis label (Lateral G)
        x_label_rect = QRectF(center_x + radius * 0.8, center_y + 10, 100, 20)
        painter.drawText(x_label_rect, Qt.AlignLeft | Qt.AlignVCenter, "Ay")

        # Y-axis label (Longitudinal G) - moved down to avoid overlap with title
        y_label_rect = QRectF(center_x - 30, center_y - radius * 0.9, 100, 20)
        painter.drawText(y_label_rect, Qt.AlignCenter, "Ax")

        # X-axis
        painter.setPen(QPen(Qt.white, 1))
        painter.drawLine(
            int(center_x - radius), center_y, int(center_x + radius), center_y
        )

        # Y-axis
        painter.drawLine(
            center_x, int(center_y + radius), center_x, int(center_y - radius)
        )

        # Calculate tick steps based on the G range
        major_tick_step = 0.5  # Major ticks at 0.5G intervals
        minor_tick_step = 0.1  # Minor ticks at 0.1G intervals

        # Generate major tick values (for labels)
        major_tick_values = []
        tick_val = self._min_g
        while tick_val <= self._max_g:
            if tick_val != 0:  # Skip the center point
                major_tick_values.append(tick_val)
            tick_val += major_tick_step

        # Generate minor tick values (for shorter ticks)
        minor_tick_values = []
        tick_val = self._min_g
        while tick_val <= self._max_g:
            if (
                tick_val != 0 and tick_val % major_tick_step != 0
            ):  # Skip center and major ticks
                minor_tick_values.append(tick_val)
            tick_val += minor_tick_step

        # Draw X-axis major ticks and labels
        for value in major_tick_values:
            # Calculate the normalized position from -max_g to max_g range
            normalized_value = value / self._max_g

            # Calculate tick position
            tick_x = center_x + normalized_value * radius

            # Draw tick mark
            painter.setPen(QPen(Qt.white, 1))
            painter.drawLine(int(tick_x), center_y - 5, int(tick_x), center_y + 5)

            # Draw label
            tick_label = f"{value:+.1f}"
            tick_label = tick_label.replace(".0", "")  # Remove .0 for whole numbers
            painter.setFont(QFont("Arial", 7))
            label_rect = QRectF(tick_x - 15, center_y + 7, 30, 15)
            painter.drawText(label_rect, Qt.AlignCenter, tick_label)

        # Draw X-axis minor ticks (more visible now)
        for value in minor_tick_values:
            # Calculate the normalized position
            normalized_value = value / self._max_g

            # Calculate tick position
            tick_x = center_x + normalized_value * radius

            # Draw slightly more visible minor tick mark (longer and brighter)
            painter.setPen(QPen(QColor(200, 200, 200), 0.7))
            painter.drawLine(int(tick_x), center_y - 3, int(tick_x), center_y + 3)

        # Draw Y-axis major ticks and labels
        for value in major_tick_values:
            # Calculate the normalized position
            normalized_value = value / self._max_g

            # Calculate tick position (negative because Y increases downward in screen coords)
            tick_y = center_y - normalized_value * radius

            # Draw tick mark
            painter.setPen(QPen(Qt.white, 1))
            painter.drawLine(center_x - 5, int(tick_y), center_x + 5, int(tick_y))

            # Draw label
            tick_label = f"{value:+.1f}"
            tick_label = tick_label.replace(".0", "")  # Remove .0 for whole numbers
            painter.setFont(QFont("Arial", 7))
            label_rect = QRectF(center_x - 25, tick_y - 7, 20, 15)
            painter.drawText(label_rect, Qt.AlignRight | Qt.AlignVCenter, tick_label)

        # Draw Y-axis minor ticks (more visible now)
        for value in minor_tick_values:
            # Calculate the normalized position
            normalized_value = value / self._max_g

            # Calculate tick position
            tick_y = center_y - normalized_value * radius

            # Draw slightly more visible minor tick mark (longer and brighter)
            painter.setPen(QPen(QColor(200, 200, 200), 0.7))
            painter.drawLine(center_x - 3, int(tick_y), center_x + 3, int(tick_y))

    def _draw_accel_points(self, painter, center_x, center_y, radius):
        """Draw the acceleration history as individual points (no lines)."""
        if not self._history:
            return

        # Draw all history points as visible dots using accent color
        point_size = 3  # Larger size for better visibility
        painter.setPen(Qt.NoPen)
        # Use accent color with some transparency
        accent_color = QColor(config.ACCENT_COLOR)
        accent_color.setAlpha(200)
        painter.setBrush(accent_color)

        for ax, ay in self._history:
            # Calculate screen position - normalize to map the full range to the radius
            x = center_x + (ay / self._max_g) * radius
            y = center_y - (ax / self._max_g) * radius

            # Draw a small circle at each history position
            painter.drawEllipse(
                QRectF(x - point_size / 2, y - point_size / 2, point_size, point_size)
            )

    def _draw_accel_dot(self, painter, center_x, center_y, radius):
        """Draw the acceleration dot showing current G forces."""
        # Calculate dot position - normalize the acceleration values
        x = center_x + (self._ay / self._max_g) * radius
        y = center_y - (self._ax / self._max_g) * radius

        # Draw dot using QRectF with accent color
        painter.setPen(Qt.black)
        painter.setBrush(QColor(config.ACCENT_COLOR))
        painter.drawEllipse(QRectF(x - 5, y - 5, 10, 10))

        # Draw lines to axes
        painter.setPen(QPen(QColor(100, 100, 100), 1, Qt.DashLine))
        painter.drawLine(int(x), int(y), int(x), center_y)
        painter.drawLine(int(x), int(y), center_x, int(y))

    def _draw_numeric_display(self, painter, width, height):
        """Draw the numeric display of current values."""
        # Format acceleration values
        text = f"Ax: {self._ax:.2f}G  Ay: {self._ay:.2f}G"

        # Draw in bottom-right corner
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 10))
        text_rect = QRectF(width - 150, height - 30, 140, 25)
        painter.drawText(text_rect, Qt.AlignRight | Qt.AlignVCenter, text)

    def set_update_interval(self, interval_ms):
        """Set the update interval for the GG diagram.

        Args:
            interval_ms: Update interval in milliseconds
        """
        if self._update_timer.isActive():
            self._update_timer.stop()
        self._update_timer.start(interval_ms)

    def clear_history(self):
        """Clear the trace history."""
        self._history.clear()
        self.update()
