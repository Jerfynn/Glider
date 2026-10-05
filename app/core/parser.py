"""
Robust Telemetry Parser for Underwater Glider Serial and UDP data streams.
Supports:
1. UDP 19-parameter stream:
   DATA,Timestamp,pwm,pwmstate,temperature,humidity,voltage,current,
   pressure,pressure,depth,flow,acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z,no need
2. Standard CSV stream:
   roll,pitch,yaw,depth,temperature,pressure,battery_voltage,battery_current,battery_soc,battery_soh
3. JSON format
4. Key-Value format
"""

import json
import time
from typing import Optional
from app.core.telemetry_model import TelemetryPacket


def _safe_float(val: str, default: float = 0.0) -> tuple[float, bool]:
    """Safely converts string to float, returning (value, is_valid)."""
    if not val:
        return default, False
    v_clean = val.strip().upper()
    if v_clean in ("INVALID", "ERR", "ERROR", "NAN", "NULL", "NONE", "--"):
        return default, False
    try:
        return float(v_clean), True
    except ValueError:
        return default, False


def _safe_int(val: str, default: int = 0) -> int:
    """Safely converts string to int."""
    try:
        return int(float(val.strip()))
    except (ValueError, TypeError):
        return default


def _is_numeric(val: str) -> bool:
    """Helper to test if a string represents a valid float or int."""
    if not val:
        return False
    try:
        float(val.strip())
        return True
    except (ValueError, TypeError):
        return False


class TelemetryParser:
    """Parses raw UDP / TCP / Serial strings into structured TelemetryPacket objects."""

    def __init__(self):
        self.last_valid_packet: Optional[TelemetryPacket] = None

    def parse_line(self, line: str) -> Optional[TelemetryPacket]:
        """Parses a single line received from TCP, UDP, serial, or simulator."""
        line = line.strip()
        if not line:
            return None

        packet = TelemetryPacket(timestamp=time.time(), raw_text=line)

        try:
            # 1. Check for stream starting with "DATA," or containing 15+ comma-separated values
            if line.startswith("DATA,") or line.startswith("data,"):
                return self._parse_stream_data(line, packet)

            # 2. Check for JSON format
            if line.startswith("{") and line.endswith("}"):
                return self._parse_json(line, packet)

            # 3. Check for Key-Value format (e.g. R:12.4,P:-5.2,Y:184.7...)
            if ":" in line and ("," in line or ";" in line or " " in line):
                return self._parse_key_value(line, packet)

            # 4. Comma-separated format
            parts = [p.strip() for p in line.split(",") if p.strip()]
            if len(parts) >= 15:
                return self._parse_stream_data(line, packet)

            return self._parse_csv(line, packet)

        except Exception as ex:
            packet.is_valid = False
            packet.error_msg = str(ex)
            return packet

    def _parse_stream_data(self, line: str, packet: TelemetryPacket) -> TelemetryPacket:
        """
        Parses telemetry streams in 23, 19, or 18 parameter formats.
        Format 1 (23 parameters):
        motor mode, motor pwm, motor state, acc_X, acc_y, acc_z, gyro_x, gyro_y, gyro_z,
        roll, pitch, yaw, pressure bar, pressure psi, pressure bar (2), depth,
        previous depth, current depth, change in depth, temperature, humidity, current, voltage
        """
        parts = [p.strip() for p in line.split(",")]
        
        # Strip optional "DATA" prefix
        if parts and parts[0].upper() == "DATA":
            tokens = parts[1:]
        else:
            tokens = parts

        if len(tokens) < 10:
            packet.is_valid = False
            packet.error_msg = f"Insufficient fields in stream ({len(tokens)} items)"
            return packet

        # 1. Check for 24 parameter format (with timestamp, mode, pwm, ..., flow)
        # or 23 parameter format (mode, pwm, ..., flow)
        if len(tokens) >= 24 and _is_numeric(tokens[0]) and float(tokens[0]) > 10000.0:
            # 24-field format with leading timestamp
            packet.raw_timestamp = _safe_int(tokens[0])
            return self._parse_24_parameter_format(tokens, packet)
        elif len(tokens) >= 24:
            return self._parse_24_parameter_format(tokens, packet)
        elif len(tokens) >= 22:
            return self._parse_24_parameter_format(tokens, packet)

        # 2. Check for legacy / 19 / 18 formats
        if len(tokens) >= 3 and not _is_numeric(tokens[2]):
            f3, _ = _safe_float(tokens[3])
            f4, _ = _safe_float(tokens[4])
            f5, _ = _safe_float(tokens[5])
            if f4 > 25.0 and f3 > 15.0 and f5 > 10.0:
                return self._parse_legacy_format(tokens, packet)
            else:
                return self._parse_with_timestamp_format(tokens, packet)

        if len(tokens) >= 2 and not _is_numeric(tokens[1]):
            return self._parse_without_timestamp_format(tokens, packet)

        if len(tokens) >= 19:
            return self._parse_with_timestamp_format(tokens, packet)
        elif len(tokens) >= 18:
            return self._parse_without_timestamp_format(tokens, packet)
        else:
            return self._parse_legacy_format(tokens, packet)

    def _parse_24_parameter_format(self, tokens: list[str], packet: TelemetryPacket) -> TelemetryPacket:
        """
        Parses telemetry stream in either:
        A) 24 parameters with leading timestamp:
           0: timestamp
           1: mode
           2: motor pwm
           3: motor state
           4: acc_x
           5: acc_y
           6: acc_z
           7: gyro_x
           8: gyro_y
           9: gyro_z
           10: roll
           11: pitch
           12: yaw
           13: BMP pressure bar (Internal pressure in bar)
           14: BMP pressure psi (Internal pressure in psi)
           15: MS5837 pressure bar (External hydrostatic pressure in bar)
           16: current depth
           17: previous depth
           18: change in depth
           19: temperature
           20: humidity
           21: current
           22: voltage
           23: flow

        B) 23 parameters without leading timestamp (offset by -1, flow at end or legacy 23-param format)
        """
        # Determine if tokens[0] is timestamp or mode
        if len(tokens) >= 24 or (_is_numeric(tokens[0]) and len(tokens) >= 23 and not any(c in tokens[0].upper() for c in ("MANUAL", "AUTO"))):
            # Leading timestamp present
            packet.raw_timestamp = _safe_int(tokens[0])
            t_mode = tokens[1] if len(tokens) > 1 else "MANUAL"
            t_pwm = tokens[2] if len(tokens) > 2 else "1500"
            t_pwmstate = tokens[3] if len(tokens) > 3 else "STOP"
            t_acc_x = tokens[4] if len(tokens) > 4 else "0.0"
            t_acc_y = tokens[5] if len(tokens) > 5 else "0.0"
            t_acc_z = tokens[6] if len(tokens) > 6 else "1.0"
            t_gyro_x = tokens[7] if len(tokens) > 7 else "0.0"
            t_gyro_y = tokens[8] if len(tokens) > 8 else "0.0"
            t_gyro_z = tokens[9] if len(tokens) > 9 else "0.0"
            t_roll = tokens[10] if len(tokens) > 10 else "0.0"
            t_pitch = tokens[11] if len(tokens) > 11 else "0.0"
            t_yaw = tokens[12] if len(tokens) > 12 else "0.0"
            t_bmp_bar = tokens[13] if len(tokens) > 13 else "0.0"
            t_bmp_psi = tokens[14] if len(tokens) > 14 else "0.0"
            t_ms_bar = tokens[15] if len(tokens) > 15 else "0.0"
            t_curr_depth = tokens[16] if len(tokens) > 16 else "0.0"
            t_prev_depth = tokens[17] if len(tokens) > 17 else "0.0"
            t_delta_depth = tokens[18] if len(tokens) > 18 else "0.0"
            t_temp = tokens[19] if len(tokens) > 19 else "0.0"
            t_humidity = tokens[20] if len(tokens) > 20 else "0.0"
            t_current = tokens[21] if len(tokens) > 21 else "0.0"
            t_voltage = tokens[22] if len(tokens) > 22 else "0.0"
            t_flow = tokens[23] if len(tokens) > 23 else "0.0"
        else:
            # 23-parameter sequence starting directly with mode
            t_mode = tokens[0] if len(tokens) > 0 else "MANUAL"
            t_pwm = tokens[1] if len(tokens) > 1 else "1500"
            t_pwmstate = tokens[2] if len(tokens) > 2 else "STOP"
            t_acc_x = tokens[3] if len(tokens) > 3 else "0.0"
            t_acc_y = tokens[4] if len(tokens) > 4 else "0.0"
            t_acc_z = tokens[5] if len(tokens) > 5 else "1.0"
            t_gyro_x = tokens[6] if len(tokens) > 6 else "0.0"
            t_gyro_y = tokens[7] if len(tokens) > 7 else "0.0"
            t_gyro_z = tokens[8] if len(tokens) > 8 else "0.0"
            t_roll = tokens[9] if len(tokens) > 9 else "0.0"
            t_pitch = tokens[10] if len(tokens) > 10 else "0.0"
            t_yaw = tokens[11] if len(tokens) > 11 else "0.0"
            t_bmp_bar = tokens[12] if len(tokens) > 12 else "0.0"
            t_bmp_psi = tokens[13] if len(tokens) > 13 else "0.0"
            t_ms_bar = tokens[14] if len(tokens) > 14 else "0.0"
            t_curr_depth = tokens[15] if len(tokens) > 15 else "0.0"
            t_prev_depth = tokens[16] if len(tokens) > 16 else "0.0"
            t_delta_depth = tokens[17] if len(tokens) > 17 else "0.0"
            t_temp = tokens[18] if len(tokens) > 18 else "0.0"
            t_humidity = tokens[19] if len(tokens) > 19 else "0.0"
            t_current = tokens[20] if len(tokens) > 20 else "0.0"
            t_voltage = tokens[21] if len(tokens) > 21 else "0.0"
            t_flow = tokens[22] if len(tokens) > 22 else "0.0"

        # Mode
        raw_mode = t_mode.strip().upper()
        if raw_mode in ("0", "MANUAL"):
            packet.motor_mode = "MANUAL (0)"
        elif raw_mode in ("1", "TIMING", "AUTO_TIMING"):
            packet.motor_mode = "AUTO: TIMING (1)"
        elif raw_mode in ("2", "DEPTH", "AUTO_DEPTH"):
            packet.motor_mode = "AUTO: DEPTH (2)"
        else:
            packet.motor_mode = raw_mode

        # Motor PWM & State
        packet.pwm = _safe_int(t_pwm, default=1500)
        packet.pwmstate = t_pwmstate.strip() or "STOP"

        # Accelerometer (g)
        packet.acc_x, _ = _safe_float(t_acc_x)
        packet.acc_y, _ = _safe_float(t_acc_y)
        packet.acc_z, _ = _safe_float(t_acc_z, default=1.0)

        # Gyroscope (°/s)
        packet.gyro_x, _ = _safe_float(t_gyro_x)
        packet.gyro_y, _ = _safe_float(t_gyro_y)
        packet.gyro_z, _ = _safe_float(t_gyro_z)

        # Attitude (° roll, pitch, yaw)
        packet.roll, _ = _safe_float(t_roll)
        packet.pitch, _ = _safe_float(t_pitch)
        packet.yaw, _ = _safe_float(t_yaw)

        # BMP Internal Pressure (bar & psi)
        p1_val, p1_ok = _safe_float(t_bmp_bar)
        packet.pressure = p1_val
        packet.pressure_valid = p1_ok

        psi_val, psi_ok = _safe_float(t_bmp_psi)
        packet.pressure_psi = psi_val
        packet.pressure_psi_valid = psi_ok

        # MS5837 External Hydrostatic Pressure (bar)
        p2_val, p2_ok = _safe_float(t_ms_bar)
        packet.pressure_2 = p2_val
        packet.pressure_2_valid = p2_ok

        # Depths: current depth, previous depth, change in depth
        cd_val, cd_ok = _safe_float(t_curr_depth)
        packet.curr_depth = cd_val
        packet.curr_depth_valid = cd_ok
        packet.depth = cd_val
        packet.depth_valid = cd_ok
        packet.altitude = cd_val
        packet.altitude_valid = cd_ok

        pd_val, pd_ok = _safe_float(t_prev_depth)
        packet.prev_depth = pd_val
        packet.prev_depth_valid = pd_ok

        dd_val, dd_ok = _safe_float(t_delta_depth)
        packet.delta_depth = dd_val
        packet.delta_depth_valid = dd_ok

        # Temperature (°C)
        t_val, t_ok = _safe_float(t_temp)
        packet.temperature = t_val
        packet.temperature_valid = t_ok
        packet.temperature_2 = t_val
        packet.temperature_2_valid = t_ok

        # Humidity (%)
        packet.humidity, _ = _safe_float(t_humidity)

        # Current (A)
        packet.battery_current, _ = _safe_float(t_current)

        # Voltage (V)
        volt_val, _ = _safe_float(t_voltage)
        packet.battery_voltage = volt_val
        if volt_val > 0.0:
            packet.battery_soc = max(0.0, min(100.0, round((volt_val - 20.0) / (25.2 - 20.0) * 100.0, 1)))

        # Flow (L/min)
        packet.flow, _ = _safe_float(t_flow)

        packet.is_valid = True
        self.last_valid_packet = packet
        return packet

    def _parse_23_parameter_format(self, tokens: list[str], packet: TelemetryPacket) -> TelemetryPacket:
        return self._parse_24_parameter_format(tokens, packet)

    def _parse_with_timestamp_format(self, tokens: list[str], packet: TelemetryPacket) -> TelemetryPacket:
        """
        Exact Stream Format with timestamp (19 parameters):
        0: timestamp (ms)
        1: motor pwm
        2: motor state
        3: acc_x
        4: acc_y
        5: acc_z
        6: gyro_x
        7: gyro_y
        8: gyro_z
        9: roll
        10: pitch
        11: yaw
        12: pressure (bar)
        13: pressure (psi)
        14: temperature (°C)
        15: humidity (%)
        16: current (A)
        17: voltage (V)
        18: flow (L/min)
        """
        packet.raw_timestamp = _safe_int(tokens[0])
        packet.pwm = _safe_int(tokens[1], default=1500)
        packet.pwmstate = tokens[2].strip() if len(tokens) > 2 else "STOP"
        
        acc_x, _ = _safe_float(tokens[3]) if len(tokens) > 3 else (0.0, False)
        packet.acc_x = acc_x
        
        acc_y, _ = _safe_float(tokens[4]) if len(tokens) > 4 else (0.0, False)
        packet.acc_y = acc_y
        
        acc_z, _ = _safe_float(tokens[5], default=1.0) if len(tokens) > 5 else (1.0, False)
        packet.acc_z = acc_z
        
        gyro_x, _ = _safe_float(tokens[6]) if len(tokens) > 6 else (0.0, False)
        packet.gyro_x = gyro_x
        
        gyro_y, _ = _safe_float(tokens[7]) if len(tokens) > 7 else (0.0, False)
        packet.gyro_y = gyro_y
        
        gyro_z, _ = _safe_float(tokens[8]) if len(tokens) > 8 else (0.0, False)
        packet.gyro_z = gyro_z
        
        roll_val, _ = _safe_float(tokens[9]) if len(tokens) > 9 else (gyro_x, False)
        packet.roll = roll_val
        
        pitch_val, _ = _safe_float(tokens[10]) if len(tokens) > 10 else (gyro_y, False)
        packet.pitch = pitch_val
        
        if len(tokens) > 11:
            yaw_val, _ = _safe_float(tokens[11])
            packet.yaw = yaw_val
        else:
            packet.yaw = gyro_z
            
        # 12: pressure (bar)
        if len(tokens) > 12:
            p_val, p_ok = _safe_float(tokens[12])
            packet.pressure = p_val
            packet.pressure_valid = p_ok
            # Compute depth from bar (1 bar ~ 10m water column above atmospheric pressure 1.013 bar)
            if p_ok and p_val > 0.0:
                calc_depth = max(0.0, (p_val - 1.01325) * 10.0)
                packet.depth = round(calc_depth, 2)
                packet.depth_valid = True
                packet.altitude = packet.depth
                packet.altitude_valid = True
            
        # 13: pressure (psi)
        if len(tokens) > 13:
            p_psi_val, p_psi_ok = _safe_float(tokens[13])
            packet.pressure_psi = p_psi_val
            packet.pressure_2 = p_psi_val
            packet.pressure_2_valid = p_psi_ok
            
        # 14: temperature (°C)
        if len(tokens) > 14:
            t_val, t_ok = _safe_float(tokens[14])
            packet.temperature = t_val
            packet.temperature_valid = t_ok
            packet.temperature_2 = t_val
            packet.temperature_2_valid = t_ok
            
        # 15: humidity (%)
        if len(tokens) > 15:
            hum_val, _ = _safe_float(tokens[15])
            packet.humidity = hum_val
            
        # 16: current (A)
        if len(tokens) > 16:
            curr_val, _ = _safe_float(tokens[16])
            packet.battery_current = curr_val
            
        # 17: voltage (V)
        if len(tokens) > 17:
            volt_val, _ = _safe_float(tokens[17])
            packet.battery_voltage = volt_val
            if volt_val > 0.0:
                # Estimate SOC for 3S/4S pack
                if volt_val >= 13.0:
                    soc = (volt_val - 12.0) / (16.8 - 12.0) * 100.0
                else:
                    soc = (volt_val - 10.0) / (12.6 - 10.0) * 100.0
                packet.battery_soc = max(0.0, min(100.0, round(soc, 1)))
            
        # 18: flow (L/min)
        if len(tokens) > 18:
            flow_val, _ = _safe_float(tokens[18])
            packet.flow = flow_val

        packet.is_valid = True
        self.last_valid_packet = packet
        return packet

    def _parse_without_timestamp_format(self, tokens: list[str], packet: TelemetryPacket) -> TelemetryPacket:
        """
        Exact Stream Format without timestamp (18 parameters starting with motor pwm):
        0: motor pwm
        1: motor state
        2: acc_x
        3: acc_y
        4: acc_z
        5: gyro_x
        6: gyro_y
        7: gyro_z
        8: roll
        9: pitch
        10: yaw
        11: pressure (bar)
        12: pressure (psi)
        13: temperature (°C)
        14: humidity (%)
        15: current (A)
        16: voltage (V)
        17: flow (L/min)
        """
        packet.pwm = _safe_int(tokens[0], default=1500)
        packet.pwmstate = tokens[1].strip() if len(tokens) > 1 else "STOP"
        
        acc_x, _ = _safe_float(tokens[2]) if len(tokens) > 2 else (0.0, False)
        packet.acc_x = acc_x
        
        acc_y, _ = _safe_float(tokens[3]) if len(tokens) > 3 else (0.0, False)
        packet.acc_y = acc_y
        
        acc_z, _ = _safe_float(tokens[4], default=1.0) if len(tokens) > 4 else (1.0, False)
        packet.acc_z = acc_z
        
        gyro_x, _ = _safe_float(tokens[5]) if len(tokens) > 5 else (0.0, False)
        packet.gyro_x = gyro_x
        
        gyro_y, _ = _safe_float(tokens[6]) if len(tokens) > 6 else (0.0, False)
        packet.gyro_y = gyro_y
        
        gyro_z, _ = _safe_float(tokens[7]) if len(tokens) > 7 else (0.0, False)
        packet.gyro_z = gyro_z
        
        roll_val, _ = _safe_float(tokens[8]) if len(tokens) > 8 else (gyro_x, False)
        packet.roll = roll_val
        
        pitch_val, _ = _safe_float(tokens[9]) if len(tokens) > 9 else (gyro_y, False)
        packet.pitch = pitch_val
        
        if len(tokens) > 10:
            yaw_val, _ = _safe_float(tokens[10])
            packet.yaw = yaw_val
        else:
            packet.yaw = gyro_z
            
        # 11: pressure (bar)
        if len(tokens) > 11:
            p_val, p_ok = _safe_float(tokens[11])
            packet.pressure = p_val
            packet.pressure_valid = p_ok
            if p_ok and p_val > 0.0:
                calc_depth = max(0.0, (p_val - 1.01325) * 10.0)
                packet.depth = round(calc_depth, 2)
                packet.depth_valid = True
                packet.altitude = packet.depth
                packet.altitude_valid = True
            
        # 12: pressure (psi)
        if len(tokens) > 12:
            p_psi_val, p_psi_ok = _safe_float(tokens[12])
            packet.pressure_psi = p_psi_val
            packet.pressure_2 = p_psi_val
            packet.pressure_2_valid = p_psi_ok
            
        # 13: temperature (°C)
        if len(tokens) > 13:
            t_val, t_ok = _safe_float(tokens[13])
            packet.temperature = t_val
            packet.temperature_valid = t_ok
            packet.temperature_2 = t_val
            packet.temperature_2_valid = t_ok
            
        # 14: humidity (%)
        if len(tokens) > 14:
            hum_val, _ = _safe_float(tokens[14])
            packet.humidity = hum_val
            
        # 15: current (A)
        if len(tokens) > 15:
            curr_val, _ = _safe_float(tokens[15])
            packet.battery_current = curr_val
            
        # 16: voltage (V)
        if len(tokens) > 16:
            volt_val, _ = _safe_float(tokens[16])
            packet.battery_voltage = volt_val
            if volt_val > 0.0:
                if volt_val >= 13.0:
                    soc = (volt_val - 12.0) / (16.8 - 12.0) * 100.0
                else:
                    soc = (volt_val - 10.0) / (12.6 - 10.0) * 100.0
                packet.battery_soc = max(0.0, min(100.0, round(soc, 1)))
            
        # 17: flow (L/min)
        if len(tokens) > 17:
            flow_val, _ = _safe_float(tokens[17])
            packet.flow = flow_val

        packet.is_valid = True
        self.last_valid_packet = packet
        return packet

    def _parse_legacy_format(self, tokens: list[str], packet: TelemetryPacket) -> TelemetryPacket:
        """
        Legacy format:
        0: Timestamp, 1: pwm, 2: pwmstate, 3: temp, 4: humidity, 5: voltage, 6: current,
        7: pressure, 8: pressure_2, 9: depth, 10: flow, 11: acc_x, 12: acc_y, 13: acc_z,
        14: gyro_x, 15: gyro_y, 16: gyro_z, 17: extra
        """
        packet.raw_timestamp = _safe_int(tokens[0])
        packet.pwm = _safe_int(tokens[1], default=1500)
        packet.pwmstate = tokens[2].strip() if len(tokens) > 2 else "REV_STOP"
        
        temp_val, temp_ok = _safe_float(tokens[3])
        packet.temperature = temp_val
        packet.temperature_valid = temp_ok
        
        hum_val, _ = _safe_float(tokens[4])
        packet.humidity = hum_val
        
        volt_val, _ = _safe_float(tokens[5])
        packet.battery_voltage = volt_val
        
        curr_val, _ = _safe_float(tokens[6])
        packet.battery_current = curr_val
        
        p1_val, p1_ok = _safe_float(tokens[7])
        packet.pressure = p1_val
        packet.pressure_valid = p1_ok
        
        if len(tokens) > 8:
            p2_val, p2_ok = _safe_float(tokens[8])
            packet.pressure_2 = p2_val
            packet.pressure_2_valid = p2_ok
        
        if len(tokens) > 9:
            depth_val, depth_ok = _safe_float(tokens[9])
            packet.depth = max(0.0, depth_val)
            packet.depth_valid = depth_ok
            packet.altitude = depth_val
            packet.altitude_valid = depth_ok
        
        if len(tokens) > 10:
            flow_val, _ = _safe_float(tokens[10])
            packet.flow = flow_val
        
        if len(tokens) > 11:
            acc_x, _ = _safe_float(tokens[11])
            packet.acc_x = acc_x
        if len(tokens) > 12:
            acc_y, _ = _safe_float(tokens[12])
            packet.acc_y = acc_y
        if len(tokens) > 13:
            acc_z, _ = _safe_float(tokens[13], default=1.0)
            packet.acc_z = acc_z
        
        if len(tokens) > 14:
            gyro_x, _ = _safe_float(tokens[14])
            packet.gyro_x = gyro_x
            packet.roll = gyro_x
        if len(tokens) > 15:
            gyro_y, _ = _safe_float(tokens[15])
            packet.gyro_y = gyro_y
            packet.pitch = gyro_y
        if len(tokens) > 16:
            gyro_z, _ = _safe_float(tokens[16])
            packet.gyro_z = gyro_z
            packet.yaw = gyro_z % 360.0
            
        if len(tokens) > 17:
            ext_val, _ = _safe_float(tokens[17])
            packet.extra_val = ext_val

        packet.is_valid = True
        self.last_valid_packet = packet
        return packet

    def _parse_csv(self, line: str, packet: TelemetryPacket) -> TelemetryPacket:
        parts = [p.strip() for p in line.split(",") if p.strip()]

        if not parts:
            packet.is_valid = False
            packet.error_msg = "Empty payload"
            return packet

        values = []
        for p in parts:
            try:
                values.append(float(p))
            except ValueError:
                pass

        if len(values) < 3:
            packet.is_valid = False
            packet.error_msg = "Insufficient parameters (need at least roll, pitch, yaw)"
            return packet

        # 1. Roll
        packet.roll = values[0]
        packet.gyro_x = values[0]
        # 2. Pitch
        packet.pitch = values[1]
        packet.gyro_y = values[1]
        # 3. Yaw
        packet.yaw = values[2] % 360.0
        packet.gyro_z = values[2]

        # 4. Depth
        if len(values) >= 4:
            packet.depth = max(0.0, values[3])
            packet.depth_valid = True
        # 5. Temperature
        if len(values) >= 5:
            packet.temperature = values[4]
        # 6. Pressure
        if len(values) >= 6:
            packet.pressure = values[5]
            packet.pressure_valid = True
        else:
            packet.pressure = round(1.013 + (packet.depth / 10.0), 2)

        # 7. Battery Voltage
        if len(values) >= 7:
            packet.battery_voltage = values[6]
        else:
            packet.battery_voltage = 19.07

        # 8. Battery Current
        if len(values) >= 8:
            packet.battery_current = values[7]
        else:
            packet.battery_current = -37.88

        # 9. Battery SoC
        if len(values) >= 9:
            packet.battery_soc = min(100.0, max(0.0, values[8]))
        else:
            packet.battery_soc = 85.0

        # 10. Battery SoH
        if len(values) >= 10:
            packet.battery_soh = min(100.0, max(0.0, values[9]))
        else:
            packet.battery_soh = 98.0

        packet.is_valid = True
        self.last_valid_packet = packet
        return packet

    def _parse_json(self, line: str, packet: TelemetryPacket) -> TelemetryPacket:
        data = json.loads(line)
        packet.roll = float(data.get("roll", data.get("r", data.get("gyro_x", 0.0))))
        packet.pitch = float(data.get("pitch", data.get("p", data.get("gyro_y", 0.0))))
        packet.yaw = float(data.get("yaw", data.get("y", data.get("gyro_z", 0.0)))) % 360.0
        packet.depth = float(data.get("depth", data.get("d", 0.0)))
        packet.temperature = float(data.get("temp", data.get("temperature", data.get("t", 31.3))))
        packet.humidity = float(data.get("humidity", data.get("h", 72.6)))
        packet.pressure = float(data.get("pressure", data.get("press", 1.013 + packet.depth / 10.0)))
        packet.battery_voltage = float(data.get("battery_voltage", data.get("voltage", data.get("v", 19.07))))
        packet.battery_current = float(data.get("battery_current", data.get("current", data.get("i", -37.88))))
        packet.pwm = int(data.get("pwm", 1500))
        packet.pwmstate = str(data.get("pwmstate", "REV_STOP"))
        packet.acc_x = float(data.get("acc_x", -0.172))
        packet.acc_y = float(data.get("acc_y", 0.066))
        packet.acc_z = float(data.get("acc_z", 1.056))
        packet.battery_soc = float(data.get("battery_soc", data.get("soc", 85.0)))
        packet.battery_soh = float(data.get("battery_soh", data.get("soh", 98.0)))
        packet.is_valid = True
        self.last_valid_packet = packet
        return packet

    def _parse_key_value(self, line: str, packet: TelemetryPacket) -> TelemetryPacket:
        delims = [",", ";", " "]
        selected_delim = ","
        for d in delims:
            if d in line:
                selected_delim = d
                break

        tokens = line.split(selected_delim)
        for token in tokens:
            if ":" not in token and "=" not in token:
                continue
            sep = ":" if ":" in token else "="
            k, v = token.split(sep, 1)
            k = k.strip().upper()
            try:
                val = float(v.strip())
                if k in ("R", "ROLL", "GYRO_X"):
                    packet.roll = val
                    packet.gyro_x = val
                elif k in ("P", "PITCH", "GYRO_Y"):
                    packet.pitch = val
                    packet.gyro_y = val
                elif k in ("Y", "YAW", "GYRO_Z"):
                    packet.yaw = val % 360.0
                    packet.gyro_z = val
                elif k in ("D", "DEPTH"):
                    packet.depth = max(0.0, val)
                    packet.depth_valid = True
                elif k in ("T", "TEMP", "TEMPERATURE"):
                    packet.temperature = val
                elif k in ("H", "HUM", "HUMIDITY"):
                    packet.humidity = val
                elif k in ("PR", "PRESS", "PRESSURE"):
                    packet.pressure = val
                    packet.pressure_valid = True
                elif k in ("BV", "VOLT", "VOLTAGE", "BAT_V"):
                    packet.battery_voltage = val
                elif k in ("BC", "CURR", "CURRENT", "BAT_I"):
                    packet.battery_current = val
                elif k in ("PWM",):
                    packet.pwm = int(val)
                elif k in ("ACC_X",):
                    packet.acc_x = val
                elif k in ("ACC_Y",):
                    packet.acc_y = val
                elif k in ("ACC_Z",):
                    packet.acc_z = val
                elif k in ("SOC", "BAT_SOC"):
                    packet.battery_soc = val
                elif k in ("SOH", "BAT_SOH"):
                    packet.battery_soh = val
            except ValueError:
                if k in ("PWMSTATE", "STATE"):
                    packet.pwmstate = v.strip()

        packet.is_valid = True
        self.last_valid_packet = packet
        return packet
