"""
Top Header Bar Widget for GliderView GCS Interface.
Integrates System Telemetry Status, Live UTC Clock, Logging Status,
Packet Counter, Dive Cycles, Battery Monitor, and Connection States.
Clean White / Light Theme with high-contrast status badges.
"""

from datetime import datetime
from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from app.config import COLORS, APP_NAME, APP_VERSION, APP_SUBTITLE
from app.utils.icons import get_icon


class HeaderBar(QWidget):
    """
    Top application bar containing branding, live UTC clock, logging status,
    packet message counter, dive cycles, battery monitor, and connection status.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HeaderBar")
        self.setFixedHeight(54)
        self.setStyleSheet(f"""
            QWidget#HeaderBar {{
                background-color: {COLORS['bg_card']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(10)

        # 1. Left Logo & Titles
        left_layout = QHBoxLayout()
        left_layout.setSpacing(10)

        # SVG Vector Logo
        self.lbl_logo = QLabel()
        self.lbl_logo.setFixedSize(28, 28)
        self.lbl_logo.setAlignment(Qt.AlignCenter)
        self.lbl_logo.setStyleSheet("border: none; background: transparent;")
        logo_icon = get_icon("logo_glider", size=22)
        self.lbl_logo.setPixmap(logo_icon.pixmap(22, 22))
        left_layout.addWidget(self.lbl_logo)

        # Title block
        title_box = QVBoxLayout()
        title_box.setSpacing(1)

        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        
        self.lbl_title = QLabel(APP_NAME)
        self.lbl_title.setStyleSheet(f"border: none; background: transparent; font-size: 14px; font-weight: 800; color: {COLORS['text_primary']}; letter-spacing: 0.2px;")

        self.lbl_version = QLabel(APP_VERSION)
        self.lbl_version.setStyleSheet(f"border: none; background: transparent; font-size: 10px; font-weight: 700; color: {COLORS['accent_yellow']};")

        title_row.addWidget(self.lbl_title)
        title_row.addWidget(self.lbl_version)
        title_row.addStretch()

        self.lbl_subtitle = QLabel(APP_SUBTITLE)
        self.lbl_subtitle.setStyleSheet(f"border: none; background: transparent; font-size: 10px; color: {COLORS['text_secondary']};")

        title_box.addLayout(title_row)
        title_box.addWidget(self.lbl_subtitle)
        left_layout.addLayout(title_box)

        layout.addLayout(left_layout)
        layout.addStretch(1)

        # 2. Right Status Indicators & System Information
        right_layout = QHBoxLayout()
        right_layout.setSpacing(6)

        # A. Logging Pill
        self.logging_pill = self._create_pill()
        lay_log = QHBoxLayout(self.logging_pill)
        lay_log.setContentsMargins(8, 0, 8, 0)
        lay_log.setSpacing(4)
        lbl_log_tag = QLabel("LOGGING:")
        lbl_log_tag.setStyleSheet(f"border: none; background: transparent; color: {COLORS['text_secondary']}; font-size: 10px; font-weight: 700;")
        self.lbl_logging = QLabel("OFF")
        self.lbl_logging.setStyleSheet(f"border: none; background: transparent; color: {COLORS['text_muted']}; font-size: 10px; font-weight: 700; font-family: 'Consolas', monospace;")
        lay_log.addWidget(lbl_log_tag)
        lay_log.addWidget(self.lbl_logging)
        right_layout.addWidget(self.logging_pill)

        # B. UTC Time Pill
        self.time_pill = self._create_pill()
        lay_time = QHBoxLayout(self.time_pill)
        lay_time.setContentsMargins(8, 0, 8, 0)
        lay_time.setSpacing(4)
        lbl_utc_tag = QLabel("UTC:")
        lbl_utc_tag.setStyleSheet(f"border: none; background: transparent; color: {COLORS['text_secondary']}; font-size: 10px; font-weight: 700;")
        self.lbl_time = QLabel("--:--:--")
        self.lbl_time.setStyleSheet(f"border: none; background: transparent; color: {COLORS['text_primary']}; font-size: 11px; font-weight: 600; font-family: 'Consolas', monospace;")
        lay_time.addWidget(lbl_utc_tag)
        lay_time.addWidget(self.lbl_time)
        right_layout.addWidget(self.time_pill)

        # C. Message Counter Pill
        self.msg_pill = self._create_pill()
        lay_msg = QHBoxLayout(self.msg_pill)
        lay_msg.setContentsMargins(8, 0, 8, 0)
        lay_msg.setSpacing(4)
        lbl_msg_tag = QLabel("MSGS:")
        lbl_msg_tag.setStyleSheet(f"border: none; background: transparent; color: {COLORS['text_secondary']}; font-size: 10px; font-weight: 700;")
        self.lbl_messages = QLabel("0")
        self.lbl_messages.setStyleSheet(f"border: none; background: transparent; color: {COLORS['text_primary']}; font-size: 11px; font-weight: 700; font-family: 'Consolas', monospace;")
        lay_msg.addWidget(lbl_msg_tag)
        lay_msg.addWidget(self.lbl_messages)
        right_layout.addWidget(self.msg_pill)

        # D. Dive Cycles Pill: DIVES: 0
        self.dive_pill = self._create_pill()
        dive_layout = QHBoxLayout(self.dive_pill)
        dive_layout.setContentsMargins(8, 0, 8, 0)
        dive_layout.setSpacing(4)
        lbl_dive_tag = QLabel("DIVES:")
        lbl_dive_tag.setStyleSheet(f"border: none; background: transparent; color: {COLORS['text_secondary']}; font-size: 10px; font-weight: 700;")
        self.lbl_dive_val = QLabel("0")
        self.lbl_dive_val.setStyleSheet(f"border: none; background: transparent; color: {COLORS['accent_yellow']}; font-size: 11px; font-weight: 800; font-family: 'Consolas', monospace;")
        dive_layout.addWidget(lbl_dive_tag)
        dive_layout.addWidget(self.lbl_dive_val)
        right_layout.addWidget(self.dive_pill)

        # E. Battery Pill with Low Battery Warning
        self.battery_pill = self._create_pill()
        battery_layout = QHBoxLayout(self.battery_pill)
        battery_layout.setContentsMargins(8, 0, 8, 0)
        battery_layout.setSpacing(4)
        self.battery_icon_lbl = QLabel("⚡")
        self.battery_icon_lbl.setStyleSheet("font-size: 11px;")
        self.battery_text = QLabel("BATTERY: -- V")
        self.battery_text.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 11px; font-weight: 600; font-family: 'Consolas', monospace;")
        battery_layout.addWidget(self.battery_icon_lbl)
        battery_layout.addWidget(self.battery_text)
        right_layout.addWidget(self.battery_pill)

        # F. Status Pill: ● DISCONNECTED / ● CONNECTED
        self.status_pill = QFrame()
        self.status_pill.setObjectName("StatusPill")
        self.status_pill.setFixedHeight(26)
        pill_layout = QHBoxLayout(self.status_pill)
        pill_layout.setContentsMargins(10, 0, 10, 0)
        pill_layout.setSpacing(6)
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("border: none; background: transparent; font-size: 9px;")
        self.status_text = QLabel("DISCONNECTED")
        self.status_text.setStyleSheet("border: none; background: transparent; font-size: 11px; font-weight: 600; letter-spacing: 0.4px;")
        pill_layout.addWidget(self.status_dot)
        pill_layout.addWidget(self.status_text)
        right_layout.addWidget(self.status_pill)

        # G. Port Info Pill: COM10 @ 115200 ⌵
        self.port_pill = self._create_pill()
        port_layout = QHBoxLayout(self.port_pill)
        port_layout.setContentsMargins(10, 0, 8, 0)
        port_layout.setSpacing(6)
        self.lbl_port_info = QLabel("NO CONNECTION")
        self.lbl_port_info.setStyleSheet(f"border: none; background: transparent; color: {COLORS['text_primary']}; font-size: 11px; font-weight: 500; font-family: 'Consolas', monospace;")
        self.lbl_port_arrow = QLabel()
        self.lbl_port_arrow.setStyleSheet("border: none; background: transparent;")
        arrow_icon = get_icon("chevron_down", color=COLORS["text_secondary"], size=10)
        self.lbl_port_arrow.setPixmap(arrow_icon.pixmap(10, 10))
        port_layout.addWidget(self.lbl_port_info)
        port_layout.addWidget(self.lbl_port_arrow)
        right_layout.addWidget(self.port_pill)

        layout.addLayout(right_layout)

        # Live UTC Clock Timer (1 Hz)
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)
        self._update_clock()

        # Initial state
        self.set_connected(False)

    def _create_pill(self) -> QFrame:
        pill = QFrame()
        pill.setFixedHeight(26)
        pill.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 3px;
            }}
            QFrame QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        return pill

    def _update_clock(self):
        utc_now = datetime.utcnow()
        formatted = utc_now.strftime("%d %b %Y %H:%M:%S")
        self.lbl_time.setText(formatted)

    def update_message_count(self, count: int):
        self.lbl_messages.setText(str(count))

    def set_logging_status(self, is_logging: bool, filename: str = ""):
        if is_logging:
            self.lbl_logging.setText("ACTIVE")
            self.lbl_logging.setStyleSheet(f"border: none; background: transparent; color: {COLORS['status_green']}; font-size: 10px; font-weight: 800; font-family: 'Consolas', monospace;")
        else:
            self.lbl_logging.setText("OFF")
            self.lbl_logging.setStyleSheet(f"border: none; background: transparent; color: {COLORS['text_muted']}; font-size: 10px; font-weight: 700; font-family: 'Consolas', monospace;")

    def set_dive_count(self, count: int):
        """Updates the top bar dive counter badge."""
        self.lbl_dive_val.setText(str(count))

    def set_battery_status(self, voltage: float, current: float = 0.0):
        """
        Updates the header battery readout and applies low-battery warning styling.
        Threshold:
        - < 22.0 V: Low Battery Warning / Critical (Red alert style)
        - >= 22.0 V: Normal Operating Voltage
        """
        if voltage <= 0:
            self.battery_text.setText("BATTERY: -- V")
            self.battery_pill.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['bg_card']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 3px;
                }}
            """)
            self.battery_text.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 11px; font-weight: 600; font-family: 'Consolas', monospace;")
            return

        if voltage < 22.0:
            # Low Battery Alert (< 22.0 V)
            self.battery_pill.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['status_red_bg']};
                    border: 1px solid {COLORS['status_red_border']};
                    border-radius: 3px;
                }}
            """)
            self.battery_text.setText(f"LOW BATT: {voltage:.2f}V ⚠️")
            self.battery_text.setStyleSheet(f"color: {COLORS['status_red']}; font-size: 11px; font-weight: 800; font-family: 'Consolas', monospace;")
        else:
            # Normal Battery State (>= 22.0 V)
            self.battery_pill.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['bg_card']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 3px;
                }}
            """)
            self.battery_text.setText(f"BATTERY: {voltage:.2f}V")
            self.battery_text.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 11px; font-weight: 600; font-family: 'Consolas', monospace;")

    def set_status(self, state: str, port_info: str = ""):
        """
        Updates the connection status pill with three states:
        - "CONNECTED": Green pill with active link
        - "WAITING" / "LISTENING": Amber pill waiting for telemetry data
        - "DISCONNECTED": Red pill when disconnected
        """
        state_upper = state.upper()
        if state_upper in ("CONNECTED", "ONLINE", "ACTIVE"):
            self.status_pill.setStyleSheet(f"""
                QFrame#StatusPill {{
                    background-color: {COLORS['status_green_bg']};
                    border: 1px solid {COLORS['status_green_border']};
                    border-radius: 3px;
                }}
                QFrame#StatusPill QLabel {{
                    border: none;
                    background: transparent;
                }}
            """)
            self.status_dot.setStyleSheet(f"border: none; background: transparent; color: {COLORS['status_green']}; font-size: 9px;")
            self.status_text.setText("CONNECTED")
            self.status_text.setStyleSheet(f"border: none; background: transparent; color: {COLORS['status_green']}; font-size: 11px; font-weight: 700; letter-spacing: 0.4px;")
            if port_info:
                self.lbl_port_info.setText(port_info)
        elif state_upper in ("WAITING", "LISTENING", "CONNECTING", "NO_DATA"):
            self.status_pill.setStyleSheet(f"""
                QFrame#StatusPill {{
                    background-color: {COLORS['status_amber_bg']};
                    border: 1px solid {COLORS['status_amber_border']};
                    border-radius: 3px;
                }}
                QFrame#StatusPill QLabel {{
                    border: none;
                    background: transparent;
                }}
            """)
            self.status_dot.setStyleSheet(f"border: none; background: transparent; color: {COLORS['status_amber']}; font-size: 9px;")
            self.status_text.setText("WAITING FOR DATA")
            self.status_text.setStyleSheet(f"border: none; background: transparent; color: {COLORS['status_amber']}; font-size: 11px; font-weight: 700; letter-spacing: 0.4px;")
            if port_info:
                self.lbl_port_info.setText(port_info)
        else:
            self.status_pill.setStyleSheet(f"""
                QFrame#StatusPill {{
                    background-color: {COLORS['status_red_bg']};
                    border: 1px solid {COLORS['status_red_border']};
                    border-radius: 3px;
                }}
                QFrame#StatusPill QLabel {{
                    border: none;
                    background: transparent;
                }}
            """)
            self.status_dot.setStyleSheet(f"border: none; background: transparent; color: {COLORS['status_red']}; font-size: 9px;")
            self.status_text.setText("DISCONNECTED")
            self.status_text.setStyleSheet(f"border: none; background: transparent; color: {COLORS['status_red']}; font-size: 11px; font-weight: 700; letter-spacing: 0.4px;")
            self.lbl_port_info.setText("NO CONNECTION")

    def set_connected(self, connected: bool, port_info: str = "COM10 @ 115200"):
        if connected:
            self.set_status("CONNECTED", port_info)
        else:
            self.set_status("DISCONNECTED", port_info)
            self.set_battery_status(0.0)
