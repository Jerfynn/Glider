"""
Depth Control and Dive Profile Command Transmission Tab Widget.
Allows configuring and transmitting Dive In (m), Hold (s), and Dive Out (m) values.
Formats data payload as: Dive In, Hold, Dive Out (e.g. 0.5,0.2,0.5).
Clean White / Light Theme with industrial amber accents.
"""

from datetime import datetime
from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QColor
from qtpy.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QDoubleSpinBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
)
from app.config import COLORS


class DepthControlTabWidget(QFrame):
    """
    Dedicated Depth Control Tab.
    Features:
      - 3 Input Options: Dive In (m), Hold (s), Dive Out (m)
      - Transmit command button sending: Dive In,Hold,Dive Out (e.g. 0.5,0.2,0.5)
      - Real-time command payload preview
      - Command transmission log history table
    """

    send_depth_requested = Signal(float, float, float, str)  # (dive_in, hold, dive_out, formatted_cmd)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DepthControlCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        # 1. Section Header: DEPTH CONTROL
        header_row = QHBoxLayout()
        header_row.setSpacing(8)

        bar = QFrame()
        bar.setFixedWidth(4)
        bar.setFixedHeight(16)
        bar.setStyleSheet(f"background-color: {COLORS['accent_yellow']}; border-radius: 2px;")

        title_label = QLabel("DEPTH CONTROL")
        title_label.setObjectName("CardTitle")
        title_label.setStyleSheet(f"font-size: 14px; font-weight: 800; color: {COLORS['text_primary']}; letter-spacing: 0.5px;")

        header_row.addWidget(bar)
        header_row.addWidget(title_label)
        header_row.addStretch()
        layout.addLayout(header_row)

        # 2. Main Parameters Card
        card_control = QFrame()
        card_control.setStyleSheet(f"""
            QFrame#ControlPanelBox {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
        """)
        card_control.setObjectName("ControlPanelBox")

        control_layout = QVBoxLayout(card_control)
        control_layout.setContentsMargins(20, 18, 20, 18)
        control_layout.setSpacing(14)

        # Parameter Input Grid (3 Options)
        input_grid = QGridLayout()
        input_grid.setHorizontalSpacing(16)
        input_grid.setVerticalSpacing(8)

        # Option 1: Dive In (m)
        lbl_dive_in = QLabel("Dive In (m):")
        lbl_dive_in.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {COLORS['text_primary']};")

        self.spin_dive_in = QDoubleSpinBox()
        self.spin_dive_in.setRange(0.0, 500.0)
        self.spin_dive_in.setValue(0.5)
        self.spin_dive_in.setSingleStep(0.1)
        self.spin_dive_in.setDecimals(2)
        self.spin_dive_in.setSuffix(" m")
        self.spin_dive_in.setFixedHeight(36)
        self._apply_spinbox_style(self.spin_dive_in)
        self.spin_dive_in.valueChanged.connect(self._update_preview)

        # Option 2: Hold (s)
        lbl_hold = QLabel("Hold (s):")
        lbl_hold.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {COLORS['text_primary']};")

        self.spin_hold = QDoubleSpinBox()
        self.spin_hold.setRange(0.0, 3600.0)
        self.spin_hold.setValue(0.2)
        self.spin_hold.setSingleStep(0.1)
        self.spin_hold.setDecimals(2)
        self.spin_hold.setSuffix(" s")
        self.spin_hold.setFixedHeight(36)
        self._apply_spinbox_style(self.spin_hold)
        self.spin_hold.valueChanged.connect(self._update_preview)

        # Option 3: Dive Out (m)
        lbl_dive_out = QLabel("Dive Out (m):")
        lbl_dive_out.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {COLORS['text_primary']};")

        self.spin_dive_out = QDoubleSpinBox()
        self.spin_dive_out.setRange(0.0, 500.0)
        self.spin_dive_out.setValue(0.5)
        self.spin_dive_out.setSingleStep(0.1)
        self.spin_dive_out.setDecimals(2)
        self.spin_dive_out.setSuffix(" m")
        self.spin_dive_out.setFixedHeight(36)
        self._apply_spinbox_style(self.spin_dive_out)
        self.spin_dive_out.valueChanged.connect(self._update_preview)

        # Add to Grid: Col 0 = Dive In, Col 1 = Hold, Col 2 = Dive Out
        input_grid.addWidget(lbl_dive_in, 0, 0)
        input_grid.addWidget(self.spin_dive_in, 1, 0)

        input_grid.addWidget(lbl_hold, 0, 1)
        input_grid.addWidget(self.spin_hold, 1, 1)

        input_grid.addWidget(lbl_dive_out, 0, 2)
        input_grid.addWidget(self.spin_dive_out, 1, 2)

        control_layout.addLayout(input_grid)

        # Transmission Row: Live Payload Preview + Send Button
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.lbl_preview = QLabel("TRANSMIT PAYLOAD: 0.5,0.2,0.5")
        self.lbl_preview.setStyleSheet(f"""
            QLabel {{
                background-color: #F1F5F9;
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 6px 12px;
                color: {COLORS['text_primary']};
                font-family: 'Consolas', monospace;
                font-size: 13px;
                font-weight: 700;
            }}
        """)

        self.btn_send = QPushButton("  SEND DEPTH COMMAND  ")
        self.btn_send.setObjectName("PrimaryButton")
        self.btn_send.setFixedHeight(36)
        self.btn_send.setStyleSheet(f"""
            QPushButton#PrimaryButton {{
                background-color: {COLORS['accent_yellow']};
                border: 1px solid {COLORS['accent_yellow_hover']};
                border-radius: 4px;
                color: #FFFFFF;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.5px;
                padding: 0 20px;
            }}
            QPushButton#PrimaryButton:hover {{
                background-color: {COLORS['accent_yellow_hover']};
            }}
            QPushButton#PrimaryButton:pressed {{
                background-color: {COLORS['accent_yellow_pressed']};
            }}
        """)
        self.btn_send.clicked.connect(self._on_send_clicked)

        btn_row.addWidget(self.lbl_preview, 1)
        btn_row.addWidget(self.btn_send, 0)

        control_layout.addLayout(btn_row)
        layout.addWidget(card_control)

        # 3. Transmission History Table
        history_card = QFrame()
        history_card.setStyleSheet(f"""
            QFrame#HistoryBox {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
        """)
        history_card.setObjectName("HistoryBox")

        history_layout = QVBoxLayout(history_card)
        history_layout.setContentsMargins(16, 14, 16, 14)
        history_layout.setSpacing(10)

        lbl_hist_title = QLabel("COMMAND TRANSMISSION LOG")
        lbl_hist_title.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {COLORS['accent_yellow']}; letter-spacing: 0.5px;")
        history_layout.addWidget(lbl_hist_title)

        self.table_history = QTableWidget()
        self.table_history.setColumnCount(6)
        self.table_history.setHorizontalHeaderLabels([
            "Time", "Dive In (m)", "Hold (s)", "Dive Out (m)", "Transmitted Payload", "Status"
        ])
        self.table_history.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_history.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_history.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_history.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_history.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table_history.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table_history.verticalHeader().setVisible(False)
        self.table_history.setAlternatingRowColors(True)
        self.table_history.setStyleSheet(f"""
            QTableWidget {{
                background-color: #FFFFFF;
                alternate-background-color: #F8FAFC;
                color: #0F172A;
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                gridline-color: {COLORS['border_subtle']};
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }}
            QTableWidget::item {{
                color: #0F172A;
                padding: 4px 6px;
            }}
            QHeaderView::section {{
                background-color: #F1F5F9;
                color: #0F172A;
                padding: 4px 8px;
                border: none;
                border-bottom: 1px solid {COLORS['border']};
                font-weight: 700;
                font-size: 11px;
            }}
        """)

        history_layout.addWidget(self.table_history)
        layout.addWidget(history_card, 1)

        self._update_preview()

    def _apply_spinbox_style(self, spinbox: QDoubleSpinBox):
        spinbox.setStyleSheet(f"""
            QDoubleSpinBox {{
                background-color: #FFFFFF;
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 4px 10px;
                color: {COLORS['text_primary']};
                font-family: 'Consolas', monospace;
                font-size: 14px;
                font-weight: 700;
            }}
            QDoubleSpinBox:focus {{
                border-color: {COLORS['accent_yellow']};
            }}
        """)

    def _format_val(self, val: float) -> str:
        """Formats float cleanly: e.g. 0.5 instead of 0.500000."""
        s = f"{val:.2f}"
        if s.endswith(".00"):
            return f"{int(val)}"
        elif s.endswith("0"):
            return s[:-1]
        return s

    def _get_payload_string(self) -> str:
        d_in = self._format_val(self.spin_dive_in.value())
        hold = self._format_val(self.spin_hold.value())
        d_out = self._format_val(self.spin_dive_out.value())
        return f"{d_in},{hold},{d_out}"

    def _update_preview(self):
        payload = self._get_payload_string()
        self.lbl_preview.setText(f"TRANSMIT PAYLOAD: {payload}")

    def _on_send_clicked(self):
        d_in = self.spin_dive_in.value()
        hold = self.spin_hold.value()
        d_out = self.spin_dive_out.value()
        payload = self._get_payload_string()
        self.send_depth_requested.emit(d_in, hold, d_out, payload)

    def add_command_log(self, dive_in: float, hold: float, dive_out: float, command_str: str, success: bool = True):
        """Appends a transmitted command to history table with crystal-clear contrast."""
        row = self.table_history.rowCount()
        self.table_history.insertRow(row)

        time_str = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        item_time = QTableWidgetItem(time_str)
        item_time.setTextAlignment(Qt.AlignCenter)
        item_time.setForeground(QColor("#0F172A"))

        item_in = QTableWidgetItem(f"{dive_in:g} m")
        item_in.setTextAlignment(Qt.AlignCenter)
        item_in.setForeground(QColor("#0F172A"))

        item_hold = QTableWidgetItem(f"{hold:g} s")
        item_hold.setTextAlignment(Qt.AlignCenter)
        item_hold.setForeground(QColor("#0F172A"))

        item_out = QTableWidgetItem(f"{dive_out:g} m")
        item_out.setTextAlignment(Qt.AlignCenter)
        item_out.setForeground(QColor("#0F172A"))

        item_cmd = QTableWidgetItem(command_str)
        item_cmd.setForeground(QColor("#0F172A"))

        status_text = "TRANSMITTED" if success else "FAILED"
        item_status = QTableWidgetItem(status_text)
        item_status.setTextAlignment(Qt.AlignCenter)
        if success:
            item_status.setForeground(QColor("#16A34A"))
        else:
            item_status.setForeground(QColor("#DC2626"))

        self.table_history.setItem(row, 0, item_time)
        self.table_history.setItem(row, 1, item_in)
        self.table_history.setItem(row, 2, item_hold)
        self.table_history.setItem(row, 3, item_out)
        self.table_history.setItem(row, 4, item_cmd)
        self.table_history.setItem(row, 5, item_status)
        self.table_history.scrollToBottom()
