import socket

PI_IP = "192.168.1.24"
PI_PORT = 5000

print("==============================================")
print("       TEENSY DATA - RASPBERRY PI")
print("==============================================")
print(f"Connecting to {PI_IP}:{PI_PORT}...")
print()

try:

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect((PI_IP, PI_PORT))

    print("Connected to Raspberry Pi!")
    print("Receiving Teensy data...")
    print("----------------------------------------------")

    while True:

        data = sock.recv(4096)

        if not data:
            print("\nRaspberry Pi closed the connection.")
            break

        text = data.decode("utf-8", errors="replace")

        print(text, end="")

except ConnectionRefusedError:

    print("\nERROR: Connection refused.")
    print("Make sure teensy_server.py is running on the Raspberry Pi.")

except TimeoutError:

    print("\nERROR: Connection timed out.")

except KeyboardInterrupt:

    print("\nStopped by user.")

except Exception as e:

    print(f"\nERROR: {e}")

finally:

    sock.close()

    print("\nDisconnected.")