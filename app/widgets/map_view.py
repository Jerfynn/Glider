"""
2D/3D Dive Profile & Mission Trajectory Visualizer for Underwater Gliders.
Clean White / Light Theme.
"""

from collections import deque
import numpy as np
import pyqtgraph as pg
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
from app.config import COLORS
from app.core.telemetry_model import TelemetryPacket


class MapViewWidget(QFrame):
    """
    Shows real-time sawtooth depth dive profile with clean white theme.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MapViewCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("DIVE PROFILE & MISSION TRACK")
        title.setObjectName("CardTitle")
        hdr.addWidget(title)
        hdr.addStretch()

        self.btn_reset = QPushButton("RESET TRACK")
        self.btn_reset.setFixedHeight(24)
        self.btn_reset.clicked.connect(self.reset_track)
        hdr.addWidget(self.btn_reset)
        layout.addLayout(hdr)

        # Plot: Depth vs Elapsed Time
        self.plot_widget = pg.PlotWidget(self)
        self.plot_widget.setBackground(COLORS["bg_card"])
        self.plot_widget.showGrid(x=True, y=True, alpha=0.35)
        self.plot_widget.setLabel("left", "Depth (m)", color=COLORS["text_secondary"])
        self.plot_widget.setLabel("bottom", "Elapsed Time (s)", color=COLORS["text_secondary"])
        self.plot_widget.getAxis("left").setTextPen(COLORS["text_secondary"])
        self.plot_widget.getAxis("bottom").setTextPen(COLORS["text_secondary"])
        self.plot_widget.getAxis("left").setPen(pg.mkPen(color=COLORS["border_highlight"], width=1))
        self.plot_widget.getAxis("bottom").setPen(pg.mkPen(color=COLORS["border_highlight"], width=1))
        
        # Invert Y-axis for ocean depth
        self.plot_widget.getPlotItem().getViewBox().invertY(True)
        self.plot_widget.setYRange(0, 70, padding=0.02)

        # Depth curve with amber gold
        self.curve = self.plot_widget.plot(
            pen=pg.mkPen(color=COLORS["accent_yellow"], width=2.2),
            antialias=True
        )

        surface_line = pg.InfiniteLine(pos=0, angle=0, pen=pg.mkPen(color=COLORS["border_highlight"], width=1.2, style=Qt.DashLine))
        self.plot_widget.addItem(surface_line)

        layout.addWidget(self.plot_widget, 1)

        self.times = deque(maxlen=2000)
        self.depths = deque(maxlen=2000)
        self.start_time = None

    def update_telemetry(self, packet: TelemetryPacket):
        if self.start_time is None:
            self.start_time = packet.timestamp

        t_rel = packet.timestamp - self.start_time
        self.times.append(t_rel)
        self.depths.append(packet.depth)

        if len(self.times) > 1:
            self.curve.setData(np.array(self.times), np.array(self.depths))

    def reset_track(self):
        self.times.clear()
        self.depths.clear()
        self.start_time = None
        self.curve.setData(np.array([]), np.array([]))
