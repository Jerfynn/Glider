"""
Link Status Widget displaying packet counts, data throughput, errors, latency, and uptime.
Restrained monochromatic technical typography.
"""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from app.config import COLORS
from app.core.telemetry_model import SerialStats


class StatusItemRow(QWidget):
    def __init__(self, label: str, init_val: str, color_val: str = COLORS["text_primary"], parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(6)

        self.lbl_label = QLabel(label)
        self.lbl_label.setObjectName("SubtleLabel")
        layout.addWidget(self.lbl_label)

        layout.addStretch()

        self.lbl_val = QLabel(init_val)
        self.lbl_val.setStyleSheet(f"""
            color: {color_val};
            font-size: 12px;
            font-weight: 400;
            font-family: 'Consolas', 'Roboto Mono', 'SF Mono', monospace;
        """)
        layout.addWidget(self.lbl_val)

    def set_value(self, val_text: str, color_override: str = None):
        self.lbl_val.setText(val_text)
        if color_override:
            self.lbl_val.setStyleSheet(f"color: {color_override}; font-size: 12px; font-weight: 400; font-family: Consolas, monospace;")


class SerialStatusPanel(QFrame):
    """
    Panel showing telemetry throughput, packet count, errors, latency, and uptime.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SerialStatusCard")
        self.setFrameShape(QFrame.StyledPanel)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(3)

        # Header Title
        title = QLabel("LINK STATUS")
        title.setObjectName("CardTitle")
        layout.addWidget(title)

        # Key-Value Rows
        self.row_rx_rate = StatusItemRow("RX Rate", "0.00 KB/s", COLORS["text_primary"], self)
        self.row_packets = StatusItemRow("Packets", "0", COLORS["text_primary"], self)
        self.row_errors = StatusItemRow("Errors", "0", COLORS["text_primary"], self)
        self.row_latency = StatusItemRow("Latency", "0 ms", COLORS["text_primary"], self)
        self.row_uptime = StatusItemRow("Uptime", "00:00:00", COLORS["text_primary"], self)

        layout.addWidget(self.row_rx_rate)
        layout.addWidget(self.row_packets)
        layout.addWidget(self.row_errors)
        layout.addWidget(self.row_latency)
        layout.addWidget(self.row_uptime)

    def update_stats(self, stats: SerialStats):
        self.row_rx_rate.set_value(f"{stats.rx_rate_kbps:.2f} KB/s")
        self.row_packets.set_value(f"{stats.packet_count:,}")
        
        err_col = COLORS["status_red"] if stats.error_count > 0 else COLORS["text_primary"]
        self.row_errors.set_value(str(stats.error_count), err_col)

        self.row_latency.set_value(f"{stats.latency_ms:.0f} ms")

        # Format uptime HH:MM:SS
        total_sec = int(stats.uptime_seconds)
        hrs = total_sec // 3600
        mins = (total_sec % 3600) // 60
        secs = total_sec % 60
        self.row_uptime.set_value(f"{hrs:02d}:{mins:02d}:{secs:02d}")

