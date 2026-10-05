"""
Bottom Status Footer Bar Widget for GliderView GCS Interface.
Clean White / Light Theme.
"""

from datetime import datetime
from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import QWidget, QHBoxLayout, QLabel
from app.config import COLORS


class FooterBar(QWidget):
    """
    Bottom application footer bar displaying Logging status, UTC Clock,
    Firmware revision, and message counter.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FooterBar")
        self.setFixedHeight(24)
        self.setStyleSheet(f"""
            QWidget#FooterBar {{
                background-color: {COLORS['bg_card']};
                border-top: 1px solid {COLORS['border']};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 2, 14, 2)
        layout.setSpacing(20)

        # 1. Logging status
        self.lbl_logging = QLabel("Logging: OFF")
        self.lbl_logging.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        layout.addWidget(self.lbl_logging)

        layout.addStretch()

        # 2. Time (UTC)
        self.lbl_time = QLabel("Time (UTC): -- --- ---- --:--:--")
        self.lbl_time.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px; font-weight: 500; font-family: 'Consolas', monospace;")
        layout.addWidget(self.lbl_time)

        layout.addStretch()

        # 3. Firmware revision
        self.lbl_firmware = QLabel("Firmware: --")
        self.lbl_firmware.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        layout.addWidget(self.lbl_firmware)

        # 4. Message counter
        self.lbl_messages = QLabel("Messages: 0")
        self.lbl_messages.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        layout.addWidget(self.lbl_messages)

        # Clock timer update (1 Hz)
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)
        self._update_clock()

    def _update_clock(self):
        utc_now = datetime.utcnow()
        formatted = utc_now.strftime("%d  %b  %Y  %H:%M:%S")
        self.lbl_time.setText(f"Time (UTC): {formatted}")

    def update_message_count(self, count: int):
        self.lbl_messages.setText(f"Messages: {count}")
