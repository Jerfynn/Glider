"""
Motion / Cycle Profile Configuration Tab Widget.
Allows setting and transmitting Reverse and Forward cycle parameters:
- Reverse: Acceleration (s), Hold (s), Deceleration (s)
- Forward: Acceleration (s), Hold (s), Deceleration (s)
Clean White / Light Theme matching GCS design system.
"""

from datetime import datetime
from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QColor, QFont
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QDoubleSpinBox,
    QPushButton, QFrame, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox
)
from app.config import COLORS


class MotionProfileTabWidget(QFrame):
    """
    Dedicated Cycle / Motion Profile Configuration tab.
    Allows configuring acceleration, hold, and deceleration durations for Reverse and Forward phases,
    calculates total cycle time, and transmits profile commands to Teensy via Gateway.
    """

    send_profile_requested = Signal(str, str, str)  # (phase, params_str, formatted_cmd)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MotionProfileCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        # 1. Section Header
        header_row = QHBoxLayout()
        header_row.setSpacing(8)

        bar = QFrame()
        bar.setFixedWidth(3)
        bar.setFixedHeight(14)
        bar.setStyleSheet(f"background-color: {COLORS['accent_yellow']}; border-radius: 1px;")

        title_label = QLabel("CYCLE & MOTION PROFILE CONFIGURATION")
        title_label.setObjectName("CardTitle")

        header_row.addWidget(bar)
        header_row.addWidget(title_label)
        header_row.addStretch()
        layout.addLayout(header_row)

        # 2. Main Parameters Card (2 Columns: REVERSE and FORWARD)
        card_params = QFrame()
        card_params.setStyleSheet(f"""
            QFrame#ParamsBox {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
        """)
        card_params.setObjectName("ParamsBox")

        params_main_layout = QVBoxLayout(card_params)
        params_main_layout.setContentsMargins(18, 16, 18, 16)
        params_main_layout.setSpacing(14)

        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(16)

        # --- LEFT PANEL: REVERSE ---
        rev_box = QFrame()
        rev_box.setStyleSheet(f"""
            QFrame#SubBox {{
                background-color: #FFFFFF;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
        """)
        rev_box.setObjectName("SubBox")
        rev_layout = QVBoxLayout(rev_box)
        rev_layout.setContentsMargins(14, 12, 14, 12)
        rev_layout.setSpacing(10)

        rev_title_row = QHBoxLayout()
        rev_badge = QLabel("REVERSE")
        rev_badge.setStyleSheet(f"""
            background-color: #FEF3C7;
            color: #92400E;
            font-size: 11px;
            font-weight: 800;
            padding: 2px 8px;
            border-radius: 4px;
            border: 1px solid #FDE68A;
        """)
        rev_sub = QLabel("(Climb / Pitch Up Phase)")
        rev_sub.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        rev_title_row.addWidget(rev_badge)
        rev_title_row.addWidget(rev_sub)
        rev_title_row.addStretch()
        rev_layout.addLayout(rev_title_row)

        grid_rev = QGridLayout()
        grid_rev.setHorizontalSpacing(10)
        grid_rev.setVerticalSpacing(8)

        lbl_r_acc = QLabel("Acceleration:")
        lbl_r_acc.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {COLORS['text_secondary']};")
        self.spin_r_acc = self._create_spinbox(value=19.2)

        lbl_r_hold = QLabel("Hold:")
        lbl_r_hold.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {COLORS['text_secondary']};")
        self.spin_r_hold = self._create_spinbox(value=15.0)

        lbl_r_dec = QLabel("Deceleration:")
        lbl_r_dec.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {COLORS['text_secondary']};")
        self.spin_r_dec = self._create_spinbox(value=24.3)

        lbl_r_stable = QLabel("Stable Duration:")
        lbl_r_stable.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {COLORS['text_secondary']};")
        self.spin_r_stable = self._create_spinbox(value=10.0)

        grid_rev.addWidget(lbl_r_acc, 0, 0)
        grid_rev.addWidget(self.spin_r_acc, 0, 1)
        grid_rev.addWidget(lbl_r_hold, 1, 0)
        grid_rev.addWidget(self.spin_r_hold, 1, 1)
        grid_rev.addWidget(lbl_r_dec, 2, 0)
        grid_rev.addWidget(self.spin_r_dec, 2, 1)
        grid_rev.addWidget(lbl_r_stable, 3, 0)
        grid_rev.addWidget(self.spin_r_stable, 3, 1)

        rev_layout.addLayout(grid_rev)

        # Send Reverse Button
        self.btn_send_rev = QPushButton("  SEND REVERSE  ")
        self.btn_send_rev.setFixedHeight(34)
        self.btn_send_rev.setCursor(Qt.PointingHandCursor)
        self.btn_send_rev.setStyleSheet(f"""
            QPushButton {{
                background-color: #D97706;
                border: 1px solid #B45309;
                border-radius: 4px;
                color: #FFFFFF;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.5px;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background-color: #B45309;
            }}
            QPushButton:pressed {{
                background-color: #92400E;
            }}
        """)
        self.btn_send_rev.clicked.connect(self._on_send_reverse_clicked)
        rev_layout.addWidget(self.btn_send_rev)

        columns_layout.addWidget(rev_box, 1)

        # --- RIGHT PANEL: FORWARD ---
        fwd_box = QFrame()
        fwd_box.setStyleSheet(f"""
            QFrame#SubBox {{
                background-color: #FFFFFF;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
        """)
        fwd_box.setObjectName("SubBox")
        fwd_layout = QVBoxLayout(fwd_box)
        fwd_layout.setContentsMargins(14, 12, 14, 12)
        fwd_layout.setSpacing(10)

        fwd_title_row = QHBoxLayout()
        fwd_badge = QLabel("FORWARD")
        fwd_badge.setStyleSheet(f"""
            background-color: #E0F2FE;
            color: #0369A1;
            font-size: 11px;
            font-weight: 800;
            padding: 2px 8px;
            border-radius: 4px;
            border: 1px solid #BAE6FD;
        """)
        fwd_sub = QLabel("(Dive / Pitch Down Phase)")
        fwd_sub.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        fwd_title_row.addWidget(fwd_badge)
        fwd_title_row.addWidget(fwd_sub)
        fwd_title_row.addStretch()
        fwd_layout.addLayout(fwd_title_row)

        grid_fwd = QGridLayout()
        grid_fwd.setHorizontalSpacing(10)
        grid_fwd.setVerticalSpacing(8)

        lbl_f_acc = QLabel("Acceleration:")
        lbl_f_acc.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {COLORS['text_secondary']};")
        self.spin_f_acc = self._create_spinbox(value=19.2)

        lbl_f_hold = QLabel("Hold:")
        lbl_f_hold.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {COLORS['text_secondary']};")
        self.spin_f_hold = self._create_spinbox(value=15.0)

        lbl_f_dec = QLabel("Deceleration:")
        lbl_f_dec.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {COLORS['text_secondary']};")
        self.spin_f_dec = self._create_spinbox(value=24.3)

        lbl_f_stable = QLabel("Stable Duration:")
        lbl_f_stable.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {COLORS['text_secondary']};")
        self.spin_f_stable = self._create_spinbox(value=10.0)

        grid_fwd.addWidget(lbl_f_acc, 0, 0)
        grid_fwd.addWidget(self.spin_f_acc, 0, 1)
        grid_fwd.addWidget(lbl_f_hold, 1, 0)
        grid_fwd.addWidget(self.spin_f_hold, 1, 1)
        grid_fwd.addWidget(lbl_f_dec, 2, 0)
        grid_fwd.addWidget(self.spin_f_dec, 2, 1)
        grid_fwd.addWidget(lbl_f_stable, 3, 0)
        grid_fwd.addWidget(self.spin_f_stable, 3, 1)

        fwd_layout.addLayout(grid_fwd)

        # Send Forward Button
        self.btn_send_fwd = QPushButton("  SEND FORWARD  ")
        self.btn_send_fwd.setFixedHeight(34)
        self.btn_send_fwd.setCursor(Qt.PointingHandCursor)
        self.btn_send_fwd.setStyleSheet(f"""
            QPushButton {{
                background-color: #0284C7;
                border: 1px solid #0369A1;
                border-radius: 4px;
                color: #FFFFFF;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.5px;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background-color: #0369A1;
            }}
            QPushButton:pressed {{
                background-color: #075985;
            }}
        """)
        self.btn_send_fwd.clicked.connect(self._on_send_forward_clicked)
        fwd_layout.addWidget(self.btn_send_fwd)

        columns_layout.addWidget(fwd_box, 1)

        params_main_layout.addLayout(columns_layout)
        layout.addWidget(card_params)

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
        history_layout.setContentsMargins(14, 12, 14, 12)
        history_layout.setSpacing(8)

        lbl_hist_title = QLabel("PROFILE TRANSMISSION LOG")
        lbl_hist_title.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {COLORS['accent_yellow']}; letter-spacing: 0.5px;")
        history_layout.addWidget(lbl_hist_title)

        self.table_history = QTableWidget()
        self.table_history.setColumnCount(5)
        self.table_history.setHorizontalHeaderLabels(["Time", "Phase", "Parameters (Acc / Hold / Dec / Stable)", "Transmitted Command", "Status"])
        self.table_history.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_history.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_history.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_history.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table_history.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
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

    def _create_spinbox(self, value: float) -> QDoubleSpinBox:
        sp = QDoubleSpinBox()
        sp.setRange(0.0, 999.0)
        sp.setValue(value)
        sp.setSingleStep(0.5)
        sp.setDecimals(1)
        sp.setSuffix(" s")
        sp.setFixedHeight(32)
        sp.setStyleSheet(f"""
            QDoubleSpinBox {{
                background-color: #FFFFFF;
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 4px 8px;
                color: {COLORS['text_primary']};
                font-family: 'Consolas', monospace;
                font-size: 13px;
                font-weight: 700;
            }}
            QDoubleSpinBox:focus {{
                border-color: {COLORS['accent_yellow']};
            }}
        """)
        return sp

    def _on_send_reverse_clicked(self):
        r_acc = self.spin_r_acc.value()
        r_hold = self.spin_r_hold.value()
        r_dec = self.spin_r_dec.value()
        r_stable = self.spin_r_stable.value()
        params_str = f"Acc: {r_acc:.1f}s, Hold: {r_hold:.1f}s, Dec: {r_dec:.1f}s, Stable: {r_stable:.1f}s"
        formatted = f"REVERSE,{r_acc:.1f},{r_hold:.1f},{r_dec:.1f},{r_stable:.1f}"
        self.send_profile_requested.emit("REVERSE", params_str, formatted)

    def _on_send_forward_clicked(self):
        f_acc = self.spin_f_acc.value()
        f_hold = self.spin_f_hold.value()
        f_dec = self.spin_f_dec.value()
        f_stable = self.spin_f_stable.value()
        params_str = f"Acc: {f_acc:.1f}s, Hold: {f_hold:.1f}s, Dec: {f_dec:.1f}s, Stable: {f_stable:.1f}s"
        formatted = f"FORWARD,{f_acc:.1f},{f_hold:.1f},{f_dec:.1f},{f_stable:.1f}"
        self.send_profile_requested.emit("FORWARD", params_str, formatted)

    def add_command_log(self, phase: str, params_str: str, command_str: str, success: bool = True):
        """Appends transmitted profile command to history log with crystal-clear contrast."""
        row = self.table_history.rowCount()
        self.table_history.insertRow(row)

        time_str = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        item_time = QTableWidgetItem(time_str)
        item_time.setTextAlignment(Qt.AlignCenter)
        item_time.setForeground(QColor("#0F172A"))

        item_phase = QTableWidgetItem(phase)
        item_phase.setTextAlignment(Qt.AlignCenter)
        if phase == "REVERSE":
            item_phase.setForeground(QColor("#D97706"))
        else:
            item_phase.setForeground(QColor("#0284C7"))

        item_params = QTableWidgetItem(params_str)
        item_params.setForeground(QColor("#0F172A"))

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
        self.table_history.setItem(row, 1, item_phase)
        self.table_history.setItem(row, 2, item_params)
        self.table_history.setItem(row, 3, item_cmd)
        self.table_history.setItem(row, 4, item_status)
        self.table_history.scrollToBottom()
