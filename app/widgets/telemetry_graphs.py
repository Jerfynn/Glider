"""
Real-time Hardware-accelerated Telemetry Graphs using PyQtGraph.
Clean White / Light Theme with high-contrast traces.
"""

from collections import deque
import time
import numpy as np

import pyqtgraph as pg
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QFrame
)

from app.config import COLORS, GRAPH_TIME_WINDOWS


class MiniStripChart(pg.PlotWidget):
    """A clean, styled white-themed strip chart for a single telemetry signal."""

    def __init__(self, title: str, line_color: str, y_min: float = -40, y_max: float = 40, y_ticks: list = None, parent=None):
        super().__init__(parent)
        
        # Background & styling (#FFFFFF)
        self.setBackground(COLORS["bg_card"])
        self.showGrid(x=True, y=True, alpha=0.35)
        self.setMouseEnabled(x=False, y=False)
        self.setMenuEnabled(False)
        self.hideButtons()

        # Title
        self.setTitle(f"<span style='color: {COLORS['text_primary']}; font-weight: 600; font-size: 11px; font-family: Segoe UI, sans-serif;'>{title}</span>")

        # Axes styling
        axis_pen = pg.mkPen(color=COLORS["border_highlight"], width=1)
        self.getAxis("left").setPen(axis_pen)
        self.getAxis("bottom").setPen(axis_pen)
        self.getAxis("left").setTextPen(COLORS["text_secondary"])
        self.getAxis("bottom").setTextPen(COLORS["text_secondary"])
        self.getAxis("left").setStyle(tickFont=pg.QtGui.QFont("Segoe UI", 8))
        self.getAxis("bottom").setStyle(tickFont=pg.QtGui.QFont("Segoe UI", 8))
        
        # Set ranges
        self.setYRange(y_min, y_max, padding=0.02)
        if y_ticks:
            ticks_formatted = [(val, str(val)) for val in y_ticks]
            self.getAxis("left").setTicks([ticks_formatted])
        
        # Plot curve
        self.curve = self.plot(
            pen=pg.mkPen(color=line_color, width=2.0),
            antialias=True
        )

        # Bottom axis formatting (30s, 20s, 10s, 0s)
        self.time_window = 30.0
        self._update_axis_ticks()

    def _update_axis_ticks(self):
        w = int(self.time_window)
        ticks = [(-w, f"{w}s"), (-w * 2 // 3, f"{w*2//3}s"), (-w // 3, f"{w//3}s"), (0, "0s")]
        self.getAxis("bottom").setTicks([ticks])

    def set_time_window(self, seconds: float):
        self.time_window = seconds
        self.setXRange(-seconds, 0, padding=0.0)
        self._update_axis_ticks()

    def update_data(self, times_relative: np.ndarray, values: np.ndarray):
        """Plots times (negative offsets from now) and values."""
        self.curve.setData(times_relative, values)


class TelemetryGraphsPanel(QFrame):
    """
    Bottom Center Telemetry Graphs widget with Roll, Pitch, and Yaw strip charts.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TelemetryGraphsCard")
        self.setFrameShape(QFrame.StyledPanel)

        # Data history buffers
        self.max_points = 4000
        self.times = deque(maxlen=self.max_points)
        self.roll_data = deque(maxlen=self.max_points)
        self.pitch_data = deque(maxlen=self.max_points)
        self.yaw_data = deque(maxlen=self.max_points)

        self.current_window_sec = 30.0

        # UI Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Header bar
        header = QHBoxLayout()
        header.setSpacing(10)

        title = QLabel("TELEMETRY GRAPH")
        title.setObjectName("CardTitle")
        header.addWidget(title)

        header.addStretch()

        # Time Window Selector
        lbl_win = QLabel("Time Window")
        lbl_win.setObjectName("SubtleLabel")
        header.addWidget(lbl_win)

        self.combo_window = QComboBox()
        self.combo_window.setFixedHeight(24)
        for label in GRAPH_TIME_WINDOWS.keys():
            self.combo_window.addItem(label)
        self.combo_window.setCurrentText("30 Seconds")
        self.combo_window.currentTextChanged.connect(self._on_window_changed)
        header.addWidget(self.combo_window)

        # Clear Button
        self.btn_clear = QPushButton("CLEAR")
        self.btn_clear.setFixedHeight(24)
        self.btn_clear.clicked.connect(self.clear_data)
        header.addWidget(self.btn_clear)

        layout.addLayout(header)

        # 3 Charts Layout
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(8)

        self.chart_roll = MiniStripChart("ROLL (°)", COLORS["trace_roll"], -40, 40, [-40, -20, 0, 20, 40], self)
        self.chart_pitch = MiniStripChart("PITCH (°)", COLORS["trace_pitch"], -40, 40, [-40, -20, 0, 20, 40], self)
        self.chart_yaw = MiniStripChart("YAW (°)", COLORS["trace_yaw"], -180, 180, [-180, -90, 0, 90, 180], self)

        charts_layout.addWidget(self.chart_roll)
        charts_layout.addWidget(self.chart_pitch)
        charts_layout.addWidget(self.chart_yaw)

        layout.addLayout(charts_layout)

        # Initial setup
        self._on_window_changed("30 Seconds")

    def _on_window_changed(self, text: str):
        sec = GRAPH_TIME_WINDOWS.get(text, 30)
        self.current_window_sec = float(sec)
        self.chart_roll.set_time_window(self.current_window_sec)
        self.chart_pitch.set_time_window(self.current_window_sec)
        self.chart_yaw.set_time_window(self.current_window_sec)

    def add_telemetry_point(self, t: float, roll: float, pitch: float, yaw: float):
        """Append new telemetry reading and refresh graphs."""
        self.times.append(t)
        self.roll_data.append(roll)
        self.pitch_data.append(pitch)
        self.yaw_data.append(yaw)

        if len(self.times) < 2:
            return

        now = t
        times_arr = np.array(self.times) - now
        cutoff = -self.current_window_sec
        mask = times_arr >= cutoff

        if not np.any(mask):
            return

        rel_t = times_arr[mask]
        r_arr = np.array(self.roll_data)[mask]
        p_arr = np.array(self.pitch_data)[mask]
        y_arr = np.array(self.yaw_data)[mask]

        self.chart_roll.update_data(rel_t, r_arr)
        self.chart_pitch.update_data(rel_t, p_arr)
        self.chart_yaw.update_data(rel_t, y_arr)

    def clear_data(self):
        self.times.clear()
        self.roll_data.clear()
        self.pitch_data.clear()
        self.yaw_data.clear()
        self.chart_roll.update_data(np.array([]), np.array([]))
        self.chart_pitch.update_data(np.array([]), np.array([]))
        self.chart_yaw.update_data(np.array([]), np.array([]))
