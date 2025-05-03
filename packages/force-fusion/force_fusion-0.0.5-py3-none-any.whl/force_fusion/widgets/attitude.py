"""
Attitude widget for displaying vehicle roll and pitch.

Displays roll on top half (back view) and pitch on bottom half (side view).
"""

import math
import os

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPen, QPolygonF
from PyQt5.QtSvg import QSvgRenderer
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
    Widget that displays a dual-gauge attitude indicator showing vehicle roll and pitch.

    Features:
    - Top half: Roll indicator with car rear view
    - Bottom half: Pitch indicator with car side view
    - Color-coded tick marks
    - Numeric value display
    - SVG car icons that rotate with the vehicle
    """

    def __init__(self, parent=None):
        """
        Initialize the attitude widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Current attitude values
        self._roll = -2.0  # degrees, positive = right wing up
        self._pitch = 17.0  # degrees, positive = nose up

        # Angle limits
        self._max_angle = config.ROLL_MAX  # max angle display in degrees

        # Try to load SVG renderers
        self._car_back_renderer = QSvgRenderer()
        self._car_side_renderer = QSvgRenderer()

        # Try to load from resources or filesystem
        self._car_back_renderer.load(CAR_BACK_PATH)
        self._car_side_renderer.load(CAR_SIDE_PATH)

        # Set widget properties
        self.setMinimumSize(200, 200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(config.BACKGROUND_COLOR))
        self.setPalette(palette)

    def setRoll(self, roll_deg):
        """
        Set the roll angle.

        Args:
            roll_deg: Roll angle in degrees, positive = right wing up
        """
        self._roll = max(-self._max_angle, min(self._max_angle, roll_deg))
        self.update()

    def setPitch(self, pitch_deg):
        """
        Set the pitch angle.

        Args:
            pitch_deg: Pitch angle in degrees, positive = nose up
        """
        self._pitch = max(-self._max_angle, min(self._max_angle, pitch_deg))
        self.update()

    # Legacy method support
    def set_roll(self, roll_deg):
        """Legacy method for compatibility with existing code."""
        self.setRoll(roll_deg)

    def set_pitch(self, pitch_deg):
        """Legacy method for compatibility with existing code."""
        self.setPitch(pitch_deg)

    def paintEvent(self, event):
        """
        Paint the attitude indicator.

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
        radius = min(width, height) // 2 - 10

        # Draw background and bezel
        self._draw_background(painter, center_x, center_y, radius)

        # Draw roll gauge (top half)
        self._draw_roll_gauge(painter, center_x, center_y, radius)

        # Draw pitch gauge (bottom half)
        self._draw_pitch_gauge(painter, center_x, center_y, radius)

        # Draw plus and minus signs
        self._draw_plus_minus_signs(painter, center_x, center_y, radius)

        # Remove title drawing - now handled by main UI
        # painter.setPen(QColor(config.TEXT_COLOR))
        # painter.setFont(QFont("Arial", 10))
        # painter.drawText(QRectF(0, 5, width, 20), Qt.AlignCenter, "Attitude")

    def _draw_background(self, painter, center_x, center_y, radius):
        """Draw the outer bezel and background."""
        # Define colors for bezel and background
        bezel_color = QColor(config.BEZEL_COLOR)
        bezel_border_color = QColor(config.BEZEL_BORDER_COLOR)
        background_color = QColor(0, 0, 0)

        # Draw dark bezel (outer circle)
        painter.setPen(QPen(bezel_border_color, 2))
        painter.setBrush(bezel_color)
        painter.drawEllipse(
            center_x - radius - 5,
            center_y - radius - 5,
            (radius + 5) * 2,
            (radius + 5) * 2,
        )

        # Draw black background (inner circle)
        painter.setPen(QPen(bezel_border_color, 1))
        painter.setBrush(background_color)
        painter.drawEllipse(
            center_x - radius, center_y - radius, radius * 2, radius * 2
        )

    def _draw_plus_minus_signs(self, painter, center_x, center_y, radius):
        """Draw plus and minus signs on the left and right sides of the gauge."""
        # Set up font and color
        painter.setPen(QColor(config.TEXT_COLOR))
        painter.setFont(QFont("Arial", 16, QFont.Bold))

        # Draw plus sign on right side
        plus_rect = QRectF(center_x + radius - 25, center_y - 15, 30, 30)
        painter.drawText(plus_rect, Qt.AlignCenter, "+")

        # Draw minus sign on left side
        minus_rect = QRectF(center_x - radius - 5, center_y - 15, 30, 30)
        painter.drawText(minus_rect, Qt.AlignCenter, "−")

    def _draw_roll_gauge(self, painter, center_x, center_y, radius):
        """Draw the roll gauge in the top half of the widget."""
        # Save painter state
        painter.save()

        # Create clipping region for top half
        painter.setClipRect(0, 0, self.width(), center_y)

        # Draw the roll angle ticks
        self._draw_roll_ticks(painter, center_x, center_y, radius)

        # Draw the roll pointer (cyan triangle)
        self._draw_roll_pointer(painter, center_x, center_y, radius)

        # Draw the car back view icon
        self._draw_car_back(painter, center_x, center_y, radius)

        # Restore painter state
        painter.restore()

    def _draw_roll_ticks(self, painter, center_x, center_y, radius):
        """Draw the roll angle tick marks around the top semicircle."""
        # Extended list of tick angles with more increments
        tick_angles = [
            -40,
            -35,
            -30,
            -25,
            -20,
            -15,
            -10,
            -5,
            0,
            5,
            10,
            15,
            20,
            25,
            30,
            35,
            40,
        ]

        for angle in tick_angles:
            # Convert to radians (0 at top, positive clockwise)
            rad_angle = math.radians(90 - angle)

            # Calculate tick mark positions
            outer_x = center_x + (radius - 5) * math.cos(rad_angle)
            outer_y = center_y - (radius - 5) * math.sin(rad_angle)

            # Use different inner radius for major vs minor ticks
            if angle % 10 == 0:  # Major ticks (10, 20, 30, 40)
                inner_x = center_x + (radius - 15) * math.cos(rad_angle)
                inner_y = center_y - (radius - 15) * math.sin(rad_angle)
                tick_width = 2
            else:  # Minor ticks (5, 15, 25, 35)
                inner_x = center_x + (radius - 10) * math.cos(rad_angle)
                inner_y = center_y - (radius - 10) * math.sin(rad_angle)
                tick_width = 1

            # Determine color based on angle
            if abs(angle) == 40:
                tick_color = QColor(
                    config.DANGER_COLOR
                )  # Use red from config instead of Qt.red
            elif abs(angle) == 30:
                tick_color = QColor(
                    config.WARNING_COLOR
                )  # Use orange from config instead of hardcoded
            else:
                tick_color = QColor(
                    config.TEXT_COLOR
                )  # Use text color from config instead of Qt.white

            # Draw the tick mark
            painter.setPen(QPen(tick_color, tick_width))
            painter.drawLine(int(outer_x), int(outer_y), int(inner_x), int(inner_y))

            # Draw labels for major ticks (10 degree increments)
            if angle % 10 == 0 and angle != 0:
                label_x = center_x + (radius - 30) * math.cos(rad_angle)
                label_y = center_y - (radius - 30) * math.sin(rad_angle)

                # Adjust text alignment based on position
                rect = QRectF(label_x - 15, label_y - 10, 30, 20)
                painter.setPen(tick_color)
                painter.setFont(QFont("Arial", 8))
                painter.drawText(rect, Qt.AlignCenter, f"{abs(angle)}")

    def _draw_roll_pointer(self, painter, center_x, center_y, radius):
        """Draw the roll pointer (cyan triangle at top)."""
        # Calculate the pointer position (rotates with roll)
        # Move pointer closer to edge by using a larger radius
        pointer_radius = radius - 10  # Closer to the edge
        pointer_angle = math.radians(90 - self._roll)  # 0 at top, positive clockwise

        pointer_x = center_x + pointer_radius * math.cos(pointer_angle)
        pointer_y = center_y - pointer_radius * math.sin(pointer_angle)

        # Create a larger, more pointed triangle
        triangle = QPolygonF()
        # The tip points outward
        triangle.append(QPointF(pointer_x, pointer_y - 12))  # Taller tip
        # Make the base wider
        triangle.append(QPointF(pointer_x - 8, pointer_y + 4))  # Wider base
        triangle.append(QPointF(pointer_x + 8, pointer_y + 4))  # Wider base

        # Draw the pointer
        painter.setPen(Qt.black)
        painter.setBrush(
            QColor(config.ROLL_POINTER_COLOR)
        )  # Use config color instead of hardcoded
        painter.drawPolygon(triangle)

    def _draw_car_back(self, painter, center_x, center_y, radius):
        """Draw the car back view icon that rotates with roll."""
        # Save current state
        painter.save()

        # Position of the car SVG in the top half - move higher up (was 0.3)
        car_center_y = center_y - radius * 0.5

        # Move to center and rotate by roll angle
        painter.translate(center_x, car_center_y)
        painter.rotate(self._roll)

        # Calculate icon size (25% of radius instead of 30% to make it smaller)
        icon_size = int(radius * 0.25)

        # Draw horizontal reference line through the car to show tilt
        # Make the line longer (1.5x the icon size) and more visible
        painter.setPen(
            QPen(QColor(config.TEXT_COLOR), 2)
        )  # Use text color from config instead of Qt.white
        line_half_width = int(icon_size * 0.9)  # Extended beyond the icon
        painter.drawLine(-line_half_width, 0, line_half_width, 0)

        # Render the car back view if renderer is valid
        if self._car_back_renderer.isValid():
            self._car_back_renderer.render(
                painter, QRectF(-icon_size / 2, -icon_size / 2, icon_size, icon_size)
            )
        else:
            # Draw a simple car shape if no SVG is available
            painter.setPen(QColor(config.TEXT_COLOR))  # Use text color from config
            painter.setBrush(QColor(config.TEXT_COLOR))  # Use text color from config
            painter.drawRect(
                -icon_size / 4, -icon_size / 4, icon_size / 2, icon_size / 2
            )

        # Restore painter state
        painter.restore()

        # Draw roll value text below the SVG - move higher up (was 0.1)
        text_y = center_y - radius * 0.3
        painter.setPen(
            QColor(config.ROLL_POINTER_COLOR)
        )  # Use config color instead of hardcoded
        painter.setFont(QFont("Arial", 12))
        roll_text_rect = QRectF(center_x - 40, text_y, 80, 20)
        painter.drawText(roll_text_rect, Qt.AlignCenter, f"{self._roll:.0f}")

    def _draw_pitch_gauge(self, painter, center_x, center_y, radius):
        """Draw the pitch gauge in the bottom half of the widget."""
        # Save painter state
        painter.save()

        # Create clipping region for bottom half
        painter.setClipRect(0, center_y, self.width(), self.height())

        # Draw the pitch angle ticks
        self._draw_pitch_ticks(painter, center_x, center_y, radius)

        # Draw the pitch pointer (amber triangle)
        self._draw_pitch_pointer(painter, center_x, center_y, radius)

        # Draw the car side view icon
        self._draw_car_side(painter, center_x, center_y, radius)

        # Restore painter state
        painter.restore()

    def _draw_pitch_ticks(self, painter, center_x, center_y, radius):
        """Draw the pitch angle tick marks around the bottom semicircle."""
        # Extended list of tick angles with more increments
        tick_angles = [
            -40,
            -35,
            -30,
            -25,
            -20,
            -15,
            -10,
            -5,
            0,
            5,
            10,
            15,
            20,
            25,
            30,
            35,
            40,
        ]

        for angle in tick_angles:
            # For pitch gauge, positive angles (nose up) should appear on the right side
            # Invert the angle when drawing ticks for proper display
            display_angle = -angle

            # Convert to radians (0 at bottom, positive counterclockwise)
            rad_angle = math.radians(270 - display_angle)

            # Calculate tick mark positions
            outer_x = center_x + (radius - 5) * math.cos(rad_angle)
            outer_y = center_y - (radius - 5) * math.sin(rad_angle)

            # Use different inner radius for major vs minor ticks
            if angle % 10 == 0:  # Major ticks (10, 20, 30, 40)
                inner_x = center_x + (radius - 15) * math.cos(rad_angle)
                inner_y = center_y - (radius - 15) * math.sin(rad_angle)
                tick_width = 2
            else:  # Minor ticks (5, 15, 25, 35)
                inner_x = center_x + (radius - 10) * math.cos(rad_angle)
                inner_y = center_y - (radius - 10) * math.sin(rad_angle)
                tick_width = 1

            # Determine color based on angle
            if abs(angle) == 40:
                tick_color = QColor(
                    config.DANGER_COLOR
                )  # Use red from config instead of Qt.red
            elif abs(angle) == 30:
                tick_color = QColor(
                    config.WARNING_COLOR
                )  # Use orange from config instead of hardcoded
            else:
                tick_color = QColor(
                    config.TEXT_COLOR
                )  # Use text color from config instead of Qt.white

            # Draw the tick mark
            painter.setPen(QPen(tick_color, tick_width))
            painter.drawLine(int(outer_x), int(outer_y), int(inner_x), int(inner_y))

            # Draw labels for major ticks (10 degree increments)
            if angle % 10 == 0 and angle != 0:
                label_x = center_x + (radius - 30) * math.cos(rad_angle)
                label_y = center_y - (radius - 30) * math.sin(rad_angle)

                # Adjust text alignment based on position
                rect = QRectF(label_x - 15, label_y - 10, 30, 20)
                painter.setPen(tick_color)
                painter.setFont(QFont("Arial", 8))
                painter.drawText(rect, Qt.AlignCenter, f"{abs(angle)}")

    def _draw_pitch_pointer(self, painter, center_x, center_y, radius):
        """Draw the pitch pointer (amber triangle at bottom)."""
        # Calculate the pointer position (rotates with pitch)
        # Move pointer closer to edge by using a larger radius
        pointer_radius = radius - 10  # Closer to the edge
        # We need to invert the pitch angle for display (positive = right side)
        pointer_angle = math.radians(270 + self._pitch)  # 0 at bottom, invert the angle

        pointer_x = center_x + pointer_radius * math.cos(pointer_angle)
        pointer_y = center_y - pointer_radius * math.sin(pointer_angle)

        # Create a larger, more pointed triangle
        triangle = QPolygonF()
        # The tip points outward
        triangle.append(QPointF(pointer_x, pointer_y + 12))  # Taller tip
        # Make the base wider
        triangle.append(QPointF(pointer_x - 8, pointer_y - 4))  # Wider base
        triangle.append(QPointF(pointer_x + 8, pointer_y - 4))  # Wider base

        # Draw the pointer
        painter.setPen(Qt.black)
        painter.setBrush(
            QColor(config.PITCH_POINTER_COLOR)
        )  # Use config color instead of hardcoded
        painter.drawPolygon(triangle)

    def _draw_car_side(self, painter, center_x, center_y, radius):
        """Draw the car side view icon that rotates with pitch."""
        # Save current state
        painter.save()

        # Position of the car SVG in the bottom half - move lower (was 0.3)
        car_center_y = center_y + radius * 0.5

        # Move to center and rotate by pitch angle
        painter.translate(center_x, car_center_y)
        painter.rotate(-self._pitch)  # Negative because nose up is positive pitch

        # Calculate icon size (30% of radius)
        icon_size = int(radius * 0.3)

        # Draw horizontal reference line through the car to show tilt
        # Make the line longer (1.5x the icon size) and more visible
        painter.setPen(
            QPen(QColor(config.TEXT_COLOR), 2)
        )  # Use text color from config instead of Qt.white
        line_half_width = int(icon_size * 0.9)  # Extended beyond the icon
        painter.drawLine(-line_half_width, 0, line_half_width, 0)

        # Render the car side view if renderer is valid
        if self._car_side_renderer.isValid():
            self._car_side_renderer.render(
                painter, QRectF(-icon_size / 2, -icon_size / 2, icon_size, icon_size)
            )
        else:
            # Draw a simple car shape if no SVG is available
            painter.setPen(QColor(config.TEXT_COLOR))  # Use text color from config
            painter.setBrush(QColor(config.TEXT_COLOR))  # Use text color from config
            painter.drawRect(
                -icon_size / 4, -icon_size / 4, icon_size / 2, icon_size / 2
            )

        # Restore painter state
        painter.restore()

        # Draw pitch value text below the SVG - move lower (was 0.5)
        text_y = center_y + radius * 0.7
        painter.setPen(
            QColor(config.PITCH_POINTER_COLOR)
        )  # Use config color instead of hardcoded
        painter.setFont(QFont("Arial", 12))
        pitch_text_rect = QRectF(center_x - 40, text_y, 80, 20)
        painter.drawText(pitch_text_rect, Qt.AlignCenter, f"{self._pitch:.0f}")
