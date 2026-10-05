"""
Asynchronous Telemetry Connection Worker (UDP Socket & Serial COM) and Simulator Thread using QtPy.
"""

import socket
import time
from typing import Optional
from qtpy.QtCore import QThread, Signal
import serial
import serial.tools.list_ports

from app.core.telemetry_model import TelemetryPacket, SerialStats
from app.core.parser import TelemetryParser
from app.core.simulator import GliderSimulator


class SerialWorker(QThread):
    """
    Background worker thread handling UDP network sockets, physical COM port serial reading,
    and high-fidelity simulation mode with real-time signal dispatching.
    """

    # Signals
    telemetry_received = Signal(object)      # TelemetryPacket
    raw_line_received = Signal(str)          # raw string
    stats_updated = Signal(object)           # SerialStats / ConnectionStats
    connection_changed = Signal(bool, str)   # (is_connected, message)
    command_sent = Signal(str)               # command string sent
    error_occurred = Signal(str)             # error description

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = False
        self._is_simulated = False
        self._is_receiving_data = False
        self._last_packet_time = 0.0
        self.connection_mode: str = "TCP"  # "TCP", "UDP", or "SERIAL"
        self.last_remote_addr: Optional[tuple] = None
        
        # Network params
        self.udp_ip: str = "192.168.1.51"
        self.udp_port: int = 5000
        self.udp_socket: Optional[socket.socket] = None
        self.tcp_socket: Optional[socket.socket] = None

        # Serial params
        self.port: str = "COM10"
        self.baud_rate: int = 115200
        self.data_bits: int = 8
        self.parity: str = "N"
        self.stop_bits: float = 1.0
        self.serial_inst: Optional[serial.Serial] = None

        # Parser & Simulator
        self.parser = TelemetryParser()
        self.simulator = GliderSimulator()

        # Metrics tracking
        self.stats = SerialStats()
        self._bytes_window = 0
        self._last_rate_time = time.time()
        self._connect_time = 0.0

    def send_command(self, cmd_text: str) -> bool:
        """Transmits a command string over TCP, UDP socket, or Serial COM port."""
        cmd = cmd_text.strip() + "\n"
        if self._is_simulated:
            self.command_sent.emit(cmd_text)
            self.raw_line_received.emit(f"[TX] {cmd_text}")
            return True

        mode_upper = self.connection_mode.upper()
        if "TCP" in mode_upper:
            if self.tcp_socket:
                try:
                    self.tcp_socket.sendall(cmd.encode("utf-8"))
                    self.command_sent.emit(cmd_text)
                    self.raw_line_received.emit(f"[TX] {cmd_text}")
                    return True
                except Exception as e:
                    self.error_occurred.emit(f"Failed to send TCP command: {e}")
                    return False
        elif "UDP" in mode_upper:
            if self.udp_socket:
                try:
                    dest = self.last_remote_addr or (self.udp_ip, self.udp_port)
                    self.udp_socket.sendto(cmd.encode("utf-8"), dest)
                    self.command_sent.emit(cmd_text)
                    self.raw_line_received.emit(f"[TX] {cmd_text}")
                    return True
                except Exception as e:
                    self.error_occurred.emit(f"Failed to send UDP command: {e}")
                    return False
        else:
            if self.serial_inst and self.serial_inst.is_open:
                try:
                    self.serial_inst.write(cmd.encode("utf-8"))
                    self.command_sent.emit(cmd_text)
                    self.raw_line_received.emit(f"[TX] {cmd_text}")
                    return True
                except Exception as e:
                    self.error_occurred.emit(f"Failed to send Serial command: {e}")
                    return False
        return False

    @staticmethod
    def list_available_ports():
        """Scans and returns available COM ports on the system."""
        try:
            ports = serial.tools.list_ports.comports()
            port_list = []
            for p in ports:
                port_list.append(p.device)
            return sorted(port_list)
        except Exception:
            return ["COM1", "COM3", "COM10"]

    def start_tcp_connection(self, ip: str = "192.168.1.51", port: int = 5000, is_sim: bool = False):
        """Initiates TCP client connection to Raspberry Pi server."""
        self.connection_mode = "TCP"
        self.udp_ip = ip.strip() or "192.168.1.51"
        self.udp_port = int(port)
        self._is_simulated = is_sim
        self._is_receiving_data = False
        self._last_packet_time = 0.0
        self._running = True
        self.start()

    def start_udp_connection(self, ip: str = "192.168.1.51", port: int = 5000, is_sim: bool = False):
        """Initiates UDP network socket listening."""
        self.connection_mode = "UDP"
        self.udp_ip = ip.strip() or "0.0.0.0"
        self.udp_port = int(port)
        self._is_simulated = is_sim
        self._is_receiving_data = False
        self._last_packet_time = 0.0
        self._running = True
        self.start()

    def start_serial_connection(self, port: str, baud: int, data_bits: int = 8, parity: str = "None", stop_bits: str = "1", is_sim: bool = False):
        """Initiates connection to a physical COM port."""
        self.connection_mode = "SERIAL"
        self.port = port
        self.baud_rate = baud
        self.data_bits = data_bits
        self._is_simulated = is_sim
        self._is_receiving_data = False
        self._last_packet_time = 0.0
        
        # Parse parity
        par_map = {"None": serial.PARITY_NONE, "Even": serial.PARITY_EVEN, "Odd": serial.PARITY_ODD, "Mark": serial.PARITY_MARK, "Space": serial.PARITY_SPACE}
        self.parity = par_map.get(parity, serial.PARITY_NONE)

        # Parse stop bits
        stop_map = {"1": serial.STOPBITS_ONE, "1.5": serial.STOPBITS_ONE_POINT_FIVE, "2": serial.STOPBITS_TWO}
        self.stop_bits = stop_map.get(stop_bits, serial.STOPBITS_ONE)

        self._running = True
        self.start()

    def start_connection(self, mode: str = "TCP", port: str = "COM10", baud: int = 115200, data_bits: int = 8,
                         parity: str = "None", stop_bits: str = "1", ip: str = "192.168.1.51", udp_port: int = 5000,
                         is_sim: bool = False):
        """Unified connection starter."""
        mode_upper = mode.upper()
        if "TCP" in mode_upper:
            self.start_tcp_connection(ip=ip, port=udp_port, is_sim=is_sim)
        elif "UDP" in mode_upper:
            self.start_udp_connection(ip=ip, port=udp_port, is_sim=is_sim)
        else:
            self.start_serial_connection(port=port, baud=baud, data_bits=data_bits, parity=parity, stop_bits=stop_bits, is_sim=is_sim)

    def stop_connection(self):
        """Disconnects and terminates the background thread."""
        self._running = False
        self._is_receiving_data = False
        
        # Close serial port if open
        if self.serial_inst and self.serial_inst.is_open:
            try:
                self.serial_inst.close()
            except Exception:
                pass
            self.serial_inst = None

        # Close UDP socket if open
        if self.udp_socket:
            try:
                self.udp_socket.close()
            except Exception:
                pass
            self.udp_socket = None

        # Close TCP socket if open
        if hasattr(self, "tcp_socket") and self.tcp_socket:
            try:
                self.tcp_socket.close()
            except Exception:
                pass
            self.tcp_socket = None

        self.wait(1000)
        self.stats.is_connected = False
        self.stats.is_receiving_data = False
        self.stats.uptime_seconds = 0.0
        self.connection_changed.emit(False, "DISCONNECTED")

    def run(self):
        """Main thread loop."""
        self._connect_time = time.time()
        self._last_rate_time = time.time()
        self._bytes_window = 0
        
        mode_upper = self.connection_mode.upper()
        if "TCP" in mode_upper:
            port_label = f"TCP:{self.udp_ip}:{self.udp_port}"
        elif "UDP" in mode_upper:
            port_label = f"UDP:{self.udp_port}"
        else:
            port_label = self.port

        self.stats = SerialStats(
            is_connected=True,
            is_receiving_data=False,
            port_name=port_label if not self._is_simulated else "SIMULATOR",
            baud_rate=self.baud_rate if mode_upper == "SERIAL" else self.udp_port
        )

        if self._is_simulated:
            self._is_receiving_data = True
            self.connection_changed.emit(True, "CONNECTED")
            self._run_simulation_loop()
        elif "TCP" in mode_upper:
            self._run_tcp_loop()
        elif "UDP" in mode_upper:
            self._run_udp_loop()
        else:
            self._run_serial_loop_entry()

    def _run_tcp_loop(self):
        """Connects to TCP server (Raspberry Pi / Teensy) and streams telemetry."""
        try:
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.settimeout(4.0)
            target_ip = self.udp_ip.strip() or "192.168.1.51"
            target_port = int(self.udp_port)

            self.tcp_socket.connect((target_ip, target_port))
            self.tcp_socket.settimeout(0.2)

            # Signal that socket is connected and listening for first data packet
            self.connection_changed.emit(True, "WAITING")

        except Exception as e:
            self._running = False
            self.stats.is_connected = False
            self.stats.is_receiving_data = False
            self.error_occurred.emit(f"TCP connection failed to {self.udp_ip}:{self.udp_port}: {e}")
            self.connection_changed.emit(False, "DISCONNECTED")
            if hasattr(self, "tcp_socket") and self.tcp_socket:
                try:
                    self.tcp_socket.close()
                except Exception:
                    pass
                self.tcp_socket = None
            return

        buffer = ""
        while self._running and self.tcp_socket:
            try:
                t0 = time.perf_counter()
                try:
                    data = self.tcp_socket.recv(4096)
                    if not data:
                        self.error_occurred.emit("Raspberry Pi closed the TCP connection.")
                        break
                except socket.timeout:
                    self._check_data_timeout()
                    continue
                except (OSError, socket.error):
                    break

                data_len = len(data)
                self.stats.rx_bytes += data_len
                self._bytes_window += data_len

                buffer += data.decode("utf-8", errors="replace")
                while "\n" in buffer:
                    line_str, buffer = buffer.split("\n", 1)
                    line_str = line_str.strip()
                    if line_str:
                        self.raw_line_received.emit(line_str)
                        packet = self.parser.parse_line(line_str)
                        if packet and packet.is_valid:
                            self.stats.packet_count += 1
                            self._last_packet_time = time.time()
                            if not self._is_receiving_data:
                                self._is_receiving_data = True
                                self.connection_changed.emit(True, "CONNECTED")
                            self.telemetry_received.emit(packet)
                        else:
                            self.stats.error_count += 1

                self._check_data_timeout()
                t_read = (time.perf_counter() - t0) * 1000.0
                self.stats.latency_ms = round(t_read, 1)
                self._update_stats()

            except Exception as ex:
                self.stats.error_count += 1
                self.error_occurred.emit(f"TCP stream error: {ex}")
                time.sleep(0.05)

        if hasattr(self, "tcp_socket") and self.tcp_socket:
            try:
                self.tcp_socket.close()
            except Exception:
                pass
            self.tcp_socket = None

        self._running = False
        self.stats.is_connected = False
        self.stats.is_receiving_data = False
        self.connection_changed.emit(False, "DISCONNECTED")

    def _run_udp_loop(self):
        """Listens on UDP socket for incoming telemetry datagrams."""
        try:
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.udp_socket.settimeout(0.2)

            # Try binding to specific IP or fallback to 0.0.0.0 (all interfaces)
            bind_success = False
            target_ip = self.udp_ip.strip()

            if target_ip and target_ip not in ("0.0.0.0", "127.0.0.1", "localhost"):
                try:
                    self.udp_socket.bind((target_ip, self.udp_port))
                    bind_success = True
                except Exception:
                    bind_success = False

            if not bind_success:
                try:
                    self.udp_socket.bind(("0.0.0.0", self.udp_port))
                    bind_success = True
                except Exception as ex:
                    raise RuntimeError(f"Could not bind UDP socket to port {self.udp_port}: {ex}")

            # Emit WAITING state until first telemetry packet arrives
            self.connection_changed.emit(True, "WAITING")

        except Exception as e:
            self._running = False
            self.stats.is_connected = False
            self.stats.is_receiving_data = False
            self.error_occurred.emit(f"UDP connection failed: {e}")
            self.connection_changed.emit(False, "DISCONNECTED")
            return

        while self._running and self.udp_socket:
            try:
                t0 = time.perf_counter()
                try:
                    data, addr = self.udp_socket.recvfrom(4096)
                except socket.timeout:
                    self._check_data_timeout()
                    continue
                except (OSError, socket.error):
                    break

                if data:
                    self.last_remote_addr = addr
                    data_len = len(data)
                    self.stats.rx_bytes += data_len
                    self._bytes_window += data_len

                    text = data.decode("utf-8", errors="replace").strip()
                    lines = text.splitlines()
                    for line in lines:
                        line_str = line.strip()
                        if line_str:
                            self.raw_line_received.emit(line_str)
                            packet = self.parser.parse_line(line_str)
                            if packet and packet.is_valid:
                                self.stats.packet_count += 1
                                self._last_packet_time = time.time()
                                if not self._is_receiving_data:
                                    self._is_receiving_data = True
                                    self.connection_changed.emit(True, "CONNECTED")
                                self.telemetry_received.emit(packet)
                            else:
                                self.stats.error_count += 1

                    t_read = (time.perf_counter() - t0) * 1000.0
                    self.stats.latency_ms = round(t_read, 1)
                    self._update_stats()

            except Exception as ex:
                self.stats.error_count += 1
                self.error_occurred.emit(f"UDP read error: {ex}")
                time.sleep(0.05)

        if self.udp_socket:
            try:
                self.udp_socket.close()
            except Exception:
                pass
            self.udp_socket = None

    def _run_serial_loop_entry(self):
        """Opens physical serial port and enters loop."""
        try:
            self.serial_inst = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                bytesize=self.data_bits,
                parity=self.parity,
                stopbits=self.stop_bits,
                timeout=0.1
            )
            # Emit WAITING state until first telemetry packet arrives
            self.connection_changed.emit(True, "WAITING")
            self._run_serial_loop()
        except Exception as e:
            self._running = False
            self.stats.is_connected = False
            self.stats.is_receiving_data = False
            self.error_occurred.emit(f"Failed to open {self.port}: {e}")
            self.connection_changed.emit(False, "DISCONNECTED")

    def _run_serial_loop(self):
        """Reads lines from physical serial port."""
        buffer = bytearray()

        while self._running and self.serial_inst and self.serial_inst.is_open:
            try:
                t0 = time.perf_counter()
                raw_chunk = self.serial_inst.read(self.serial_inst.in_waiting or 1)
                
                if raw_chunk:
                    chunk_len = len(raw_chunk)
                    self.stats.rx_bytes += chunk_len
                    self._bytes_window += chunk_len
                    buffer.extend(raw_chunk)

                    # Process complete lines
                    while b"\n" in buffer:
                        line_bytes, buffer = buffer.split(b"\n", 1)
                        line_str = line_bytes.decode("utf-8", errors="replace").strip()
                        if line_str:
                            self.raw_line_received.emit(line_str)
                            packet = self.parser.parse_line(line_str)
                            if packet and packet.is_valid:
                                self.stats.packet_count += 1
                                self._last_packet_time = time.time()
                                if not self._is_receiving_data:
                                    self._is_receiving_data = True
                                    self.connection_changed.emit(True, "CONNECTED")
                                self.telemetry_received.emit(packet)
                            else:
                                self.stats.error_count += 1

                self._check_data_timeout()
                t_read = (time.perf_counter() - t0) * 1000.0
                self.stats.latency_ms = round(t_read, 1)
                self._update_stats()

            except Exception as ex:
                self.stats.error_count += 1
                self.error_occurred.emit(f"Serial read error: {ex}")
                time.sleep(0.05)

        if self.serial_inst and self.serial_inst.is_open:
            self.serial_inst.close()

    def _check_data_timeout(self):
        """If data has stopped arriving for > 2.5s, switch status to WAITING."""
        if not self._is_simulated and self._is_receiving_data:
            if time.time() - self._last_packet_time > 2.5:
                self._is_receiving_data = False
                self.connection_changed.emit(True, "WAITING")




    def _run_simulation_loop(self):
        """Simulates realistic telemetry generation at ~20 Hz (50 ms interval)."""
        dt = 0.05
        while self._running:
            t0 = time.perf_counter()
            packet = self.simulator.step(dt)

            self.stats.packet_count += 1
            raw_len = len(packet.raw_text.encode('utf-8')) + 2
            self.stats.rx_bytes += raw_len
            self._bytes_window += raw_len

            self.raw_line_received.emit(packet.raw_text)
            self.telemetry_received.emit(packet)

            t_elapsed = (time.perf_counter() - t0)
            self.stats.latency_ms = round(t_elapsed * 1000.0, 1)
            self._update_stats()

            sleep_time = max(0.005, dt - t_elapsed)
            time.sleep(sleep_time)

    def _update_stats(self):
        """Calculates throughput rates and uptime every 500 ms."""
        now = time.time()
        elapsed_rate = now - self._last_rate_time
        if elapsed_rate >= 0.5:
            rate_kb = (self._bytes_window / 1024.0) / elapsed_rate
            self.stats.rx_rate_kbps = round(rate_kb, 2)
            self.stats.uptime_seconds = round(now - self._connect_time, 1)
            self.stats_updated.emit(self.stats)
            
            self._bytes_window = 0
            self._last_rate_time = now

