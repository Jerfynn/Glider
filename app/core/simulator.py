"""
Realistic Underwater Glider / ROV Physics and Telemetry Simulator.
Generates UDP stream in format:
DATA,Timestamp,pwm,pwmstate,temperature,humidity,voltage,current,
pressure,pressure,depth,flow,acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z,no need
"""

import math
import time
from app.core.telemetry_model import TelemetryPacket


class GliderSimulator:
    """
    Simulates realistic ocean vehicle telemetry and flight dynamics matching:
    DATA,Timestamp,pwm,pwmstate,temperature,humidity,voltage,current,
    pressure,pressure,depth,flow,acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z,no need
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.phase = "DIVE"  # "DIVE", "CLIMB"
        self.depth = 12.5
        self.target_max_depth = 60.0
        self.target_min_depth = 1.0
        self.speed = 1.35
        self.base_heading = 184.7
        self.sim_time = 0.0
        self.start_ticks = int(time.time() * 1000)

        # Actuator and Environmental
        self.pwm = 1500
        self.pwmstate = "REV_STOP"
        self.humidity = 72.6
        self.flow = 0.0

        # Battery state (e.g. 5S/6S LiPo nominal ~ 19.07V)
        self.battery_voltage = 19.07
        self.battery_current = -37.88
        self.battery_soc = 85.0
        self.battery_soh = 98.2

    def step(self, dt: float = 0.05) -> TelemetryPacket:
        """Step the vehicle dynamics forward by dt seconds."""
        self.sim_time += dt
        t = self.sim_time
        ticks = self.start_ticks + int(t * 1000)

        # Glide profile state machine
        phase_before_step = self.phase
        if self.phase == "DIVE":
            target_pitch = -4.67 + 2.0 * math.sin(t * 0.8)
            roll = 1.44 + 3.0 * math.sin(t * 0.5)
            self.depth += 0.3 * dt * math.sin(math.radians(-target_pitch)) * self.speed * 10
            if self.depth >= self.target_max_depth:
                self.phase = "CLIMB"
        elif self.phase == "CLIMB":
            target_pitch = 4.67 + 2.0 * math.sin(t * 0.8)
            roll = 1.44 + 2.5 * math.sin(t * 0.6 + 1.0)
            self.depth -= 0.3 * dt * math.sin(math.radians(target_pitch)) * self.speed * 10
            if self.depth <= self.target_min_depth:
                self.depth = self.target_min_depth
                self.phase = "DIVE"
        else:
            target_pitch = 0.0
            roll = 0.0

        # Simulate the propulsion command used by the analytics state machine:
        # PWM above neutral is dive-in; below neutral is dive-out.
        if self.phase != phase_before_step:
            self.pwm = 1500
            self.pwmstate = "STOP"
        elif self.phase == "DIVE":
            self.pwm = 1600
            self.pwmstate = "FWD_RUN"
        else:
            self.pwm = 1400
            self.pwmstate = "REV_RUN"

        # Dynamics smoothing
        pitch = target_pitch + 0.8 * math.sin(t * 2.0)
        yaw = -0.20 + 1.2 * math.sin(t * 0.2)

        # IMU Accelerometer simulation (1g normal on Z-axis, plus small motion dynamics)
        acc_x = -0.172 + 0.05 * math.sin(t * 1.5)
        acc_y = 0.066 + 0.04 * math.cos(t * 1.3)
        acc_z = 1.056 + 0.08 * math.sin(t * 2.2)

        # Temperature & Humidity
        temp = 31.30 + 0.2 * math.sin(t * 0.1)
        prev_depth = self.depth - (0.3 * dt * math.sin(math.radians(-target_pitch)) * self.speed * 10)
        curr_depth = self.depth
        delta_depth = curr_depth - prev_depth

        # Battery simulation (nominal 24V 6S pack)
        voltage = 24.20 - (t * 0.001)
        current = -8.45 + 1.2 * math.sin(t * 1.8)

        # Pressure calculations (Sensors 1 & 2)
        pressure_bar_1 = 1.0056 + (curr_depth / 10.0)
        pressure_psi_1 = pressure_bar_1 * 14.5038
        pressure_bar_2 = pressure_bar_1

        motor_mode = "MANUAL" if self.sim_time < 5.0 else "AUTO"
        motor_state = self.pwmstate if hasattr(self, 'pwmstate') else "MANUAL_STOP"

        # Raw string matching exact 24-parameter format:
        # timestamp, mode, motor pwm, motor state, acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, roll, pitch, yaw,
        # BMP pressure bar, BMP pressure psi, MS5837 pressure bar, current depth, previous depth, change in depth,
        # temperature, humidity, current, voltage, flow
        raw_str = (
            f"{ticks},{motor_mode},{self.pwm},{motor_state},{acc_x:.2f},{acc_y:.2f},{acc_z:.2f},"
            f"0.00,0.00,0.00,{roll:.2f},{pitch:.2f},{yaw:.2f},"
            f"{pressure_bar_1:.4f},{pressure_psi_1:.2f},{pressure_bar_2:.4f},"
            f"{curr_depth:.2f},{prev_depth:.2f},{delta_depth:+.2f},"
            f"{temp:.2f},{self.humidity:.1f},{current:.2f},{voltage:.2f},{self.flow:.2f}"
        )

        packet = TelemetryPacket(
            timestamp=time.time(),
            raw_timestamp=ticks,
            motor_mode=motor_mode,
            pwm=self.pwm,
            pwmstate=motor_state,
            acc_x=round(acc_x, 2),
            acc_y=round(acc_y, 2),
            acc_z=round(acc_z, 2),
            gyro_x=0.0,
            gyro_y=0.0,
            gyro_z=0.0,
            roll=round(roll, 2),
            pitch=round(pitch, 2),
            yaw=round(yaw, 2),
            pressure=round(pressure_bar_1, 4),
            pressure_valid=True,
            pressure_psi=round(pressure_psi_1, 2),
            pressure_psi_valid=True,
            pressure_2=round(pressure_bar_2, 4),
            pressure_2_valid=True,
            depth=round(self.target_max_depth, 2),
            depth_valid=True,
            prev_depth=round(prev_depth, 2),
            prev_depth_valid=True,
            curr_depth=round(curr_depth, 2),
            curr_depth_valid=True,
            delta_depth=round(delta_depth, 2),
            delta_depth_valid=True,
            altitude=round(curr_depth, 2),
            altitude_valid=True,
            temperature=round(temp, 2),
            temperature_valid=True,
            temperature_2=round(temp, 2),
            temperature_2_valid=True,
            humidity=round(self.humidity, 1),
            battery_current=round(current, 2),
            battery_voltage=round(voltage, 2),
            battery_soc=round(max(0.0, min(100.0, (voltage - 20.0) / (25.2 - 20.0) * 100.0)), 1),
            flow=round(self.flow, 2),
            raw_text=raw_str,
            is_valid=True
        )

        return packet
