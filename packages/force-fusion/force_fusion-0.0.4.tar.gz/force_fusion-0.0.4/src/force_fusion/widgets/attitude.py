"""
Attitude widget for displaying vehicle pitch and roll.

Based on aircraft attitude indicator design with blue sky and brown ground.
"""

import math
import os

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QPixmap, QPolygonF
from PyQt5.QtWidgets import QSizePolicy, QWidget

from force_fusion import config

# Define resource paths relative to this file
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))  # widgets/
RESOURCE_DIR = os.path.abspath(
    os.path.join(CURRENT_DIR, "..", "resources")
)  # force_fusion/resources
CAR_SIDE_PATH = os.path.join(RESOURCE_DIR, "car_side.svg")
CAR_BACK_PATH = os.path.join(RESOURCE_DIR, "car_back.svg")


class AttitudeWidget(QWidget):
    """
    Widget that displays an aircraft-style attitude indicator showing vehicle pitch and roll.

    Features:
    - Blue sky / brown ground representation
    - Artificial horizon
    - Pitch ladder markings
    - Roll markings
    - Vehicle reference symbol
    """

    def __init__(self, parent=None):
        """
        Initialize the attitude indicator widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Current attitude values
        self._pitch = 0.0  # degrees
        self._roll = 0.0  # degrees

        # Attitude indicator settings - use config values
        self._pitch_scale_max = config.PITCH_MAX  # degrees
        self._roll_scale_max = config.ROLL_MAX  # degrees
        self._pitch_step = 10.0  # Degrees between pitch marks

        # Load car icons (might use for reference symbol)
        self._car_side_pixmap = QPixmap(CAR_SIDE_PATH)
        self._car_back_pixmap = QPixmap(CAR_BACK_PATH)

        # If images couldn't be loaded, use basics
        if self._car_side_pixmap.isNull():
            print(f"Warning: Could not load {CAR_SIDE_PATH}. Using placeholder.")
            self._car_side_pixmap = QPixmap(10, 10)
            self._car_side_pixmap.fill(Qt.white)

        if self._car_back_pixmap.isNull():
            print(f"Warning: Could not load {CAR_BACK_PATH}. Using placeholder.")
            self._car_back_pixmap = QPixmap(10, 10)
            self._car_back_pixmap.fill(Qt.white)

        # Set widget properties
        self.setMinimumSize(200, 200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(config.BACKGROUND_COLOR))
        self.setPalette(palette)

        # Define colors for sky and ground
        self._sky_color = QColor(0, 180, 255)  # Sky blue
        self._ground_color = QColor(160, 120, 50)  # Brown earth

    def set_pitch(self, pitch):
        """
        Set the pitch angle.

        Args:
            pitch: Pitch angle in degrees
        """
        self._pitch = max(config.PITCH_MIN, min(config.PITCH_MAX, pitch))
        self.update()

    def set_roll(self, roll):
        """
        Set the roll angle.

        Args:
            roll: Roll angle in degrees
        """
        self._roll = max(config.ROLL_MIN, min(config.ROLL_MAX, roll))
        self.update()

    def paintEvent(self, event):
        """
        Paint the aircraft-style attitude indicator.

        Args:
            event: Paint event
        """
        # Create painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get widget dimensions and calculate radius/center
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2

        # Use the smaller dimension for the attitude sphere
        diameter = min(width, height)
        radius = (diameter // 2) - 20  # Padding from edges

        # Draw outer frame and background
        self._draw_background(painter, center_x, center_y, radius)

        # Draw the attitude sphere (sky/ground representation)
        self._draw_attitude_sphere(painter, center_x, center_y, radius)

        # Draw pitch and roll indicators
        self._draw_pitch_ladder(painter, center_x, center_y, radius)
        self._draw_roll_markings(painter, center_x, center_y, radius)

        # Draw fixed aircraft reference symbol
        self._draw_aircraft_symbol(painter, center_x, center_y, radius)

        # Draw value displays
        self._draw_value_displays(painter, center_x, center_y, radius)

        # Draw title
        painter.setPen(QColor(config.TEXT_COLOR))
        painter.setFont(QFont("Arial", 10))
        painter.drawText(QRectF(0, 5, width, 20), Qt.AlignCenter, "Attitude")

    def _draw_background(self, painter, center_x, center_y, radius):
        """Draw the outer bezel and background of the gauge."""
        # Draw outer dark circle (bezel)
        painter.setPen(QPen(QColor(60, 60, 60), 2))
        painter.setBrush(QColor(30, 30, 30))
        painter.drawEllipse(
            center_x - radius - 5,
            center_y - radius - 5,
            (radius + 5) * 2,
            (radius + 5) * 2,
        )

        # Draw inner black background
        painter.setPen(QPen(QColor(50, 50, 50), 1))
        painter.setBrush(QColor(0, 0, 0))
        painter.drawEllipse(
            center_x - radius, center_y - radius, radius * 2, radius * 2
        )

    def _draw_attitude_sphere(self, painter, center_x, center_y, radius):
        """Draw the sky/ground attitude sphere that rotates with roll and moves with pitch."""
        # Save the current state to restore later
        painter.save()

        # Create clipping region (everything outside this will not be drawn)
        clip_path = QPainterPath()
        clip_path.addEllipse(
            center_x - radius, center_y - radius, radius * 2, radius * 2
        )
        painter.setClipPath(clip_path)

        # Move to center and rotate around center based on roll angle
        painter.translate(center_x, center_y)
        painter.rotate(
            -self._roll
        )  # Reverted: Negative roll rotates background CW (left side down for positive roll)

        # Calculate horizon offset based on pitch
        # Each 10 degrees of pitch = ~1/4 of the radius in distance
        pitch_offset = (self._pitch / 10.0) * (radius / 4.0)

        # Draw the ground (bottom half plus pitch offset - POSITIVE offset moves horizon DOWN for nose up)
        ground_rect = QRectF(-radius * 1.5, 0 + pitch_offset, radius * 3, radius * 3)
        painter.setBrush(self._ground_color)
        painter.setPen(Qt.NoPen)
        painter.drawRect(ground_rect)

        # Draw the sky (top half plus pitch offset - POSITIVE offset moves horizon DOWN for nose up)
        sky_rect = QRectF(
            -radius * 1.5, -radius * 3 + pitch_offset, radius * 3, radius * 3
        )
        painter.setBrush(self._sky_color)
        painter.setPen(Qt.NoPen)
        painter.drawRect(sky_rect)

        # Draw horizon line - convert float to int
        painter.setPen(QPen(Qt.white, 2))
        painter.drawLine(
            int(-radius * 1.2),
            int(pitch_offset),  # Use positive offset
            int(radius * 1.2),
            int(pitch_offset),  # Use positive offset
        )

        painter.restore()

    def _draw_pitch_ladder(self, painter, center_x, center_y, radius):
        """Draw the pitch ladder markings that show pitch attitude."""
        # Save the current state
        painter.save()

        # Create clipping region
        clip_path = QPainterPath()
        clip_path.addEllipse(
            center_x - radius, center_y - radius, radius * 2, radius * 2
        )
        painter.setClipPath(clip_path)

        # Move to center and rotate for roll
        painter.translate(center_x, center_y)
        painter.rotate(-self._roll)  # Reverted: Negative roll rotates background CW

        # Remove the outer pitch line arcs that might appear on edges
        # by only drawing pitch ladder lines (-30 to +30 degrees) in a limited horizontal range
        line_width = radius * 0.5  # Reduced from 0.6 to avoid edge arcs

        # Draw pitch ladder lines (up to +/- 30 degrees)
        for pitch in range(-30, 31, 10):
            # Skip horizon (0 degrees) as it's already drawn
            if pitch == 0:
                continue

            # Calculate vertical position for this pitch angle
            # Positive pitch moves lines DOWN
            y_pos = (pitch / 10.0) * (radius / 4.0)

            # Different appearance for positive vs negative pitch
            if (
                pitch > 0
            ):  # Above horizon (lines appear below center when pitch is positive/nose up)
                # Draw line with gap in the middle - convert float to int
                painter.setPen(QPen(Qt.white, 1))
                painter.drawLine(
                    int(-line_width / 2), int(y_pos), int(-line_width / 8), int(y_pos)
                )
                painter.drawLine(
                    int(line_width / 8), int(y_pos), int(line_width / 2), int(y_pos)
                )

                # Draw short tickmarks on ends - convert float to int
                painter.drawLine(
                    int(-line_width / 2),
                    int(y_pos),
                    int(-line_width / 2),
                    int(y_pos - 3),
                )
                painter.drawLine(
                    int(line_width / 2), int(y_pos), int(line_width / 2), int(y_pos - 3)
                )
            else:  # Below horizon
                # Draw solid line - convert float to int
                painter.setPen(QPen(Qt.white, 1))
                painter.drawLine(
                    int(-line_width / 2), int(y_pos), int(line_width / 2), int(y_pos)
                )

                # Draw short tickmarks on ends pointing down - convert float to int
                painter.drawLine(
                    int(-line_width / 2),
                    int(y_pos),
                    int(-line_width / 2),
                    int(y_pos + 3),
                )
                painter.drawLine(
                    int(line_width / 2), int(y_pos), int(line_width / 2), int(y_pos + 3)
                )

            # Draw pitch angle labels
            text = str(abs(pitch))
            painter.setFont(QFont("Arial", 7))
            text_width = painter.fontMetrics().horizontalAdvance(text)

            # Draw left number
            painter.drawText(
                int(-line_width / 2 - text_width - 5), int(y_pos + 4), text
            )

            # Draw right number
            painter.drawText(int(line_width / 2 + 5), int(y_pos + 4), text)

        painter.restore()

    def _draw_roll_markings(self, painter, center_x, center_y, radius):
        """Draw roll degree markings at the top of the gauge."""
        # Draw roll markings at the top of the attitude indicator
        painter.save()

        # Draw roll arc at the top (very subtle - just the markers)
        painter.setPen(QPen(Qt.white, 1))
        arc_radius = radius * 0.85

        # Draw roll tick marks
        tick_angles = [0, 10, 20, 30, -10, -20, -30]
        for angle in tick_angles:
            # Convert angle to radians (0 is at the top, positive is clockwise)
            angle_rad = math.radians(90 - angle)

            # Calculate tick mark start and end positions
            start_x = center_x + arc_radius * math.cos(angle_rad)
            start_y = center_y - arc_radius * math.sin(angle_rad)

            # Longer ticks for major angles
            tick_length = 7 if angle in [0, 30, -30] else 5
            end_x = center_x + (arc_radius - tick_length) * math.cos(angle_rad)
            end_y = center_y - (arc_radius - tick_length) * math.sin(angle_rad)

            painter.drawLine(int(start_x), int(start_y), int(end_x), int(end_y))

            # Add roll angle labels for 30 degree marks
            if angle in [30, -30]:
                text = str(abs(angle))
                # Position text slightly beyond the tick marks
                text_x = center_x + (arc_radius - tick_length - 12) * math.cos(
                    angle_rad
                )
                text_y = center_y - (arc_radius - tick_length - 12) * math.sin(
                    angle_rad
                )

                # Center the text around the calculated point
                text_rect = QRectF(int(text_x - 10), int(text_y - 10), 20, 20)
                painter.drawText(text_rect, Qt.AlignCenter, text)

        # Draw roll indicator (small triangle pointing to current roll)
        if hasattr(self, "_roll") and self._roll is not None:
            roll_rad = math.radians(90 - self._roll)
            roll_x = center_x + arc_radius * math.cos(roll_rad)
            roll_y = center_y - arc_radius * math.sin(roll_rad)

            # Create triangle pointing to roll markings
            triangle = QPolygonF()
            triangle.append(QPointF(roll_x, roll_y))
            triangle.append(QPointF(roll_x - 4, roll_y - 10))  # More pointy triangle
            triangle.append(QPointF(roll_x + 4, roll_y - 10))

            painter.setBrush(QColor(255, 255, 0))  # Yellow triangle
            painter.setPen(Qt.black)
            painter.drawPolygon(triangle)

        painter.restore()

    def _draw_aircraft_symbol(self, painter, center_x, center_y, radius):
        """Draw fixed aircraft reference symbol in the center."""
        # Draw the fixed aircraft reference symbol
        painter.setPen(QPen(Qt.white, 2))

        # Draw miniature wings and center dot
        wing_width = radius * 0.3

        # Left wing with angle indicators
        painter.drawLine(
            int(center_x - 3), int(center_y), int(center_x - wing_width), int(center_y)
        )

        # Right wing with angle indicators
        painter.drawLine(
            int(center_x + 3), int(center_y), int(center_x + wing_width), int(center_y)
        )

        # Center dot/circle
        painter.setBrush(Qt.white)
        painter.drawEllipse(center_x - 2, center_y - 2, 4, 4)

    def _draw_value_displays(self, painter, center_x, center_y, radius):
        """Draw the numeric pitch and roll values."""
        # Draw pitch value at bottom
        painter.setPen(QColor(config.TEXT_COLOR))
        painter.setFont(QFont("Arial", 14, QFont.Bold))
        pitch_text = f"{self._pitch:.2f}"
        pitch_rect = QRectF(center_x - 50, center_y + radius * 0.5, 100, 30)
        painter.drawText(pitch_rect, Qt.AlignCenter, pitch_text)

        # Draw roll value at top
        roll_text = f"{self._roll:.2f}"
        roll_rect = QRectF(center_x - 50, center_y - radius * 0.5 - 30, 100, 30)
        painter.drawText(roll_rect, Qt.AlignCenter, roll_text)
