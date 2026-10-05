"""
Right Sidebar Telemetry Metrics Panel.
Clean engineering layout for White / Light Theme with full sensor channel telemetry support.
Configured with exact requested engineering sections:
  1. PROPULSION AND ACTUATION (motor mode, motor pwm, motor state)
  2. ACCELERATION (acc_X, acc_y, acc_z)
  3. ATTITUDE & GYRO (roll, pitch, yaw, gyro_x, gyro_y, gyro_z)
  4. INTERNAL CHAMBER (pressure bar, pressure psi)
  5. EXTERNAL CHAMBER (pressure bar, depth, previous depth, current depth, change in depth)
  6. INTERNAL ENVIRONMENT (temperature, humidity)
  7. POWER SYSTEM (current, voltage)
"""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea
)
from app.config import COLORS
from app.core.telemetry_model import TelemetryPacket


class MetricItemRow(QWidget):
    """A clean two-column metric row: label on left, formatted value on right."""

    def __init__(self, label: str, init_val: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(6)

        self.lbl_title = QLabel(label)
        self.lbl_title.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px; font-weight: 500;")
        layout.addWidget(self.lbl_title)

        layout.addStretch()

        self.lbl_val = QLabel(init_val)
        self.lbl_val.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 12px;
            font-weight: 600;
            font-family: 'Consolas', 'Roboto Mono', 'SF Mono', monospace;
        """)
        layout.addWidget(self.lbl_val)

    def set_value(self, val_text: str, is_valid: bool = True):
        self.lbl_val.setText(val_text)
        if not is_valid or val_text.upper() in ("INVALID", "ERR", "NAN", "--"):
            self.lbl_val.setStyleSheet(f"""
                color: {COLORS['text_secondary']};
                font-size: 11px;
                font-weight: 600;
                font-family: 'Consolas', monospace;
                background-color: #F3F4F6;
                padding: 1px 4px;
                border-radius: 3px;
            """)
        else:
            self.lbl_val.setStyleSheet(f"""
                color: {COLORS['text_primary']};
                font-size: 12px;
                font-weight: 600;
                font-family: 'Consolas', 'Roboto Mono', 'SF Mono', monospace;
            """)


def create_section_header(title: str) -> QWidget:
    """Helper to create compact section header with subtle divider."""
    container = QWidget()
    lay = QVBoxLayout(container)
    lay.setContentsMargins(0, 4, 0, 2)
    lay.setSpacing(2)

    lbl = QLabel(title.upper())
    lbl.setStyleSheet(f"color: {COLORS['accent_yellow']}; font-size: 10px; font-weight: 700; letter-spacing: 0.5px;")
    lay.addWidget(lbl)
    return container


class TelemetryMetricsPanel(QFrame):
    """
    Right sidebar panel displaying the full 7-section engineering telemetry suite.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TelemetryMetricsCard")
        self.setFrameShape(QFrame.StyledPanel)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(4)

        # Main Panel Header: TELEMETRY
        header_row = QHBoxLayout()
        header_row.setSpacing(6)
        
        bar = QFrame()
        bar.setFixedWidth(3)
        bar.setFixedHeight(12)
        bar.setStyleSheet(f"background-color: {COLORS['accent_yellow']}; border-radius: 1px;")
        
        title = QLabel("TELEMETRY")
        title.setObjectName("CardTitle")

        header_row.addWidget(bar)
        header_row.addWidget(title)
        header_row.addStretch()
        main_layout.addLayout(header_row)

        # Scroll area to comfortably fit all telemetry channels
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 4, 0)
        layout.setSpacing(2)

        # 1. PROPULSION AND ACTUATION
        layout.addWidget(create_section_header("Propulsion and Actuation"))
        self.row_motor_mode = MetricItemRow("motor mode", "MANUAL (0)", self)
        self.row_pwm = MetricItemRow("motor pwm", "1500 µs", self)
        self.row_pwm_state = MetricItemRow("motor state", "MANUAL_STOP", self)
        layout.addWidget(self.row_motor_mode)
        layout.addWidget(self.row_pwm)
        layout.addWidget(self.row_pwm_state)

        # 2. ACCELERATION
        layout.addWidget(create_section_header("Acceleration"))
        self.row_acc_x = MetricItemRow("acc_X", "+0.000 g", self)
        self.row_acc_y = MetricItemRow("acc_y", "+0.000 g", self)
        self.row_acc_z = MetricItemRow("acc_z", "+0.000 g", self)
        layout.addWidget(self.row_acc_x)
        layout.addWidget(self.row_acc_y)
        layout.addWidget(self.row_acc_z)

        # 3. ATTITUDE & GYRO
        layout.addWidget(create_section_header("Attitude & Gyro"))
        self.row_roll = MetricItemRow("roll", "+0.00 °", self)
        self.row_pitch = MetricItemRow("pitch", "+0.00 °", self)
        self.row_yaw = MetricItemRow("yaw", "0.00 °", self)
        self.row_gyro_x = MetricItemRow("gyro_x", "+0.00 °/s", self)
        self.row_gyro_y = MetricItemRow("gyro_y", "+0.00 °/s", self)
        self.row_gyro_z = MetricItemRow("gyro_z", "+0.00 °/s", self)
        layout.addWidget(self.row_roll)
        layout.addWidget(self.row_pitch)
        layout.addWidget(self.row_yaw)
        layout.addWidget(self.row_gyro_x)
        layout.addWidget(self.row_gyro_y)
        layout.addWidget(self.row_gyro_z)

        # 4. INTERNAL CHAMBER
        layout.addWidget(create_section_header("Internal Chamber"))
        self.row_int_pressure_bar = MetricItemRow("BMP pressure bar", "0.0000 bar", self)
        self.row_int_pressure_psi = MetricItemRow("BMP pressure psi", "0.00 psi", self)
        layout.addWidget(self.row_int_pressure_bar)
        layout.addWidget(self.row_int_pressure_psi)

        # 5. EXTERNAL CHAMBER
        layout.addWidget(create_section_header("External Chamber"))
        self.row_ext_pressure_bar = MetricItemRow("MS5837 pressure bar", "0.0000 bar", self)
        self.row_curr_depth = MetricItemRow("current depth", "0.00 m", self)
        self.row_prev_depth = MetricItemRow("previous depth", "0.00 m", self)
        self.row_delta_depth = MetricItemRow("change in depth", "0.00 m", self)
        layout.addWidget(self.row_ext_pressure_bar)
        layout.addWidget(self.row_curr_depth)
        layout.addWidget(self.row_prev_depth)
        layout.addWidget(self.row_delta_depth)

        # 6. INTERNAL ENVIRONMENT
        layout.addWidget(create_section_header("Internal Environment"))
        self.row_temp = MetricItemRow("temperature", "0.00 °C", self)
        self.row_humidity = MetricItemRow("humidity", "0.0 %", self)
        self.row_flow = MetricItemRow("flow", "0.00 L/min", self)
        layout.addWidget(self.row_temp)
        layout.addWidget(self.row_humidity)
        layout.addWidget(self.row_flow)

        # 7. POWER SYSTEM
        layout.addWidget(create_section_header("Power System"))
        self.row_current = MetricItemRow("current", "0.00 A", self)
        self.row_voltage = MetricItemRow("voltage", "0.00 V", self)
        layout.addWidget(self.row_current)
        layout.addWidget(self.row_voltage)

        # Dynamic Low Battery Warning Alert Banner
        self.battery_warning_card = QFrame()
        self.battery_warning_card.setObjectName("BatteryWarningCard")
        self.battery_warning_card.setStyleSheet(f"""
            QFrame#BatteryWarningCard {{
                background-color: {COLORS['status_red_bg']};
                border: 1px solid {COLORS['status_red_border']};
                border-radius: 4px;
                padding: 4px 6px;
            }}
        """)
        batt_warn_lay = QVBoxLayout(self.battery_warning_card)
        batt_warn_lay.setContentsMargins(4, 2, 4, 2)
        batt_warn_lay.setSpacing(1)

        lbl_batt_warn_title = QLabel("⚠️ LOW BATTERY WARNING")
        lbl_batt_warn_title.setAlignment(Qt.AlignCenter)
        lbl_batt_warn_title.setStyleSheet(f"color: {COLORS['status_red']}; font-size: 9px; font-weight: 800; letter-spacing: 0.5px;")
        
        self.lbl_batt_warn_sub = QLabel("Voltage critical (< 22.0 V)")
        self.lbl_batt_warn_sub.setAlignment(Qt.AlignCenter)
        self.lbl_batt_warn_sub.setStyleSheet("color: #991B1B; font-size: 8px; font-weight: 600;")

        batt_warn_lay.addWidget(lbl_batt_warn_title)
        batt_warn_lay.addWidget(self.lbl_batt_warn_sub)
        layout.addWidget(self.battery_warning_card)
        self.battery_warning_card.setVisible(False)

        layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)

    def update_telemetry(self, packet: TelemetryPacket):
        """Updates all telemetry channel readouts with incoming data."""
        # 1. Propulsion and Actuation
        self.row_motor_mode.set_value(packet.motor_mode or "MANUAL (0)")
        self.row_pwm.set_value(f"{packet.pwm} µs")
        self.row_pwm_state.set_value(packet.pwmstate or "STOP")

        # 2. Acceleration
        self.row_acc_x.set_value(f"{packet.acc_x:+.3f} g")
        self.row_acc_y.set_value(f"{packet.acc_y:+.3f} g")
        self.row_acc_z.set_value(f"{packet.acc_z:+.3f} g")

        # 3. Attitude & Gyro
        self.row_roll.set_value(f"{packet.roll:+.2f} °")
        self.row_pitch.set_value(f"{packet.pitch:+.2f} °")
        self.row_yaw.set_value(f"{packet.yaw:+.2f} °")
        self.row_gyro_x.set_value(f"{packet.gyro_x:+.2f} °/s")
        self.row_gyro_y.set_value(f"{packet.gyro_y:+.2f} °/s")
        self.row_gyro_z.set_value(f"{packet.gyro_z:+.2f} °/s")

        # 4. Internal Chamber
        self.row_int_pressure_bar.set_value(f"{packet.pressure:.4f} bar", is_valid=packet.pressure_valid)
        self.row_int_pressure_psi.set_value(f"{packet.pressure_psi:.2f} psi", is_valid=packet.pressure_psi_valid or packet.pressure_valid)

        # 5. External Chamber
        self.row_ext_pressure_bar.set_value(f"{packet.pressure_2:.4f} bar", is_valid=packet.pressure_2_valid)
        curr_d = packet.curr_depth if (packet.curr_depth_valid and packet.curr_depth != 0.0) else packet.depth
        self.row_curr_depth.set_value(f"{curr_d:.2f} m", is_valid=packet.curr_depth_valid or packet.depth_valid)
        self.row_prev_depth.set_value(f"{packet.prev_depth:.2f} m", is_valid=packet.prev_depth_valid)
        self.row_delta_depth.set_value(f"{packet.delta_depth:+.2f} m", is_valid=packet.delta_depth_valid)

        # 6. Internal Environment
        self.row_temp.set_value(f"{packet.temperature:.2f} °C", is_valid=packet.temperature_valid)
        self.row_humidity.set_value(f"{packet.humidity:.1f} %")
        self.row_flow.set_value(f"{packet.flow:.2f} L/min")

        # 7. Power System
        voltage = packet.battery_voltage
        self.row_current.set_value(f"{packet.battery_current:.2f} A")
        self.row_voltage.set_value(f"{voltage:.2f} V")

        # Battery warning condition (< 22.0 V)
        if 0.0 < voltage < 22.0:
            self.battery_warning_card.setVisible(True)
            self.lbl_batt_warn_sub.setText(f"Voltage critical ({voltage:.2f} V < 22.0 V)")
            self.row_voltage.lbl_val.setStyleSheet("color: #DC2626; font-size: 12px; font-weight: 800; font-family: 'Consolas', monospace;")
        else:
            self.battery_warning_card.setVisible(False)
