"""
Main Application Window assembling all GliderView panels, tabs, and footer.
"""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QTabWidget, QApplication,
    QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox
)
from qtpy.QtGui import QKeyEvent

from app.config import COLORS, APP_NAME, APP_VERSION
from app.style import MAIN_STYLESHEET
from app.core.serial_worker import SerialWorker
from app.core.telemetry_model import TelemetryPacket
from app.core.logger import TelemetryCsvLogger

from app.widgets.header_bar import HeaderBar
from app.widgets.connection_panel import ConnectionPanel
from app.widgets.attitude_indicator import AttitudeIndicatorWidget
from app.widgets.mode_control_panel import VehicleModeControlPanel
from app.widgets.raw_stream_panel import RawStreamPanel
from app.widgets.gl_glider_view import Glider3DViewWidget
from app.widgets.telemetry_metrics import TelemetryMetricsPanel
from app.widgets.map_view import MapViewWidget
from app.widgets.depth_viewer_tab import DepthViewerTabWidget
from app.widgets.depth_control_tab import DepthControlTabWidget
from app.widgets.motion_profile_tab import MotionProfileTabWidget
from app.widgets.analytics_tab import AnalyticsTabWidget
from app.widgets.dive_history_tab import DiveHistoryTabWidget
from app.widgets.settings_tab import SettingsTabWidget


class MainWindow(QMainWindow):
    """
    Main Ground Control Station (GCS) Telemetry Viewer Window.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION} - Underwater Glider Telemetry Viewer")
        self.resize(1360, 820)
        self.setMinimumSize(1100, 680)

        # Apply Global Stylesheet
        self.setStyleSheet(MAIN_STYLESHEET)

        # CSV Telemetry Logger
        self.csv_logger = TelemetryCsvLogger()

        # Serial Worker Thread
        self.serial_worker = SerialWorker(self)

        # Build UI
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        # Central Container
        central_widget = QWidget(self)
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(10, 8, 10, 6)
        root_layout.setSpacing(8)

        # 1. Top Header Bar
        self.header_bar = HeaderBar(self)
        root_layout.addWidget(self.header_bar)

        # 2. Main 3-Column Content Layout
        content_layout = QHBoxLayout()
        content_layout.setSpacing(8)

        # --- LEFT SIDEBAR (Width ~ 260px) ---
        left_column = QVBoxLayout()
        left_column.setSpacing(8)

        # Connection Panel
        self.connection_panel = ConnectionPanel(self)
        self.connection_panel.setFixedWidth(260)
        left_column.addWidget(self.connection_panel)

        # Attitude Indicator Widget
        self.attitude_indicator_widget = AttitudeIndicatorWidget(self)
        self.attitude_indicator_widget.setFixedWidth(260)
        self.attitude_indicator_widget.setFixedHeight(180)
        left_column.addWidget(self.attitude_indicator_widget)

        # Mode Control Panel (Moved to Left Sidebar where Raw Stream was)
        self.mode_control_panel = VehicleModeControlPanel(self)
        self.mode_control_panel.setFixedWidth(260)
        left_column.addWidget(self.mode_control_panel, 1)

        content_layout.addLayout(left_column)

        # --- CENTER MAIN AREA ---
        center_column = QVBoxLayout()
        center_column.setSpacing(8)

        # Flat Modern Tab Bar
        self.tab_widget = QTabWidget(self)

        # Tab 1: 3D VIEW
        self.glider_3d_view = Glider3DViewWidget(self)
        self.tab_widget.addTab(self.glider_3d_view, "3D VIEW")

        # Tab 2: MAP VIEW
        self.map_view = MapViewWidget(self)
        self.tab_widget.addTab(self.map_view, "MAP VIEW")

        # Tab 3: DEPTH CONTROL
        self.depth_control_tab = DepthControlTabWidget(self)
        self.tab_widget.addTab(self.depth_control_tab, "DEPTH CONTROL")

        # Tab 4: CYCLE CONFIG
        self.motion_profile_tab = MotionProfileTabWidget(self)
        self.tab_widget.addTab(self.motion_profile_tab, "CYCLE CONFIG")

        # Tab 5: ANALYTICS (Current Cycle Dive Power & Energy)
        self.analytics_tab = AnalyticsTabWidget(self)
        self.tab_widget.addTab(self.analytics_tab, "ANALYTICS")

        # Tab 6: DIVE HISTORY (Power & Energy Calculations from Cycle 1)
        self.dive_history_tab = DiveHistoryTabWidget(self.analytics_tab.engine, self)
        self.tab_widget.addTab(self.dive_history_tab, "DIVE HISTORY")

        # Tab 7: SETTINGS
        self.settings_tab = SettingsTabWidget(logger=self.csv_logger, parent=self)
        self.tab_widget.addTab(self.settings_tab, "SETTINGS")

        # Background Depth & Dive Cycle Tracker (Headless background tracker)
        self.depth_viewer_tab = DepthViewerTabWidget(parent=None)
        self.depth_viewer_tab.hide()

        center_column.addWidget(self.tab_widget, 1)

        # Bottom Data Stream (RAW) Monitor (Moved here in place of Telemetry Graph)
        self.raw_stream_panel = RawStreamPanel(self)
        self.raw_stream_panel.setFixedHeight(150)
        center_column.addWidget(self.raw_stream_panel, 0)

        content_layout.addLayout(center_column, 1)

        # --- RIGHT SIDEBAR (Width ~ 280px) ---
        right_column = QVBoxLayout()
        right_column.setSpacing(8)

        self.telemetry_metrics_panel = TelemetryMetricsPanel(self)
        self.telemetry_metrics_panel.setFixedWidth(280)
        right_column.addWidget(self.telemetry_metrics_panel, 1)

        content_layout.addLayout(right_column)

        root_layout.addLayout(content_layout, 1)

    def _connect_signals(self):
        """Connect UI components to background serial worker signals."""
        # Connection actions
        self.connection_panel.connect_requested.connect(self._on_start_connection)
        self.connection_panel.disconnect_requested.connect(self._on_stop_connection)
        self.connection_panel.calibrate_requested.connect(self._on_calibrate_vehicle)

        # Command transmission
        self.depth_control_tab.send_depth_requested.connect(self._on_send_depth_command)
        self.motion_profile_tab.send_profile_requested.connect(self._on_send_profile_command)
        self.mode_control_panel.command_requested.connect(self._on_send_raw_command)

        # Tab inter-communication
        self.depth_viewer_tab.cycle_count_changed.connect(self._on_dive_cycle_changed)

        # Worker signals
        self.serial_worker.telemetry_received.connect(self._on_telemetry_received)
        self.serial_worker.raw_line_received.connect(self.raw_stream_panel.append_raw_line)
        self.serial_worker.stats_updated.connect(self._on_stats_updated)
        self.serial_worker.connection_changed.connect(self._on_connection_changed)

    def _on_start_connection(self, mode: str, port: str, baud: int, data_bits: int, parity: str, stop_bits: str, ip: str, udp_port: int, is_sim: bool):
        self.serial_worker.start_connection(
            mode=mode,
            port=port,
            baud=baud,
            data_bits=data_bits,
            parity=parity,
            stop_bits=stop_bits,
            ip=ip,
            udp_port=udp_port,
            is_sim=is_sim
        )

    def _on_stop_connection(self):
        self.serial_worker.stop_connection()
        self.csv_logger.flush()

    def _on_calibrate_vehicle(self):
        """Sends calibration command to vehicle and logs status."""
        success = self.serial_worker.send_command("CALIBRATE\n")
        if success:
            self.raw_stream_panel.append_raw_line("[COMMAND SENT] CALIBRATE (Vehicle Sensor Zeroing)")
        else:
            self.raw_stream_panel.append_raw_line("[COMMAND FAILED] CALIBRATE (Connection Inactive)")

    def _on_dive_cycle_changed(self, count: int):
        """Synchronizes dive count across Header Bar and Analytics."""
        self.header_bar.set_dive_count(count)

    def _on_send_depth_command(self, dive_in: float, hold: float, dive_out: float, cmd: str):
        success = self.serial_worker.send_command(cmd + "\n")
        self.depth_control_tab.add_command_log(dive_in, hold, dive_out, cmd, success)
        if success:
            self.raw_stream_panel.append_raw_line(f"[COMMAND SENT] DEPTH PROFILE: {cmd}")
        else:
            self.raw_stream_panel.append_raw_line(f"[COMMAND FAILED] DEPTH PROFILE: {cmd}")

    def _on_send_profile_command(self, phase: str, params_str: str, cmd: str):
        success = self.serial_worker.send_command(cmd)
        self.motion_profile_tab.add_command_log(phase, params_str, cmd, success)

    def _on_send_raw_command(self, cmd: str):
        """Transmits raw command to connected serial/network port."""
        self.serial_worker.send_command(cmd)

    def _on_send_manual_key_command(self, cmd: str, action_name: str):
        """Transmits manual key command and logs activity."""
        self.serial_worker.send_command(cmd)

    def keyPressEvent(self, event: QKeyEvent):
        """Handles manual vehicle keyboard navigation when MANUAL mode is active."""
        if hasattr(self, 'mode_control_panel') and self.mode_control_panel.current_mode == "MANUAL":
            focused = QApplication.focusWidget()
            if not isinstance(focused, (QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox)):
                key = event.key()
                # W -> Forward
                if key in (Qt.Key_W, Qt.Key_Up):
                    self._on_send_manual_key_command("w", "FORWARD")
                    event.accept()
                    return
                # S -> Reverse
                elif key in (Qt.Key_S, Qt.Key_Down):
                    self._on_send_manual_key_command("s", "REVERSE")
                    event.accept()
                    return
                # Space or X -> Stop
                elif key in (Qt.Key_Space, Qt.Key_X):
                    self._on_send_manual_key_command("x", "STOP")
                    event.accept()
                    return
        super().keyPressEvent(event)

    def _on_connection_changed(self, connected: bool, message: str):
        self.connection_panel.set_connected_state(connected)
        is_receiving = "CONNECTED" in message.upper()
        self.depth_viewer_tab.set_connected_state(connected, is_receiving=is_receiving)
        if connected:
            if self.serial_worker._is_simulated:
                conn_info = f"SIMULATOR ({self.serial_worker.connection_mode})"
            elif self.serial_worker.connection_mode in ("TCP", "UDP"):
                conn_info = f"{self.serial_worker.connection_mode} @ {self.serial_worker.udp_ip}:{self.serial_worker.udp_port}"
            else:
                conn_info = f"{self.serial_worker.port} @ {self.serial_worker.baud_rate}"

            if is_receiving:
                self.header_bar.set_status("CONNECTED", conn_info)
            else:
                self.header_bar.set_status("WAITING", conn_info)
        else:
            self.header_bar.set_status("DISCONNECTED", "")
            self.csv_logger.flush()

    def _on_stats_updated(self, stats):
        self.header_bar.update_message_count(stats.packet_count)
        self.header_bar.set_logging_status(self.csv_logger.is_enabled and stats.packet_count > 0)

    def _on_telemetry_received(self, packet: TelemetryPacket):
        """Dispatches decoded telemetry packet across all visualizers and CSV logger."""
        if not packet.is_valid:
            return

        # 1. Real-Time CSV Telemetry Logging
        self.csv_logger.log_packet(packet)
        self.header_bar.set_logging_status(self.csv_logger.is_enabled)

        # 2. Update 3D Glider Viewport
        self.glider_3d_view.update_telemetry(packet.roll, packet.pitch, packet.yaw)

        # 3. Update Left Attitude Indicator Dial
        self.attitude_indicator_widget.update_telemetry(packet.roll, packet.pitch, packet.yaw)

        # 4. Update Right Telemetry Readout Cards & Battery Warning
        self.telemetry_metrics_panel.update_telemetry(packet)
        self.header_bar.set_battery_status(packet.battery_voltage, packet.battery_current)

        # 5. Update Map / Dive Profile
        self.map_view.update_telemetry(packet)

        # 6. Update Depth Viewer (Cycle Count)
        self.depth_viewer_tab.on_telemetry_received(packet)

        # 7. Update Analytics Dashboard (Dive Power & Energy Analytics)
        self.analytics_tab.update_telemetry(
            packet,
            active_dive_count=self.depth_viewer_tab._cycle_count,
            nose_ml=self.depth_viewer_tab.current_nose_ml,
            tail_l=self.depth_viewer_tab.current_tail_l
        )

        # 8. Update Dive History Table (All Cycles From Cycle 1)
        self.dive_history_tab.update_telemetry(packet)

    def closeEvent(self, event):
        """Clean shutdown of background worker thread and file loggers."""
        self.serial_worker.stop_connection()
        self.csv_logger.close()
        event.accept()
