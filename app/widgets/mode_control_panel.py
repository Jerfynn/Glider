"""
Vehicle Mode and Actuation Control Panel.
Placed in the left sidebar below Attitude Indicator.
Provides Mode Switching: MANUAL (0) / AUTO (TIMING (1) & DEPTH (2)),
Safety Stop Confirmation Modal, and Manual Keyboard Navigation hints.
"""

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QDialog
)
from app.config import COLORS


class StopConfirmationDialog(QDialog):
    """
    Centered modal dialog shown when switching from AUTO to MANUAL mode,
    prompting the operator to STOP vehicle motion before enabling manual control.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Safety Warning - Stop Required")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(380, 240)

        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(10, 10, 10, 10)

        card = QFrame()
        card.setObjectName("StopModalCard")
        card.setStyleSheet(f"""
            QFrame#StopModalCard {{
                background-color: #FFFFFF;
                border: 2px solid #EF4444;
                border-radius: 12px;
            }}
        """)
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(16, 12, 16, 16)
        card_lay.setSpacing(8)
        card_lay.setAlignment(Qt.AlignCenter)

        # Top close X
        top_row = QHBoxLayout()
        top_row.addStretch()
        btn_close_top = QPushButton("✕")
        btn_close_top.setFixedSize(22, 22)
        btn_close_top.setCursor(Qt.PointingHandCursor)
        btn_close_top.setStyleSheet("""
            QPushButton {
                background: #F1F5F9;
                color: #64748B;
                border-radius: 11px;
                font-size: 11px;
                font-weight: 700;
                border: none;
            }
            QPushButton:hover {
                background: #EF4444;
                color: #FFFFFF;
            }
        """)
        btn_close_top.clicked.connect(self.reject)
        top_row.addWidget(btn_close_top)
        card_lay.addLayout(top_row)

        # Center Red Stop Badge
        stop_badge = QLabel("STOP")
        stop_badge.setAlignment(Qt.AlignCenter)
        stop_badge.setFixedSize(64, 64)
        stop_badge.setStyleSheet("""
            QLabel {
                background-color: #DC2626;
                color: #FFFFFF;
                font-size: 15px;
                font-weight: 900;
                letter-spacing: 1px;
                border-radius: 32px;
                border: 3px solid #FCA5A5;
            }
        """)
        
        badge_container = QHBoxLayout()
        badge_container.setAlignment(Qt.AlignCenter)
        badge_container.addWidget(stop_badge)
        card_lay.addLayout(badge_container)

        # Title
        title_lbl = QLabel("VEHICLE STOP REQUIRED")
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setStyleSheet("color: #DC2626; font-size: 14px; font-weight: 800; letter-spacing: 0.5px;")
        card_lay.addWidget(title_lbl)

        # Message
        msg_lbl = QLabel("Autonomous (AUTO) mode is active.<br>Vehicle must be <b>STOPPED</b> before switching to <b>MANUAL</b> control.")
        msg_lbl.setAlignment(Qt.AlignCenter)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("color: #334155; font-size: 11px; line-height: 1.4;")
        card_lay.addWidget(msg_lbl)

        # Action Buttons
        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)
        btn_box.setAlignment(Qt.AlignCenter)

        self.btn_cancel = QPushButton("CANCEL")
        self.btn_cancel.setFixedHeight(30)
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #475569;
                font-size: 11px;
                font-weight: 600;
                border-radius: 6px;
                padding: 4px 14px;
                border: 1px solid #CBD5E1;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_stop_and_manual = QPushButton("STOP && SWITCH TO MANUAL")
        self.btn_stop_and_manual.setFixedHeight(30)
        self.btn_stop_and_manual.setCursor(Qt.PointingHandCursor)
        self.btn_stop_and_manual.setStyleSheet("""
            QPushButton {
                background-color: #DC2626;
                color: #FFFFFF;
                font-size: 11px;
                font-weight: 700;
                border-radius: 6px;
                padding: 4px 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #B91C1C;
            }
        """)
        self.btn_stop_and_manual.clicked.connect(self.accept)

        btn_box.addWidget(self.btn_cancel)
        btn_box.addWidget(self.btn_stop_and_manual)
        card_lay.addLayout(btn_box)

        main_lay.addWidget(card)


class VehicleModeControlPanel(QFrame):
    """
    Dedicated Left Sidebar Mode Control Panel.
    Allows switching between MANUAL (0) and AUTO (1: Timing / 2: Depth),
    with safety confirmation dialog and keyboard navigation instructions.
    """
    mode_changed = Signal(str)       # Emits "AUTO" or "MANUAL"
    command_requested = Signal(str)  # Emits "0", "1", "2", "w", "s", "x"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("VehicleModeCard")
        self.setStyleSheet(f"""
            QFrame#VehicleModeCard {{
                background-color: #FFFFFF;
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
            }}
        """)
        self.current_mode: str = "MANUAL"
        self.current_auto_submode: str = "TIMING"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        # Header Title: VEHICLE MODE
        header_row = QHBoxLayout()
        header_row.setSpacing(6)

        bar = QFrame()
        bar.setFixedWidth(3)
        bar.setFixedHeight(12)
        bar.setStyleSheet(f"background-color: {COLORS['accent_yellow']}; border-radius: 1px;")

        title = QLabel("VEHICLE MODE & CONTROL")
        title.setObjectName("CardTitle")
        title.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {COLORS['text_primary']}; letter-spacing: 0.5px;")

        header_row.addWidget(bar)
        header_row.addWidget(title)
        header_row.addStretch()
        layout.addLayout(header_row)

        # Primary Mode Pill Switch (MANUAL (0) vs AUTO)
        self.mode_pill_container = QFrame()
        self.mode_pill_container.setObjectName("ModePillContainer")
        self.mode_pill_container.setStyleSheet(f"""
            QFrame#ModePillContainer {{
                background-color: #F1F5F9;
                border: 1px solid {COLORS['border']};
                border-radius: 16px;
                padding: 2px;
            }}
        """)
        pill_layout = QHBoxLayout(self.mode_pill_container)
        pill_layout.setContentsMargins(3, 3, 3, 3)
        pill_layout.setSpacing(4)

        self.btn_manual = QPushButton("MANUAL (0)")
        self.btn_manual.setFixedHeight(28)
        self.btn_manual.setCursor(Qt.PointingHandCursor)
        self.btn_manual.setToolTip("Switch to Manual Control Mode (Sends '0')")
        self.btn_manual.clicked.connect(self._on_manual_clicked)

        self.btn_auto = QPushButton("AUTO")
        self.btn_auto.setFixedHeight(28)
        self.btn_auto.setCursor(Qt.PointingHandCursor)
        self.btn_auto.setToolTip("Switch to Automatic Mode (Timing '1' / Depth '2')")
        self.btn_auto.clicked.connect(self._on_auto_clicked)

        pill_layout.addWidget(self.btn_manual, 1)
        pill_layout.addWidget(self.btn_auto, 1)
        layout.addWidget(self.mode_pill_container)

        # Auto Sub-Mode Selector (Timing (1) vs Depth (2))
        self.auto_submode_container = QFrame()
        self.auto_submode_container.setObjectName("AutoSubmodeContainer")
        self.auto_submode_container.setStyleSheet(f"""
            QFrame#AutoSubmodeContainer {{
                background-color: #FFFFFF;
                border: 1px solid {COLORS['border']};
                border-radius: 14px;
                padding: 2px;
            }}
        """)
        submode_layout = QHBoxLayout(self.auto_submode_container)
        submode_layout.setContentsMargins(2, 2, 2, 2)
        submode_layout.setSpacing(4)

        self.btn_auto_timing = QPushButton("⏱ TIMING (1)")
        self.btn_auto_timing.setFixedHeight(24)
        self.btn_auto_timing.setCursor(Qt.PointingHandCursor)
        self.btn_auto_timing.setToolTip("Timing-Based Autonomous Cycle (Sends '1')")
        self.btn_auto_timing.clicked.connect(self._on_timing_clicked)

        self.btn_auto_depth = QPushButton("⚓ DEPTH (2)")
        self.btn_auto_depth.setFixedHeight(24)
        self.btn_auto_depth.setCursor(Qt.PointingHandCursor)
        self.btn_auto_depth.setToolTip("Depth-Based Autonomous Cycle (Sends '2')")
        self.btn_auto_depth.clicked.connect(self._on_depth_clicked)

        submode_layout.addWidget(self.btn_auto_timing, 1)
        submode_layout.addWidget(self.btn_auto_depth, 1)
        layout.addWidget(self.auto_submode_container)

        # Manual Mode Keybinding Hint Banner (visible in MANUAL mode)
        self.manual_hint_card = QFrame()
        self.manual_hint_card.setObjectName("ManualHintCard")
        self.manual_hint_card.setStyleSheet(f"""
            QFrame#ManualHintCard {{
                background-color: #EFF6FF;
                border: 1px solid #BFDBFE;
                border-radius: 6px;
                padding: 6px 8px;
            }}
        """)
        hint_lay = QVBoxLayout(self.manual_hint_card)
        hint_lay.setContentsMargins(6, 6, 6, 6)
        hint_lay.setSpacing(4)
        
        lbl_hint_title = QLabel("⌨ MANUAL CONTROLS ACTIVE (0)")
        lbl_hint_title.setAlignment(Qt.AlignCenter)
        lbl_hint_title.setStyleSheet("color: #1E40AF; font-size: 10px; font-weight: 700; letter-spacing: 0.4px;")
        
        lbl_hint_keys = QLabel("<b>[W]</b> Forward &nbsp;|&nbsp; <b>[S]</b> Reverse<br><b>[SPACE / X]</b> Motor Stop")
        lbl_hint_keys.setAlignment(Qt.AlignCenter)
        lbl_hint_keys.setStyleSheet("color: #1E3A8A; font-size: 10px; line-height: 1.3;")
        
        hint_lay.addWidget(lbl_hint_title)
        hint_lay.addWidget(lbl_hint_keys)
        layout.addWidget(self.manual_hint_card)

        layout.addStretch(1)

        self._update_mode_ui()

    def _on_manual_clicked(self):
        """Called when user clicks the MANUAL button (Sends '0')."""
        if self.current_mode == "AUTO":
            dlg = StopConfirmationDialog(self.window())
            if dlg.exec() == QDialog.Accepted:
                self.command_requested.emit("x")
                self.command_requested.emit("0")
                self.set_mode("MANUAL")
            else:
                self._update_mode_ui()
        else:
            self.command_requested.emit("0")
            self.set_mode("MANUAL")

    def _on_auto_clicked(self):
        """Called when user clicks the AUTO button."""
        cmd = "1" if self.current_auto_submode == "TIMING" else "2"
        self.command_requested.emit(cmd)
        self.set_mode("AUTO", self.current_auto_submode)

    def _on_timing_clicked(self):
        """Called when user selects Timing-based Auto submode (Sends '1')."""
        self.command_requested.emit("1")
        self.set_mode("AUTO", "TIMING")

    def _on_depth_clicked(self):
        """Called when user selects Depth-based Auto submode (Sends '2')."""
        self.command_requested.emit("2")
        self.set_mode("AUTO", "DEPTH")

    def set_mode(self, mode: str, submode: str = "TIMING"):
        """Sets active operation mode ('AUTO' or 'MANUAL') and auto submode ('TIMING' or 'DEPTH')."""
        mode = mode.upper().strip()
        if mode not in ("AUTO", "MANUAL"):
            mode = "MANUAL"
        submode = submode.upper().strip()
        if submode not in ("TIMING", "DEPTH"):
            submode = "TIMING"

        changed = (self.current_mode != mode or self.current_auto_submode != submode)
        self.current_mode = mode
        self.current_auto_submode = submode
        self._update_mode_ui()
        if changed:
            self.mode_changed.emit(self.current_mode)

    def _update_mode_ui(self):
        """Updates the visual appearance of the mode switches, sub-mode pills, and hints."""
        if self.current_mode == "AUTO":
            self.manual_hint_card.setVisible(False)
            self.auto_submode_container.setVisible(True)

            self.btn_auto.setStyleSheet("""
                QPushButton {
                    background-color: #2563EB;
                    color: #FFFFFF;
                    font-size: 11px;
                    font-weight: 700;
                    border: none;
                    border-radius: 13px;
                    padding: 2px 14px;
                }
                QPushButton:hover {
                    background-color: #1D4ED8;
                }
            """)
            self.btn_manual.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #64748B;
                    font-size: 11px;
                    font-weight: 600;
                    border: none;
                    border-radius: 13px;
                    padding: 2px 12px;
                }
                QPushButton:hover {
                    color: #1E293B;
                    background-color: #E2E8F0;
                }
            """)

            if self.current_auto_submode == "TIMING":
                self.btn_auto_timing.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['accent_yellow']};
                        color: #FFFFFF;
                        font-size: 10px;
                        font-weight: 700;
                        border: none;
                        border-radius: 11px;
                        padding: 2px 8px;
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS['accent_yellow_hover']};
                    }}
                """)
                self.btn_auto_depth.setStyleSheet("""
                    QPushButton {{
                        background-color: transparent;
                        color: #64748B;
                        font-size: 10px;
                        font-weight: 600;
                        border: none;
                        border-radius: 11px;
                        padding: 2px 8px;
                    }}
                    QPushButton:hover {{
                        color: #0F172A;
                        background-color: #F1F5F9;
                    }}
                """)
            else:
                self.btn_auto_timing.setStyleSheet("""
                    QPushButton {{
                        background-color: transparent;
                        color: #64748B;
                        font-size: 10px;
                        font-weight: 600;
                        border: none;
                        border-radius: 11px;
                        padding: 2px 8px;
                    }}
                    QPushButton:hover {{
                        color: #0F172A;
                        background-color: #F1F5F9;
                    }}
                """)
                self.btn_auto_depth.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['accent_yellow']};
                        color: #FFFFFF;
                        font-size: 10px;
                        font-weight: 700;
                        border: none;
                        border-radius: 11px;
                        padding: 2px 8px;
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS['accent_yellow_hover']};
                    }}
                """)
        else:
            # MANUAL MODE ACTIVE
            self.manual_hint_card.setVisible(True)
            self.auto_submode_container.setVisible(False)

            self.btn_manual.setStyleSheet("""
                QPushButton {
                    background-color: #2563EB;
                    color: #FFFFFF;
                    font-size: 11px;
                    font-weight: 700;
                    border: none;
                    border-radius: 13px;
                    padding: 2px 14px;
                }
                QPushButton:hover {
                    background-color: #1D4ED8;
                }
            """)
            self.btn_auto.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #64748B;
                    font-size: 11px;
                    font-weight: 600;
                    border: none;
                    border-radius: 13px;
                    padding: 2px 12px;
                }
                QPushButton:hover {
                    color: #1E293B;
                    background-color: #E2E8F0;
                }
            """)
