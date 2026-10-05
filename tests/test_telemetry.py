"""
Unit Tests for Telemetry Parser, Data Model, and Glider Simulator.
Testing UDP format and legacy formats.
"""

import unittest
from app.core.parser import TelemetryParser
from app.core.simulator import GliderSimulator


class TestGliderTelemetry(unittest.TestCase):

    def setUp(self):
        self.parser = TelemetryParser()
        self.simulator = GliderSimulator()

    def test_udp_data_parser_with_invalid_tokens(self):
        # Format: DATA,Timestamp,pwm,pwmstate,temperature,humidity,voltage,current,pressure,pressure,depth,flow,acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z,no need
        line = "DATA,319761,1500,REV_STOP,31.30,72.60,19.07,-37.88,INVALID,INVALID,INVALID,0.00,-0.172,0.066,1.056,1.44,-4.67,-0.20,51.07"
        packet = self.parser.parse_line(line)
        self.assertIsNotNone(packet)
        self.assertTrue(packet.is_valid)
        self.assertEqual(packet.raw_timestamp, 319761)
        self.assertEqual(packet.pwm, 1500)
        self.assertEqual(packet.pwmstate, "REV_STOP")
        self.assertAlmostEqual(packet.temperature, 31.30, places=2)
        self.assertAlmostEqual(packet.humidity, 72.60, places=2)
        self.assertAlmostEqual(packet.battery_voltage, 19.07, places=2)
        self.assertAlmostEqual(packet.battery_current, -37.88, places=2)
        self.assertFalse(packet.pressure_valid)
        self.assertFalse(packet.depth_valid)
        self.assertAlmostEqual(packet.flow, 0.00, places=2)
        self.assertAlmostEqual(packet.acc_x, -0.172, places=3)
        self.assertAlmostEqual(packet.acc_y, 0.066, places=3)
        self.assertAlmostEqual(packet.acc_z, 1.056, places=3)
        self.assertAlmostEqual(packet.roll, 1.44, places=2)
        self.assertAlmostEqual(packet.pitch, -4.67, places=2)
        self.assertAlmostEqual(packet.gyro_z, -0.20, places=2)
        self.assertAlmostEqual(packet.yaw, 359.80, places=2)
        self.assertAlmostEqual(packet.extra_val, 51.07, places=2)

    def test_new_19_parameter_format(self):
        # Format: motor pwm, motor state, acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, roll, pitch, yaw, pressure, temperature, altitude, temperature, humidity, current, voltage, flow
        line = "1530,FWD_RUN,-0.115,-0.009,1.057,-0.27,-1.66,-0.21,1.44,-4.67,359.80,1.013,30.20,12.50,28.50,74.90,-37.88,18.37,0.00"
        packet = self.parser.parse_line(line)
        self.assertIsNotNone(packet)
        self.assertTrue(packet.is_valid)
        self.assertEqual(packet.pwm, 1530)
        self.assertEqual(packet.pwmstate, "FWD_RUN")
        self.assertAlmostEqual(packet.acc_x, -0.115, places=3)
        self.assertAlmostEqual(packet.acc_y, -0.009, places=3)
        self.assertAlmostEqual(packet.acc_z, 1.057, places=3)
        self.assertAlmostEqual(packet.gyro_x, -0.27, places=2)
        self.assertAlmostEqual(packet.gyro_y, -1.66, places=2)
        self.assertAlmostEqual(packet.gyro_z, -0.21, places=2)
        self.assertAlmostEqual(packet.roll, 1.44, places=2)
        self.assertAlmostEqual(packet.pitch, -4.67, places=2)
        self.assertAlmostEqual(packet.yaw, 359.80, places=2)
        self.assertAlmostEqual(packet.pressure, 1.013, places=3)
        self.assertTrue(packet.pressure_valid)
        self.assertAlmostEqual(packet.temperature, 30.20, places=2)
        self.assertTrue(packet.temperature_valid)
        self.assertAlmostEqual(packet.altitude, 12.50, places=2)
        self.assertTrue(packet.altitude_valid)
        self.assertAlmostEqual(packet.temperature_2, 28.50, places=2)
        self.assertTrue(packet.temperature_2_valid)
        self.assertAlmostEqual(packet.humidity, 74.90, places=2)
        self.assertAlmostEqual(packet.battery_current, -37.88, places=2)
        self.assertAlmostEqual(packet.battery_voltage, 18.37, places=2)
        self.assertAlmostEqual(packet.flow, 0.00, places=2)

    def test_new_19_parameter_format_with_data_prefix(self):
        line = "DATA,1530,FWD_RUN,-0.115,-0.009,1.057,-0.27,-1.66,-0.21,1.44,-4.67,359.80,1.013,30.20,12.50,28.50,74.90,-37.88,18.37,0.00"
        packet = self.parser.parse_line(line)
        self.assertIsNotNone(packet)
        self.assertTrue(packet.is_valid)
        self.assertEqual(packet.pwm, 1530)
        self.assertEqual(packet.pwmstate, "FWD_RUN")
        self.assertAlmostEqual(packet.roll, 1.44, places=2)
        self.assertAlmostEqual(packet.pitch, -4.67, places=2)
        self.assertAlmostEqual(packet.yaw, 359.80, places=2)
        self.assertAlmostEqual(packet.battery_voltage, 18.37, places=2)

    def test_user_real_telemetry_stream(self):
        # Format: timestamp, motor pwm, motor state, acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, roll, pitch, yaw, pressure, temperature, altitude, temperature, humidity, current, voltage, flow
        line = "79063,1300,REVERSE_HOLD,-0.92,-0.39,9.46,2.11,0.00,0.00,-0.29,0.37,-7.58,0.9932,14.41,31.80,74.10,-9.78,13.15,0.00"
        packet = self.parser.parse_line(line)
        self.assertIsNotNone(packet)
        self.assertTrue(packet.is_valid)
        self.assertEqual(packet.raw_timestamp, 79063)
        self.assertEqual(packet.pwm, 1300)
        self.assertEqual(packet.pwmstate, "REVERSE_HOLD")
        self.assertAlmostEqual(packet.acc_x, -0.92, places=2)
        self.assertAlmostEqual(packet.acc_y, -0.39, places=2)
        self.assertAlmostEqual(packet.acc_z, 9.46, places=2)
        self.assertAlmostEqual(packet.gyro_x, 2.11, places=2)
        self.assertAlmostEqual(packet.gyro_y, 0.00, places=2)
        self.assertAlmostEqual(packet.gyro_z, 0.00, places=2)
        self.assertAlmostEqual(packet.roll, -0.29, places=2)
        self.assertAlmostEqual(packet.pitch, 0.37, places=2)
        self.assertAlmostEqual(packet.yaw, -7.58, places=2)
        self.assertAlmostEqual(packet.pressure, 0.9932, places=4)
        self.assertTrue(packet.pressure_valid)
        self.assertAlmostEqual(packet.temperature, 14.41, places=2)
        self.assertAlmostEqual(packet.temperature_2, 31.80, places=2)
        self.assertAlmostEqual(packet.humidity, 74.10, places=2)
        self.assertAlmostEqual(packet.battery_current, -9.78, places=2)
        self.assertAlmostEqual(packet.battery_voltage, 13.15, places=2)
        self.assertAlmostEqual(packet.flow, 0.00, places=2)

    def test_user_teensy_packet(self):
        line = "DATA,141329,1522,FWD_ACCEL,30.20,75.00,18.20,-37.88,INVALID,INVALID,INVALID,0.00,-0.120,-0.000,1.063,-0.70,-1.71,-0.38,50.27"
        packet = self.parser.parse_line(line)
        self.assertIsNotNone(packet)
        self.assertTrue(packet.is_valid)
        self.assertEqual(packet.raw_timestamp, 141329)
        self.assertEqual(packet.pwm, 1522)
        self.assertEqual(packet.pwmstate, "FWD_ACCEL")
        self.assertAlmostEqual(packet.temperature, 30.20, places=2)
        self.assertAlmostEqual(packet.humidity, 75.00, places=2)
        self.assertAlmostEqual(packet.battery_voltage, 18.20, places=2)
        self.assertAlmostEqual(packet.battery_current, -37.88, places=2)
        self.assertFalse(packet.pressure_valid)
        self.assertFalse(packet.depth_valid)
        self.assertAlmostEqual(packet.acc_x, -0.120, places=3)
        self.assertAlmostEqual(packet.acc_y, -0.000, places=3)
        self.assertAlmostEqual(packet.acc_z, 1.063, places=3)
        self.assertAlmostEqual(packet.roll, -0.70, places=2)
        self.assertAlmostEqual(packet.pitch, -1.71, places=2)
        self.assertAlmostEqual(packet.gyro_z, -0.38, places=2)
        self.assertAlmostEqual(packet.yaw, 359.62, places=2)
        self.assertAlmostEqual(packet.extra_val, 50.27, places=2)

    def test_csv_parser_10_fields(self):
        # Format: roll,pitch,yaw,depth,temperature,pressure,battery_voltage,battery_current,battery_soc,battery_soh
        line = "12.42,-5.21,184.73,42.7,18.4,5.18,14.82,1.25,85.0,98.2"
        packet = self.parser.parse_line(line)
        self.assertIsNotNone(packet)
        self.assertTrue(packet.is_valid)
        self.assertAlmostEqual(packet.roll, 12.42, places=2)
        self.assertAlmostEqual(packet.pitch, -5.21, places=2)
        self.assertAlmostEqual(packet.yaw, 184.73, places=2)
        self.assertAlmostEqual(packet.depth, 42.7, places=1)
        self.assertAlmostEqual(packet.temperature, 18.4, places=1)
        self.assertAlmostEqual(packet.pressure, 5.18, places=2)
        self.assertAlmostEqual(packet.battery_voltage, 14.82, places=2)
        self.assertAlmostEqual(packet.battery_current, 1.25, places=2)
        self.assertAlmostEqual(packet.battery_soc, 85.0, places=1)
        self.assertAlmostEqual(packet.battery_soh, 98.2, places=1)

    def test_json_parser(self):
        line = '{"roll": 10.5, "pitch": -4.2, "yaw": 180.0, "depth": 30.0, "temp": 19.1, "pressure": 4.01, "voltage": 14.7, "current": 1.1, "soc": 80.0, "soh": 99.0}'
        packet = self.parser.parse_line(line)
        self.assertIsNotNone(packet)
        self.assertTrue(packet.is_valid)
        self.assertAlmostEqual(packet.roll, 10.5, places=2)
        self.assertAlmostEqual(packet.pitch, -4.2, places=2)
        self.assertAlmostEqual(packet.yaw, 180.0, places=2)
        self.assertAlmostEqual(packet.battery_voltage, 14.7, places=1)
        self.assertAlmostEqual(packet.battery_current, 1.1, places=1)
        self.assertAlmostEqual(packet.battery_soc, 80.0, places=1)
        self.assertAlmostEqual(packet.battery_soh, 99.0, places=1)

    def test_key_value_parser(self):
        line = "R:15.2,P:-8.3,Y:190.5,D:55.2,T:16.8,PR:6.5,BV:14.6,BC:1.3,SOC:78.5,SOH:97.0"
        packet = self.parser.parse_line(line)
        self.assertIsNotNone(packet)
        self.assertTrue(packet.is_valid)
        self.assertAlmostEqual(packet.roll, 15.2, places=2)
        self.assertAlmostEqual(packet.pitch, -8.3, places=2)
        self.assertAlmostEqual(packet.yaw, 190.5, places=2)
        self.assertAlmostEqual(packet.depth, 55.2, places=1)
        self.assertAlmostEqual(packet.battery_voltage, 14.6, places=1)
        self.assertAlmostEqual(packet.battery_current, 1.3, places=1)
        self.assertAlmostEqual(packet.battery_soc, 78.5, places=1)
        self.assertAlmostEqual(packet.battery_soh, 97.0, places=1)

    def test_depth_viewer_cycle_count(self):
        def compute_cycle_count(elapsed: float) -> int:
            if elapsed < (11.0 + 58.5):
                return 0
            return int((elapsed - 11.0) / 58.5)

        self.assertEqual(compute_cycle_count(0.0), 0)
        self.assertEqual(compute_cycle_count(10.9), 0)
        self.assertEqual(compute_cycle_count(11.0), 0)
        self.assertEqual(compute_cycle_count(69.4), 0)
        self.assertEqual(compute_cycle_count(69.5), 1)
        self.assertEqual(compute_cycle_count(127.9), 1)
        self.assertEqual(compute_cycle_count(128.0), 2)
        self.assertEqual(compute_cycle_count(186.4), 2)
        self.assertEqual(compute_cycle_count(186.5), 3)


if __name__ == "__main__":
    unittest.main()

