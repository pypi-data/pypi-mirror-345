"""
Speedometer widget for displaying speed and acceleration.
"""

import math

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen, QRadialGradient
from PyQt5.QtWidgets import QSizePolicy, QWidget

from force_fusion import config


class SpeedometerWidget(QWidget):
    """
    Widget that displays a circular speedometer with speed and acceleration.

    Features:
    - Circular gauge showing speed
    - Digital speed readout
    - Acceleration indicator bar
    """

    def __init__(self, parent=None):
        """
        Initialize the speedometer widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Current values
        self._speed = 0.0  # mi/h (changed from km/h)
        self._acceleration = 0.0  # m/s²
        self._ax = 0.0  # Longitudinal acceleration
        self._ay = 0.0  # Lateral acceleration

        # Cached calculated values
        self._speed_angle = 0.0

        # Gauge appearance settings
        self._min_angle = 135  # Start angle in degrees
        self._max_angle = 405  # End angle in degrees (45° past 0)
        self._min_speed = config.SPEED_MIN
        self._max_speed = config.SPEED_MAX

        # Set widget properties
        self.setMinimumSize(200, 200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(config.BACKGROUND_COLOR))
        self.setPalette(palette)

    def update_speed(self, speed):
        """
        Update the speed value.

        Args:
            speed: Speed in km/h from sensor
        """
        # Convert km/h to mi/h for internal use
        mph_speed = speed * 0.621371
        self._speed = max(self._min_speed, min(self._max_speed, mph_speed))
        self._recalculate()
        self.update()

    def update_acceleration(self, ax, ay=None):
        """
        Update the acceleration value.

        Args:
            ax: Longitudinal acceleration in m/s²
            ay: Lateral acceleration in m/s² (optional)
        """
        self._ax = ax
        if ay is not None:
            self._ay = ay
            # Calculate combined acceleration vector magnitude
            self._acceleration = math.sqrt(ax * ax + ay * ay)
        else:
            # Keep backward compatibility - just use ax
            self._acceleration = ax
        self.update()

    def _recalculate(self):
        """Recalculate derived values like angles."""
        # Calculate angle based on speed in mi/h
        speed_range = self._max_speed - self._min_speed
        angle_range = self._max_angle - self._min_angle

        if speed_range <= 0:
            self._speed_angle = self._min_angle
        else:
            # Use the mi/h value directly for the angle calculation
            normalized_speed = (self._speed - self._min_speed) / speed_range
            self._speed_angle = self._min_angle + normalized_speed * angle_range

    def paintEvent(self, event):
        """
        Paint the speedometer.

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
        self._draw_background(painter, center_x, center_y, radius)

        # Draw gauge ticks and labels
        self._draw_ticks_and_labels(painter, center_x, center_y, radius)

        # Draw speed needle
        self._draw_needle(painter, center_x, center_y, radius)

        # Draw digital speed and acceleration readout (moved above needle)
        self._draw_digital_readout(painter, center_x, center_y, radius)

        # Draw acceleration bar (position adjusted if necessary)
        self._draw_acceleration_bar(painter, center_x, center_y, radius)

    def _draw_background(self, painter, center_x, center_y, radius):
        """Draw the speedometer background."""
        # Outer circle
        painter.setPen(QPen(QColor(60, 60, 60), 1))
        painter.setBrush(QColor(40, 40, 40))
        painter.drawEllipse(
            center_x - radius, center_y - radius, radius * 2, radius * 2
        )

        # Inner circle with radial gradient - reduced size to leave more room for gauge
        gradient = QRadialGradient(center_x, center_y, radius * 0.75)
        gradient.setColorAt(0, QColor(50, 50, 50))
        gradient.setColorAt(1, QColor(25, 25, 25))
        painter.setBrush(gradient)
        painter.drawEllipse(
            int(center_x - radius * 0.75),
            int(center_y - radius * 0.75),
            int(radius * 1.5),
            int(radius * 1.5),
        )

    def _draw_ticks_and_labels(self, painter, center_x, center_y, radius):
        """Draw the speedometer ticks and speed labels."""
        # Set up fonts
        label_font = QFont("Arial", 8)
        painter.setFont(label_font)

        # Set up pens
        major_tick_pen = QPen(QColor(200, 200, 200), 2)
        micro_tick_pen = QPen(QColor(100, 100, 100), 0.5)  # For the smallest ticks
        label_pen = QPen(QColor(config.TEXT_COLOR), 1)

        # Calculate angles and values
        angle_range = self._max_angle - self._min_angle
        speed_range = self._max_speed - self._min_speed

        # Define tick steps in mph - modified as requested to show every 5 mph
        major_step_mph = (
            5  # Show major ticks (with labels) every 5 mph (changed from 10)
        )
        minor_step_mph = 1  # Show minor ticks every 1 mph

        # Draw arc - expanded to use more of the circle
        arc_rect = QRectF(
            center_x - radius * 0.95,
            center_y - radius * 0.95,
            radius * 1.9,
            radius * 1.9,
        )

        # Draw gradient arc from green to red
        start_angle = self._min_angle * 16  # QPainter uses 1/16th degrees
        span_angle = (self._max_angle - self._min_angle) * 16

        # Arc colors
        green = QColor(config.SUCCESS_COLOR)
        yellow = QColor(config.WARNING_COLOR)
        red = QColor(config.DANGER_COLOR)

        # Draw arcs in segments - increased pen width for more visible arc
        segment_count = 3
        for i in range(segment_count):
            segment_start = start_angle + (span_angle * i) // segment_count
            segment_span = span_angle // segment_count

            if i == 0:
                color = green
            elif i == 1:
                color = yellow
            else:
                color = red

            painter.setPen(QPen(color, 4))  # Increased thickness
            painter.drawArc(arc_rect, segment_start, segment_span)

        # Draw ticks and labels in mph directly
        for speed_mph in range(0, int(self._max_speed) + 1, minor_step_mph):
            # Calculate angle for this speed
            angle = (
                self._min_angle
                + (speed_mph - self._min_speed) * angle_range / speed_range
            )
            angle_rad = math.radians(angle)

            # Determine tick type
            is_major = speed_mph % major_step_mph == 0  # Every 5 mph

            # Calculate inner position based on tick type - adjusted for expanded arc
            if is_major:
                inner_radius = radius * 0.75  # Major ticks start farthest in
                outer_radius = radius * 0.95  # Extended to match the expanded arc
            else:  # minor tick
                inner_radius = radius * 0.85  # Minor ticks are shorter
                outer_radius = radius * 0.95  # Extended to match the expanded arc

            inner_x = center_x + inner_radius * math.cos(angle_rad)
            inner_y = center_y - inner_radius * math.sin(angle_rad)
            outer_x = center_x + outer_radius * math.cos(angle_rad)
            outer_y = center_y - outer_radius * math.sin(angle_rad)

            # Draw the tick mark with appropriate pen
            if is_major:
                painter.setPen(major_tick_pen)
            else:
                painter.setPen(micro_tick_pen)

            painter.drawLine(int(inner_x), int(inner_y), int(outer_x), int(outer_y))

            # Draw speed label for major ticks
            if is_major:
                # Draw speed label in mph - adjusted position for expanded arc
                painter.setPen(label_pen)
                label_x = center_x + (radius * 0.65) * math.cos(angle_rad)
                label_y = center_y - (radius * 0.65) * math.sin(angle_rad)

                # Adjust for text metrics
                text = str(speed_mph)
                metrics = QFontMetrics(label_font)
                text_width = metrics.horizontalAdvance(text)
                text_height = metrics.height()

                # Center the text on the calculated position
                label_rect = QRectF(
                    label_x - text_width / 2,
                    label_y - text_height / 2,
                    text_width,
                    text_height,
                )

                painter.drawText(label_rect, Qt.AlignCenter, text)

    def _draw_needle(self, painter, center_x, center_y, radius):
        """Draw the speed needle."""
        # Convert speed angle to radians
        angle_rad = math.radians(self._speed_angle)

        # Calculate needle end point - extended to match expanded arc
        needle_length = radius * 0.85  # Increased from 0.75 to reach the expanded arc
        end_x = center_x + needle_length * math.cos(angle_rad)
        end_y = center_y - needle_length * math.sin(angle_rad)

        # Draw needle
        painter.setPen(QPen(Qt.red, 2))
        painter.drawLine(center_x, center_y, int(end_x), int(end_y))

        # Draw center hub
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.setBrush(QColor(100, 100, 100))
        painter.drawEllipse(center_x - 5, center_y - 5, 10, 10)

    def _draw_digital_readout(self, painter, center_x, center_y, radius):
        """Draw the digital speed readout in mi/h and acceleration in G's."""
        # --- Speed ---
        # No conversion needed since we're already using mi/h internally
        speed_text = f"{self._speed:.1f} mi/h"

        # Set up font for speed
        speed_font = QFont("Arial", 16, QFont.Bold)
        painter.setFont(speed_font)
        speed_metrics = QFontMetrics(speed_font)
        speed_text_height = speed_metrics.height()

        # --- Acceleration ---
        # Convert acceleration from m/s² to G units (1G = 9.81 m/s²)
        accel_g = self._acceleration / 9.81

        # Set up font for acceleration
        accel_font = QFont("Arial", 10)
        painter.setFont(accel_font)
        accel_metrics = QFontMetrics(accel_font)
        accel_text_height = accel_metrics.height()

        # --- Layout ---
        # Define positions for text
        total_text_height = speed_text_height + accel_text_height + 5  # Reduced padding

        # Position the text above the center hub
        speed_rect = QRectF(
            center_x - radius * 0.6,  # Wider area for text
            center_y - radius * 0.4 - total_text_height,
            radius * 1.2,  # Wider area for text
            speed_text_height,
        )

        # Draw speed text
        painter.setFont(speed_font)
        painter.setPen(QColor(config.TEXT_COLOR))
        painter.drawText(speed_rect, Qt.AlignCenter, speed_text)

        # Draw acceleration text centered horizontally, below the speed text
        accel_rect = QRectF(
            center_x - radius * 0.6,  # Wider area for text
            speed_rect.bottom() + 2,  # Reduced padding between lines
            radius * 1.2,  # Wider area for text
            accel_text_height,
        )
        painter.setFont(accel_font)
        painter.setPen(QColor(config.TEXT_COLOR))
        combined_text = f"{accel_g:.2f} G"
        painter.drawText(accel_rect, Qt.AlignCenter, combined_text)

    def _draw_acceleration_bar(self, painter, center_x, center_y, radius):
        """Draw the acceleration indicator bar using m/s²."""
        # Define bar dimensions
        bar_width = radius * 0.8
        bar_height = radius * 0.15
        # Position bar further down
        bar_rect = QRectF(
            center_x - bar_width / 2,
            center_y + radius * 0.15,  # Adjusted position lower
            bar_width,
            bar_height,
        )

        # Draw bar background
        painter.setPen(QPen(QColor(60, 60, 60), 1))
        painter.setBrush(QColor(30, 30, 30))
        painter.drawRoundedRect(bar_rect, 3, 3)

        # Draw center line
        center_line_x = center_x
        painter.setPen(QPen(QColor(150, 150, 150), 1))
        painter.drawLine(
            center_line_x, int(bar_rect.top()), center_line_x, int(bar_rect.bottom())
        )

        # Define acceleration limits and ticks in m/s²
        accel_limit_ms2 = config.ACCEL_MAX  # Range is -ACCEL_MAX to ACCEL_MAX m/s²
        accel_marks_ms2 = [
            -accel_limit_ms2,
            -accel_limit_ms2 / 2,
            0,
            accel_limit_ms2 / 2,
            accel_limit_ms2,
        ]
        tick_height = bar_height * 0.6

        painter.setPen(QPen(QColor(150, 150, 150), 1))
        painter.setFont(QFont("Arial", 6))

        for accel_val in accel_marks_ms2:
            # Calculate x position based on acceleration value
            normalized_accel = accel_val / accel_limit_ms2
            x_pos = center_x + normalized_accel * (
                bar_width / 2 - 4
            )  # Subtract padding from edge

            # Draw tick mark
            painter.drawLine(
                int(x_pos),
                int(bar_rect.top() + (bar_height - tick_height) / 2),
                int(x_pos),
                int(bar_rect.top() + (bar_height - tick_height) / 2 + tick_height),
            )

            # Draw acceleration value label for non-zero ticks
            if accel_val != 0:
                label = f"{accel_val:.1f}"  # Label with m/s² value, unit label is below
                metrics = QFontMetrics(painter.font())
                text_width = metrics.horizontalAdvance(label)

                painter.drawText(
                    int(x_pos - text_width / 2), int(bar_rect.bottom() + 12), label
                )

        # Draw '0' label separately for better centering
        zero_label = "0"
        metrics = QFontMetrics(painter.font())
        text_width = metrics.horizontalAdvance(zero_label)
        painter.drawText(
            int(center_x - text_width / 2), int(bar_rect.bottom() + 12), zero_label
        )

        # Calculate position for acceleration indicator
        normalized_accel_indicator = (
            max(config.ACCEL_MIN, min(config.ACCEL_MAX, self._acceleration))
            / accel_limit_ms2
        )
        accel_pos_x = center_x + normalized_accel_indicator * (
            bar_width / 2 - 4
        )  # Subtract padding from edge

        # Draw acceleration indicator
        indicator_width = 6
        indicator_rect = QRectF(
            accel_pos_x - indicator_width / 2,
            bar_rect.top() + 2,
            indicator_width,
            bar_rect.height() - 4,
        )

        # Set color based on acceleration direction
        if self._acceleration >= 0:  # Changed to >= 0 for positive/zero
            accel_color = QColor(config.ACCEL_COLOR_POSITIVE)
        else:
            accel_color = QColor(config.ACCEL_COLOR_NEGATIVE)

        painter.setPen(Qt.NoPen)
        painter.setBrush(accel_color)
        painter.drawRoundedRect(indicator_rect, 2, 2)

        # Draw the acceleration value and unit label below the bar
        painter.setPen(QColor(config.TEXT_COLOR))

        # Format the current acceleration value
        accel_value_text = f"{self._acceleration:.2f}"
        unit_label = "m/s²"
        full_label = f"{accel_value_text} {unit_label}"  # Combine value and unit

        # Use a font for the combined label
        label_font = QFont("Arial", 8)  # Slightly larger font for combined label
        painter.setFont(label_font)
        metrics = QFontMetrics(label_font)
        label_width = metrics.horizontalAdvance(full_label)
        label_height = metrics.height()

        # Position the combined label centered below the number labels
        label_rect = QRectF(
            center_x - label_width / 2,
            bar_rect.bottom() + 15,  # Position below tick numbers
            label_width,
            label_height,
        )
        painter.drawText(label_rect, Qt.AlignCenter, full_label)
