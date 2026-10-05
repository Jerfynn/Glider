"""
Data models for Glider Telemetry and Serial/UDP connection status.
Supports both legacy telemetry and UDP 19-parameter stream.
"""

from dataclasses import dataclass, field
import time
from typing import Optional


@dataclass
class TelemetryPacket:
    """
    Represents a single decoded telemetry update from the underwater vehicle.
    Supports 23-field stream:
    motor mode, motor pwm, motor state, acc_X, acc_y, acc_z, gyro_x, gyro_y, gyro_z,
    roll, pitch, yaw, pressure bar, pressure psi, pressure bar (2), depth,
    previous depth, current depth, change in depth, temperature, humidity, current, voltage
    """
    timestamp: float = field(default_factory=time.time)
    raw_timestamp: int = 0          # Milliseconds / ticks from onboard MCU
    
    # Propulsion & Actuators
    motor_mode: str = "MANUAL"      # MANUAL (0) / AUTO_TIMING (1) / AUTO_DEPTH (2)
    pwm: int = 1500                 # PWM pulse width (us)
    pwmstate: str = "STOP"          # Motor state (e.g. MANUAL_STOP, FWD, REV, STOP)
    
    # Accelerometers (g or m/s^2)
    acc_x: float = 0.0              # g
    acc_y: float = 0.0              # g
    acc_z: float = 0.0              # g
    
    # Gyroscope & Attitude (deg or deg/s)
    gyro_x: float = 0.0             # deg/s
    gyro_y: float = 0.0             # deg/s
    gyro_z: float = 0.0             # deg/s
    roll: float = 0.0               # deg
    pitch: float = 0.0              # deg
    yaw: float = 0.0                # deg
    
    # Pressure Sensors
    pressure: float = 0.0           # bar (Pressure Sensor 1 in bar)
    pressure_valid: bool = True
    pressure_psi: float = 0.0       # psi (Pressure Sensor 1 in psi)
    pressure_psi_valid: bool = True
    pressure_2: float = 0.0         # bar (Pressure Sensor 2 in bar)
    pressure_2_valid: bool = True
    
    # Depth Tracking (m)
    depth: float = 0.0              # Target / reference depth (m)
    depth_valid: bool = True
    prev_depth: float = 0.0         # Previous Depth (m)
    prev_depth_valid: bool = True
    curr_depth: float = 0.0         # Current Depth (m)
    curr_depth_valid: bool = True
    delta_depth: float = 0.0        # Change in Depth (m)
    delta_depth_valid: bool = True
    altitude: float = 0.0           # meters alias
    altitude_valid: bool = True
    
    # Environmental Metrics
    temperature: float = 0.0        # °C (Water / External Temperature)
    temperature_valid: bool = True
    temperature_2: float = 0.0      # °C (Sensor 2)
    temperature_2_valid: bool = True
    humidity: float = 0.0           # %
    flow: float = 0.0               # flow rate (L/min)
    
    # Battery System Metrics
    battery_current: float = 0.0    # Amperes (A)
    battery_voltage: float = 0.0    # Volts (V)
    battery_soc: float = 0.0        # State of Charge (%)
    battery_soh: float = 0.0        # State of Health (%)
    
    # Extra parameter
    extra_val: float = 0.0
    
    # Raw message & parsing status
    raw_text: str = ""
    is_valid: bool = True
    error_msg: str = ""


@dataclass
class ConnectionStats:
    """Real-time performance and connection metrics for Serial & UDP."""
    rx_bytes: int = 0
    rx_rate_kbps: float = 0.0
    packet_count: int = 0
    error_count: int = 0
    latency_ms: float = 0.0
    uptime_seconds: float = 0.0
    is_connected: bool = False
    is_receiving_data: bool = False
    conn_type: str = "UDP"          # "UDP" or "SERIAL" or "SIMULATOR"
    target_info: str = ""           # "192.168.1.51:5000" or "COM10 @ 115200"
    port_name: str = ""
    baud_rate: int = 115200


# For backwards compatibility with existing imports
SerialStats = ConnectionStats

