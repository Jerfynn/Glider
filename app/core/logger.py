"""
High-Performance Real-Time Telemetry CSV Logger.
Automatically writes all incoming telemetry data packets into timestamped .csv files
at user-configured storage folder location.
"""

import os
import csv
import time
from datetime import datetime
from typing import Optional
from app.core.telemetry_model import TelemetryPacket


class TelemetryCsvLogger:
    """
    Thread-safe CSV file writer for incoming glider/ROV telemetry stream.
    """

    CSV_HEADERS = [
        "ISO_DateTime",
        "Timestamp_Unix",
        "Motor_Mode",
        "Motor_PWM",
        "Motor_State",
        "Acc_X_g",
        "Acc_Y_g",
        "Acc_Z_g",
        "Gyro_X_dps",
        "Gyro_Y_dps",
        "Gyro_Z_dps",
        "Roll_Deg",
        "Pitch_Deg",
        "Yaw_Deg",
        "Pressure_1_Bar",
        "Pressure_1_Psi",
        "Pressure_2_Bar",
        "Target_Depth_M",
        "Prev_Depth_M",
        "Curr_Depth_M",
        "Delta_Depth_M",
        "Temperature_C",
        "Humidity_Pct",
        "Current_A",
        "Voltage_V",
        "Flow_L_min",
        "Raw_Packet"
    ]

    def __init__(self, log_dir: Optional[str] = None):
        if not log_dir:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            log_dir = os.path.join(base_dir, "logs")

        self.log_dir = os.path.abspath(log_dir)
        self.is_enabled = True
        self.current_file_path: Optional[str] = None
        self._file_handle = None
        self._csv_writer = None
        self.rows_written = 0

        self._ensure_dir_exists()

    def _ensure_dir_exists(self):
        try:
            os.makedirs(self.log_dir, exist_ok=True)
        except Exception:
            pass

    def set_log_dir(self, new_dir: str):
        """Sets new destination directory for CSV logs."""
        if not new_dir:
            return
        
        cleaned = os.path.abspath(new_dir.strip())
        if cleaned != self.log_dir:
            self._close_file()
            self.log_dir = cleaned
            self._ensure_dir_exists()

    def _get_new_filename(self) -> str:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.log_dir, f"glider_telemetry_{timestamp_str}.csv")

    def _open_file_if_needed(self):
        if self._file_handle is None:
            self._ensure_dir_exists()
            self.current_file_path = self._get_new_filename()
            try:
                self._file_handle = open(self.current_file_path, mode="w", newline="", encoding="utf-8")
                self._csv_writer = csv.writer(self._file_handle)
                self._csv_writer.writerow(self.CSV_HEADERS)
                self._file_handle.flush()
                self.rows_written = 0
            except Exception as e:
                self._file_handle = None
                self._csv_writer = None

    def log_packet(self, packet: TelemetryPacket):
        """Logs a single parsed TelemetryPacket to CSV."""
        if not self.is_enabled:
            return

        try:
            self._open_file_if_needed()
            if self._csv_writer and self._file_handle:
                now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                
                row = [
                    now_iso,
                    f"{packet.timestamp:.3f}",
                    packet.motor_mode,
                    packet.pwm,
                    packet.pwmstate,
                    f"{packet.acc_x:.3f}",
                    f"{packet.acc_y:.3f}",
                    f"{packet.acc_z:.3f}",
                    f"{packet.gyro_x:.2f}",
                    f"{packet.gyro_y:.2f}",
                    f"{packet.gyro_z:.2f}",
                    f"{packet.roll:+.2f}",
                    f"{packet.pitch:+.2f}",
                    f"{packet.yaw:.2f}",
                    f"{packet.pressure:.3f}" if packet.pressure_valid else "INVALID",
                    f"{packet.pressure_psi:.2f}" if packet.pressure_psi_valid else "INVALID",
                    f"{packet.pressure_2:.3f}" if packet.pressure_2_valid else "INVALID",
                    f"{packet.depth:.2f}" if packet.depth_valid else "INVALID",
                    f"{packet.prev_depth:.2f}" if packet.prev_depth_valid else "INVALID",
                    f"{packet.curr_depth:.2f}" if packet.curr_depth_valid else "INVALID",
                    f"{packet.delta_depth:.2f}" if packet.delta_depth_valid else "INVALID",
                    f"{packet.temperature:.2f}" if packet.temperature_valid else "INVALID",
                    f"{packet.humidity:.2f}",
                    f"{packet.battery_current:.2f}",
                    f"{packet.battery_voltage:.2f}",
                    f"{packet.flow:.2f}",
                    packet.raw_text
                ]
                
                self._csv_writer.writerow(row)
                self.rows_written += 1
                
                # Flush every 5 rows or immediately so data is written safely to disk
                if self.rows_written % 5 == 0:
                    self._file_handle.flush()
        except Exception:
            pass

    def flush(self):
        if self._file_handle:
            try:
                self._file_handle.flush()
            except Exception:
                pass

    def _close_file(self):
        if self._file_handle:
            try:
                self._file_handle.flush()
                self._file_handle.close()
            except Exception:
                pass
            self._file_handle = None
            self._csv_writer = None

    def close(self):
        """Clean close of active log file."""
        self._close_file()

    def get_stats(self):
        """Returns (log_dir, is_enabled, current_filename, rows_written, size_kb)."""
        filename = os.path.basename(self.current_file_path) if self.current_file_path else "None (Waiting for Data)"
        size_kb = 0.0
        if self.current_file_path and os.path.exists(self.current_file_path):
            try:
                size_kb = os.path.getsize(self.current_file_path) / 1024.0
            except Exception:
                size_kb = 0.0
        return self.log_dir, self.is_enabled, filename, self.rows_written, size_kb
