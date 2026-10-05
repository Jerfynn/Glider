"""
Connection Configuration Panel Widget.
Supports UDP Network socket reception and Serial COM ports.
Clean White / Light Theme with Amber Accent.
"""

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QComboBox,
    QLineEdit, QPushButton, QFrame, QCheckBox, QStackedWidget
)
from app.config import (
    COLORS, DEFAULT_BAUD_RATES
)
from app.core.serial_worker import SerialWorker
from app.utils.icons import get_icon


class ConnectionPanel(QFrame):
    """
    Left-hand panel allowing selection of Connection Mode (UDP / Serial),
    Network IP/Port, COM Port, Baud Rate, Simulation mode, and Connect/Disconnect action.
    """

    # Signal emits: (mode, port, baud, data_bits, parity, stop_bits, ip, udp_port, is_sim)
    connect_requested = Signal(str, str, int, int, str, str, str, int, bool)
    disconnect_requested = Signal()
    calibrate_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ConnectionCard")
        self.setFrameShape(QFrame.StyledPanel)

        self.is_connected = False
        self.is_started = False

        LABEL_WIDTH = 68  # Exact uniform label width for perfect grid alignment

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # 1. Section Header: CONNECTION
        header_layout = QHBoxLayout()
        header_layout.setSpacing(6)
        
        bar = QFrame()
        bar.setFixedWidth(3)
        bar.setFixedHeight(12)
        bar.setStyleSheet(f"background-color: {COLORS['accent_yellow']}; border-radius: 1px;")
        
        title = QLabel("CONNECTION")
        title.setObjectName("CardTitle")

        header_layout.addWidget(bar)
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # 2. Mode Selector: TCP Network vs UDP Network vs Serial COM
        mode_layout = QHBoxLayout()
        mode_layout.setContentsMargins(0, 0, 0, 0)
        mode_layout.setSpacing(8)

        lbl_mode = QLabel("Mode")
        lbl_mode.setObjectName("SubtleLabel")
        lbl_mode.setFixedWidth(LABEL_WIDTH)
        
        self.combo_mode = QComboBox()
        self.combo_mode.setFixedHeight(27)
        self.combo_mode.addItem("TCP Network (Raspberry Pi)")
        self.combo_mode.addItem("UDP Network")
        self.combo_mode.addItem("Serial COM")
        self.combo_mode.currentIndexChanged.connect(self._on_mode_changed)

        mode_layout.addWidget(lbl_mode)
        mode_layout.addWidget(self.combo_mode, 1)
        layout.addLayout(mode_layout)

        # 3. Stacked Configuration Widget
        self.stack = QStackedWidget()
        
        # --- Page 0: Network Settings (TCP / UDP) ---
        net_page = QWidget()
        net_layout = QVBoxLayout(net_page)
        net_layout.setContentsMargins(0, 0, 0, 0)
        net_layout.setSpacing(6)

        # Row 1: Target IP
        row_ip = QHBoxLayout()
        row_ip.setContentsMargins(0, 0, 0, 0)
        row_ip.setSpacing(8)

        lbl_ip = QLabel("Target IP")
        lbl_ip.setObjectName("SubtleLabel")
        lbl_ip.setFixedWidth(LABEL_WIDTH)

        self.txt_ip = QLineEdit()
        self.txt_ip.setText("192.168.1.51")
        self.txt_ip.setFixedHeight(27)
        self.txt_ip.setPlaceholderText("192.168.1.51")

        row_ip.addWidget(lbl_ip)
        row_ip.addWidget(self.txt_ip, 1)
        net_layout.addLayout(row_ip)

        # Row 2: Port
        row_port = QHBoxLayout()
        row_port.setContentsMargins(0, 0, 0, 0)
        row_port.setSpacing(8)

        self.lbl_port = QLabel("Port")
        self.lbl_port.setObjectName("SubtleLabel")
        self.lbl_port.setFixedWidth(LABEL_WIDTH)

        self.txt_port = QLineEdit()
        self.txt_port.setText("5000")
        self.txt_port.setFixedHeight(27)
        self.txt_port.setPlaceholderText("5000")

        row_port.addWidget(self.lbl_port)
        row_port.addWidget(self.txt_port, 1)
        net_layout.addLayout(row_port)

        self.stack.addWidget(net_page)

        # --- Page 1: Serial COM Settings ---
        serial_page = QWidget()
        serial_layout = QVBoxLayout(serial_page)
        serial_layout.setContentsMargins(0, 0, 0, 0)
        serial_layout.setSpacing(6)

        # Row 1: COM Port
        row_com = QHBoxLayout()
        row_com.setContentsMargins(0, 0, 0, 0)
        row_com.setSpacing(8)

        lbl_com = QLabel("COM Port")
        lbl_com.setObjectName("SubtleLabel")
        lbl_com.setFixedWidth(LABEL_WIDTH)
        
        port_box = QHBoxLayout()
        port_box.setSpacing(4)
        self.combo_port = QComboBox()
        self.combo_port.setFixedHeight(27)
        
        self.btn_refresh = QPushButton()
        self.btn_refresh.setIcon(get_icon("refresh", color=COLORS["text_secondary"], size=13))
        self.btn_refresh.setFixedSize(27, 27)
        self.btn_refresh.setToolTip("Scan COM Ports")
        self.btn_refresh.clicked.connect(self.refresh_ports)

        port_box.addWidget(self.combo_port, 1)
        port_box.addWidget(self.btn_refresh)

        row_com.addWidget(lbl_com)
        row_com.addLayout(port_box, 1)
        serial_layout.addLayout(row_com)

        # Row 2: Baud Rate
        row_baud = QHBoxLayout()
        row_baud.setContentsMargins(0, 0, 0, 0)
        row_baud.setSpacing(8)

        lbl_baud = QLabel("Baud Rate")
        lbl_baud.setObjectName("SubtleLabel")
        lbl_baud.setFixedWidth(LABEL_WIDTH)

        self.combo_baud = QComboBox()
        self.combo_baud.setFixedHeight(27)
        for b in DEFAULT_BAUD_RATES:
            self.combo_baud.addItem(b)
        self.combo_baud.setCurrentText("115200")

        row_baud.addWidget(lbl_baud)
        row_baud.addWidget(self.combo_baud, 1)
        serial_layout.addLayout(row_baud)

        self.stack.addWidget(serial_page)

        layout.addWidget(self.stack)

        # 4. Simulation / Demo Mode Checkbox
        self.chk_sim = QCheckBox("Simulation / Demo Mode")
        self.chk_sim.setChecked(False)
        self.chk_sim.setFixedHeight(20)
        layout.addWidget(self.chk_sim)

        # 5. Action Buttons: CONNECT, START, CALIBRATE
        self.btn_toggle = QPushButton("CONNECT")
        self.btn_toggle.setObjectName("PrimaryButton")
        self.btn_toggle.setFixedHeight(28)
        self.btn_toggle.clicked.connect(self._on_toggle_clicked)
        layout.addWidget(self.btn_toggle)

        self.btn_start = QPushButton("START")
        self.btn_start.setFixedHeight(28)
        self.btn_start.setStyleSheet(f"""
            QPushButton {{
                background-color: #16A34A;
                border: 1px solid #15803D;
                border-radius: 3px;
                color: #FFFFFF;
                font-weight: 700;
                font-size: 11px;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background-color: #15803D;
            }}
            QPushButton:pressed {{
                background-color: #166534;
            }}
            QPushButton:disabled {{
                background-color: #E2E8F0;
                color: #94A3B8;
                border-color: #CBD5E1;
            }}
        """)
        self.btn_start.clicked.connect(self._on_start_clicked)
        layout.addWidget(self.btn_start)

        # 7. Calibrate Vehicle Button
        self.btn_calibrate = QPushButton("CALIBRATE VEHICLE")
        self.btn_calibrate.setFixedHeight(28)
        self.btn_calibrate.setCursor(Qt.PointingHandCursor)
        self.btn_calibrate.setToolTip("Transmit sensor zeroing & buoyancy calibration commands")
        self.btn_calibrate.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF;
                border: 1px solid {COLORS['accent_yellow']};
                border-radius: 3px;
                color: {COLORS['accent_yellow']};
                font-weight: 700;
                font-size: 11px;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_yellow_subtle']};
                color: {COLORS['accent_yellow_hover']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['accent_yellow']};
                color: #FFFFFF;
            }}
        """)
        self.btn_calibrate.clicked.connect(self._on_calibrate_clicked)
        layout.addWidget(self.btn_calibrate)

        # Initial ports population
        self.refresh_ports()

    def _on_mode_changed(self, index: int):
        text = self.combo_mode.currentText()
        if "TCP" in text or "UDP" in text:
            self.stack.setCurrentIndex(0)
            self.lbl_port.setText("UDP Port" if "UDP" in text else "Port")
        else:
            self.stack.setCurrentIndex(1)

    def refresh_ports(self):
        """Scans available COM ports and repopulates the dropdown."""
        current = self.combo_port.currentText()
        self.combo_port.clear()
        ports = SerialWorker.list_available_ports()
        
        if not ports:
            self.combo_port.addItem("COM10")
            self.combo_port.addItem("COM1")
            self.combo_port.addItem("COM3")
        else:
            for p in ports:
                self.combo_port.addItem(p)

        if current and self.combo_port.findText(current) != -1:
            self.combo_port.setCurrentText(current)

    def _on_toggle_clicked(self):
        if not self.is_connected:
            text = self.combo_mode.currentText()
            if "TCP" in text:
                mode = "TCP"
            elif "UDP" in text:
                mode = "UDP"
            else:
                mode = "SERIAL"

            port = self.combo_port.currentText()
            baud = int(self.combo_baud.currentText())
            db = 8
            par = "None"
            sb = "1"
            
            ip = self.txt_ip.text().strip() or "192.168.1.51"
            try:
                udp_port = int(self.txt_port.text().strip())
            except ValueError:
                udp_port = 5000

            is_sim = self.chk_sim.isChecked()
            self.connect_requested.emit(mode, port, baud, db, par, sb, ip, udp_port, is_sim)
        else:
            self.disconnect_requested.emit()

    def _on_start_clicked(self):
        self.is_started = not self.is_started
        if self.is_started:
            self.btn_start.setText("STOP")
            self.btn_start.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['status_red_bg']};
                    border: 1px solid {COLORS['status_red_border']};
                    border-radius: 3px;
                    color: {COLORS['status_red']};
                    font-weight: 700;
                    font-size: 11px;
                    letter-spacing: 0.5px;
                }}
                QPushButton:hover {{
                    background-color: #FECDCA;
                }}
            """)
        else:
            self.btn_start.setText("START")
            self.btn_start.setStyleSheet(f"""
                QPushButton {{
                    background-color: #16A34A;
                    border: 1px solid #15803D;
                    border-radius: 3px;
                    color: #FFFFFF;
                    font-weight: 700;
                    font-size: 11px;
                    letter-spacing: 0.5px;
                }}
                QPushButton:hover {{
                    background-color: #15803D;
                }}
            """)

    def _on_calibrate_clicked(self):
        """Emits vehicle calibration signal."""
        self.calibrate_requested.emit()

    def set_connected_state(self, connected: bool):
        self.is_connected = connected
        if connected:
            self.btn_toggle.setText("DISCONNECT")
            self.btn_toggle.setObjectName("DisconnectButton")
            self.btn_toggle.setStyle(self.btn_toggle.style())
            self.combo_mode.setEnabled(False)
            self.txt_ip.setEnabled(False)
            self.txt_port.setEnabled(False)
            self.combo_port.setEnabled(False)
            self.combo_baud.setEnabled(False)
            self.chk_sim.setEnabled(False)
        else:
            self.btn_toggle.setText("CONNECT")
            self.btn_toggle.setObjectName("PrimaryButton")
            self.btn_toggle.setStyle(self.btn_toggle.style())
            self.combo_mode.setEnabled(True)
            self.txt_ip.setEnabled(True)
            self.txt_port.setEnabled(True)
            self.combo_port.setEnabled(True)
            self.combo_baud.setEnabled(True)
            self.chk_sim.setEnabled(True)



