"""
Dashboard widget package.

This package contains all the custom widgets used by the Force-Fusion dashboard:
- MinimapWidget: 2D trajectory display
- SpeedometerWidget: Speed and acceleration display
- AttitudeWidget: Pitch and roll indicator
- HeadingWidget: Course-over-ground compass
- TireForceWidget: Tire normal force display
- MapboxView: 3D map with vehicle model
- GgDiagramWidget: Lateral vs. longitudinal G-force diagram
"""

from force_fusion.widgets.attitude import AttitudeWidget
from force_fusion.widgets.gg_diagram import GgDiagramWidget
from force_fusion.widgets.heading import HeadingWidget
from force_fusion.widgets.mapbox_view import MapboxView
from force_fusion.widgets.minimap import MinimapWidget
from force_fusion.widgets.speedometer import SpeedometerWidget
from force_fusion.widgets.tire_force import TireForceWidget

__all__ = [
    "MinimapWidget",
    "SpeedometerWidget",
    "AttitudeWidget",
    "HeadingWidget",
    "TireForceWidget",
    "MapboxView",
    "GgDiagramWidget",
]
