import serial
import struct
import time
import sys

PORT = "COM4"      
BAUD = 115200

DYNAMIC_MODEL = 5          
UPDATE_RATE_MS = 200      


UBX_SYNC_1 = 0xB5
UBX_SYNC_2 = 0x62

CLASS_NAV = 0x01
CLASS_ACK = 0x05
CLASS_CFG = 0x06

MSG_NAV_PVT = 0x07
MSG_ACK_NACK = 0x00
MSG_ACK_ACK = 0x01

MSG_CFG_RATE = 0x08
MSG_CFG_MSG = 0x01
MSG_CFG_NAV5 = 0x24
MSG_CFG_CFG = 0x09

def ubx_checksum(data):
    ck_a = 0
    ck_b = 0

    for byte in data:
        ck_a = (ck_a + byte) & 0xFF
        ck_b = (ck_b + ck_a) & 0xFF

    return ck_a, ck_b


def make_ubx(msg_class, msg_id, payload=b""):

    header = struct.pack(
        "<BBBH",
        msg_class,
        msg_id,
        len(payload)
    )

    checksum_data = header + payload

    ck_a, ck_b = ubx_checksum(checksum_data)

    return bytes([
        UBX_SYNC_1,
        UBX_SYNC_2
    ]) + checksum_data + bytes([
        ck_a,
        ck_b
    ])


def send_ubx(ser, msg_class, msg_id, payload=b""):

    packet = make_ubx(
        msg_class,
        msg_id,
        payload
    )

    ser.write(packet)
    ser.flush()

    print(
        f"TX UBX "
        f"class=0x{msg_class:02X} "
        f"id=0x{msg_id:02X} "
        f"length={len(payload)}"
    )


def wait_for_ack(ser, target_class, target_id, timeout=2.0):

    start = time.time()

    buffer = bytearray()

    while time.time() - start < timeout:

        data = ser.read(ser.in_waiting or 1)

        if not data:
            continue

        buffer.extend(data)

        while len(buffer) >= 8:

            
            index = buffer.find(
                bytes([UBX_SYNC_1, UBX_SYNC_2])
            )

            if index < 0:
                buffer.clear()
                break

            if index > 0:
                del buffer[:index]

            if len(buffer) < 6:
                break

            msg_class = buffer[2]
            msg_id = buffer[3]

            length = buffer[4] | (buffer[5] << 8)

            total_length = 8 + length

            if len(buffer) < total_length:
                break

            payload = buffer[6:6 + length]

            packet_without_checksum = buffer[2:6 + length]

            ck_a, ck_b = ubx_checksum(
                packet_without_checksum
            )

            if (
                buffer[6 + length] == ck_a
                and
                buffer[7 + length] == ck_b
            ):

                if (
                    msg_class == CLASS_ACK
                    and
                    msg_id == MSG_ACK_ACK
                    and
                    len(payload) >= 2
                    and
                    payload[0] == target_class
                    and
                    payload[1] == target_id
                ):

                    print(
                        f"ACK received for "
                        f"0x{target_class:02X}/"
                        f"0x{target_id:02X}"
                    )

                    del buffer[:total_length]

                    return True

                if (
                    msg_class == CLASS_ACK
                    and
                    msg_id == MSG_ACK_NACK
                    and
                    len(payload) >= 2
                    and
                    payload[0] == target_class
                    and
                    payload[1] == target_id
                ):

                    print(
                        f"NACK received for "
                        f"0x{target_class:02X}/"
                        f"0x{target_id:02X}"
                    )

                    del buffer[:total_length]

                    return False

            del buffer[:total_length]

    print(
        f"No ACK for "
        f"0x{target_class:02X}/"
        f"0x{target_id:02X}"
    )

    return False

def configure_dynamic_model(ser):

    print("\n[1] Configuring dynamic model: AT SEA")

    mask = 0x0001 | 0x0004

    dyn_model = DYNAMIC_MODEL
    fix_mode = 3

    fixed_alt = 0
    fixed_alt_var = 0

    min_elev = 5
    dr_limit = 0

    p_dop = 0
    t_dop = 0
    p_acc = 100
    t_acc = 100

    static_hold_thresh = 0

    payload = struct.pack(
        "<HBBiIbbHHHHB",
        mask,
        dyn_model,
        fix_mode,
        fixed_alt,
        fixed_alt_var,
        min_elev,
        dr_limit,
        p_dop,
        t_dop,
        p_acc,
        t_acc,
        static_hold_thresh
    )

    payload += bytes(36 - len(payload))

    send_ubx(
        ser,
        CLASS_CFG,
        MSG_CFG_NAV5,
        payload
    )

    return wait_for_ack(
        ser,
        CLASS_CFG,
        MSG_CFG_NAV5
    )


def configure_update_rate(ser):

    print("\n[2] Configuring update rate: 5 Hz")

    payload = struct.pack(
        "<HHH",
        UPDATE_RATE_MS,
        1,
        0
    )

    send_ubx(
        ser,
        CLASS_CFG,
        MSG_CFG_RATE,
        payload
    )

    return wait_for_ack(
        ser,
        CLASS_CFG,
        MSG_CFG_RATE
    )

def enable_nav_pvt(ser):

    print("\n[3] Enabling UBX-NAV-PVT")

    payload = bytes([
        CLASS_NAV,
        MSG_NAV_PVT,
        1
    ])

    send_ubx(
        ser,
        CLASS_CFG,
        MSG_CFG_MSG,
        payload
    )

    return wait_for_ack(
        ser,
        CLASS_CFG,
        MSG_CFG_MSG
    )

def save_configuration(ser):

    print("\n[4] Saving configuration")

    clear_mask = 0x00000000
    save_mask = 0x0000FFFF
    load_mask = 0x00000000
    device_mask = 0x00000017

    payload = struct.pack(
        "<IIII",
        clear_mask,
        save_mask,
        load_mask,
        device_mask
    )

    send_ubx(
        ser,
        CLASS_CFG,
        MSG_CFG_CFG,
        payload
    )
    time.sleep(1)

    print("Save command sent.")


def parse_nav_pvt(payload):

    if len(payload) < 92:
        return None

    try:


        year = struct.unpack_from("<H", payload, 4)[0]
        month = payload[6]
        day = payload[7]

        hour = payload[8]
        minute = payload[9]
        second = payload[10]

        fix_type = payload[20]

        flags = payload[21]

        num_sat = payload[23]

        longitude_raw = struct.unpack_from(
            "<i", payload, 24
        )[0]

        latitude_raw = struct.unpack_from(
            "<i", payload, 28
        )[0]

        altitude_msl_raw = struct.unpack_from(
            "<i", payload, 36
        )[0]

        horizontal_accuracy_raw = struct.unpack_from(
            "<I", payload, 40
        )[0]

        vertical_accuracy_raw = struct.unpack_from(
            "<I", payload, 44
        )[0]

        speed_raw = struct.unpack_from(
            "<i", payload, 60
        )[0]

        heading_raw = struct.unpack_from(
            "<i", payload, 64
        )[0]

        velocity_accuracy_raw = struct.unpack_from(
            "<I", payload, 68
        )[0]

        return {

            "time":
                f"{hour:02d}:"
                f"{minute:02d}:"
                f"{second:02d}",

            "date":
                f"{year:04d}-"
                f"{month:02d}-"
                f"{day:02d}",

            "fix_type": fix_type,

            "gnss_fix_ok":
                bool(flags & 0x01),

            "satellites": num_sat,

            "longitude":
                longitude_raw / 1e7,

            "latitude":
                latitude_raw / 1e7,

            "altitude_m":
                altitude_msl_raw / 1000.0,

            "hacc_m":
                horizontal_accuracy_raw / 1000.0,

            "vacc_m":
                vertical_accuracy_raw / 1000.0,

            "speed_mps":
                speed_raw / 1000.0,

            "heading_deg":
                heading_raw / 1e5,

            "velocity_accuracy_mps":
                velocity_accuracy_raw / 1000.0
        }

    except Exception as e:

        print("NAV-PVT parse error:", e)

        return None

def read_ubx(ser):

    buffer = bytearray()

    while True:

        data = ser.read(
            ser.in_waiting or 1
        )

        if not data:
            continue

        buffer.extend(data)

        while True:

            if len(buffer) < 8:
                break

            index = buffer.find(
                bytes([
                    UBX_SYNC_1,
                    UBX_SYNC_2
                ])
            )

            if index < 0:

                buffer.clear()

                break

            if index > 0:

                del buffer[:index]

            if len(buffer) < 6:
                break

            msg_class = buffer[2]
            msg_id = buffer[3]

            length = (
                buffer[4]
                |
                (buffer[5] << 8)
            )

            total = 8 + length

            if len(buffer) < total:
                break

            packet = buffer[:total]

            payload = packet[
                6:6 + length
            ]

            checksum_data = packet[
                2:6 + length
            ]

            ck_a, ck_b = ubx_checksum(
                checksum_data
            )

            if (
                packet[6 + length] == ck_a
                and
                packet[7 + length] == ck_b
            ):

                if (
                    msg_class == CLASS_NAV
                    and
                    msg_id == MSG_NAV_PVT
                ):

                    gps = parse_nav_pvt(
                        payload
                    )

                    if gps:

                        print(
                            "\n"
                        )

                        print(
                            "           M9N GPS STATUS"
                        )

                        print(
                            f"Fix type       : "
                            f"{gps['fix_type']}"
                        )

                        print(
                            f"GNSS fix valid : "
                            f"{gps['gnss_fix_ok']}"
                        )

                        print(
                            f"Satellites     : "
                            f"{gps['satellites']}"
                        )

                        print(
                            f"Latitude       : "
                            f"{gps['latitude']:.7f}"
                        )

                        print(
                            f"Longitude      : "
                            f"{gps['longitude']:.7f}"
                        )

                        print(
                            f"Altitude       : "
                            f"{gps['altitude_m']:.2f} m"
                        )

                        print(
                            f"HACC           : "
                            f"{gps['hacc_m']:.2f} m"
                        )

                        print(
                            f"VACC           : "
                            f"{gps['vacc_m']:.2f} m"
                        )

                        print(
                            f"Speed          : "
                            f"{gps['speed_mps']:.3f} m/s"
                        )

                        print(
                            f"Heading        : "
                            f"{gps['heading_deg']:.2f} deg"
                        )

                        print(
                            f"Velocity Acc   : "
                            f"{gps['velocity_accuracy_mps']:.3f} m/s"
                        )

            del buffer[:total]


def main():

    print("      HOLYBRO M9N JETSON GPS DRIVER")

    print(f"Port : {PORT}")
    print(f"Baud : {BAUD}")

    try:

        ser = serial.Serial(
            PORT,
            BAUD,
            timeout=0.2
        )

    except Exception as e:

        print("\nERROR opening GPS:")
        print(e)

        sys.exit(1)

    print("\nM9N UART opened.")

    time.sleep(2)
    if not configure_dynamic_model(ser):

        print(
            "WARNING: Dynamic model configuration "
            "was not acknowledged."
        )

    time.sleep(0.5)

    if not configure_update_rate(ser):

        print(
            "WARNING: Update-rate configuration "
            "was not acknowledged."
        )

    time.sleep(0.5)

    if not enable_nav_pvt(ser):

        print(
            "WARNING: NAV-PVT configuration "
            "was not acknowledged."
        )

    time.sleep(0.5)

    save_configuration(ser)

    time.sleep(2)
    print("      GPS CONFIGURATION COMPLETE")

    print("\nWaiting for NAV-PVT data...\n")

    read_ubx(ser)


if __name__ == "__main__":
    main()