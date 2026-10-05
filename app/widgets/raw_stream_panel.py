"""
Raw Serial Data Stream Monitor Widget with autoscroll, pause, and clear controls.
Neutral, low-saturation terminal styling.
"""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QFrame
)
from app.config import COLORS


class RawStreamPanel(QFrame):
    """
    Panel displaying real-time raw incoming serial / UDP lines.
    Positioned at bottom center with responsive horizontal header.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RawStreamCard")
        self.setFrameShape(QFrame.StyledPanel)

        self.is_paused = False
        self.max_lines = 500

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)

        # Header Row: Title on Left, Controls on Right
        header_row = QHBoxLayout()
        header_row.setSpacing(8)

        bar = QFrame()
        bar.setFixedWidth(3)
        bar.setFixedHeight(12)
        bar.setStyleSheet(f"background-color: {COLORS['accent_yellow']}; border-radius: 1px;")

        title = QLabel("DATA STREAM (RAW)")
        title.setObjectName("CardTitle")
        title.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {COLORS['text_primary']}; letter-spacing: 0.5px;")

        header_row.addWidget(bar)
        header_row.addWidget(title)
        header_row.addStretch()

        self.btn_clear = QPushButton("CLEAR")
        self.btn_clear.setFixedHeight(22)
        self.btn_clear.setCursor(Qt.PointingHandCursor)
        self.btn_clear.setStyleSheet(f"""
            QPushButton {{
                background-color: #F1F5F9;
                border: 1px solid {COLORS['border']};
                border-radius: 3px;
                padding: 2px 10px;
                font-size: 10px;
                font-weight: 600;
                color: {COLORS['text_secondary']};
            }}
            QPushButton:hover {{
                background-color: #E2E8F0;
                color: {COLORS['text_primary']};
            }}
        """)
        self.btn_clear.clicked.connect(self.clear_stream)

        self.btn_pause = QPushButton("PAUSE")
        self.btn_pause.setFixedHeight(22)
        self.btn_pause.setCursor(Qt.PointingHandCursor)
        self.btn_pause.setStyleSheet(f"""
            QPushButton {{
                background-color: #F1F5F9;
                border: 1px solid {COLORS['border']};
                border-radius: 3px;
                padding: 2px 10px;
                font-size: 10px;
                font-weight: 600;
                color: {COLORS['text_secondary']};
            }}
            QPushButton:hover {{
                background-color: #E2E8F0;
                color: {COLORS['text_primary']};
            }}
        """)
        self.btn_pause.clicked.connect(self.toggle_pause)

        header_row.addWidget(self.btn_clear)
        header_row.addWidget(self.btn_pause)
        layout.addLayout(header_row)

        # Terminal text box
        self.text_edit = QPlainTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setMaximumBlockCount(self.max_lines)
        layout.addWidget(self.text_edit, 1)

    def append_raw_line(self, line: str):
        """Append incoming line unless paused."""
        if not self.is_paused:
            self.text_edit.appendPlainText(line)

    def clear_stream(self):
        self.text_edit.clear()

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.btn_pause.setText("RESUME")
            self.btn_pause.setStyleSheet(f"background-color: {COLORS['status_green_bg']}; border: 1px solid {COLORS['status_green_border']}; color: {COLORS['status_green']}; font-weight: 600; border-radius: 3px; padding: 2px 10px;")
        else:
            self.btn_pause.setText("PAUSE")
            self.btn_pause.setStyleSheet(f"background-color: #F1F5F9; border: 1px solid {COLORS['border']}; border-radius: 3px; padding: 2px 10px; font-size: 10px; font-weight: 600; color: {COLORS['text_secondary']};")
