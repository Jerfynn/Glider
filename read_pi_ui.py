"""Read Raspberry Pi telemetry and display the values used by GliderView.

The Raspberry Pi should run its telemetry TCP server on port 5000 and send
one telemetry record per line (CSV, JSON, or key/value format supported by
GliderView's TelemetryParser).

Example:
    python read_pi_ui.py --host 192.168.1.91
"""

import argparse
import socket

from app.core.parser import TelemetryParser


def print_packet(packet):
    """Print the parsed telemetry fields displayed by the application."""
    print(
        "Roll: {0:.2f} deg | Pitch: {1:.2f} deg | Yaw: {2:.2f} deg | "
        "Depth: {3:.2f} m | Temperature: {4:.2f} C | Pressure: {5:.2f} bar | "
        "Voltage: {6:.2f} V | Current: {7:.2f} A | SoC: {8:.1f}% | SoH: {9:.1f}%".format(
            packet.roll,
            packet.pitch,
            packet.yaw,
            packet.depth,
            packet.temperature,
            packet.pressure,
            packet.battery_voltage,
            packet.battery_current,
            packet.battery_soc,
            packet.battery_soh,
        )
    )


def read_stream(host, port):
    parser = TelemetryParser()
    buffer = bytearray()

    print("Connecting to Raspberry Pi at {}:{}...".format(host, port))
    with socket.create_connection((host, port), timeout=10) as connection:
        connection.settimeout(None)
        print("Connected. Waiting for telemetry (Ctrl+C to stop).")

        while True:
            chunk = connection.recv(4096)
            if not chunk:
                print("\nRaspberry Pi closed the connection.")
                return

            buffer.extend(chunk)
            while b"\n" in buffer:
                raw_line, _, remainder = buffer.partition(b"\n")
                buffer = bytearray(remainder)
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line:
                    continue

                packet = parser.parse_line(line)
                if packet and packet.is_valid:
                    print_packet(packet)
                else:
                    reason = packet.error_msg if packet else "unrecognized record"
                    print("Invalid telemetry ({}): {}".format(reason, line))


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--host", default="192.168.1.91", help="Raspberry Pi IP address")
    cli.add_argument("--port", type=int, default=5000, help="Telemetry TCP port")
    args = cli.parse_args()

    try:
        read_stream(args.host, args.port)
    except ConnectionRefusedError:
        print("Connection refused. Check the Pi IP, port, and TCP server.")
    except TimeoutError:
        print("Connection timed out. Check that the Pi is reachable on the network.")
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except OSError as exc:
        print("Network error: {}".format(exc))


if __name__ == "__main__":
    main()
