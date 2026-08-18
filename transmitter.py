import socket
import struct
import sys
import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECEIVER_PORT = 5005

DISCOVERY_PORT = 5006
DISCOVERY_MESSAGE = b"UDP_AUDIO_INTERCOM_DISCOVER"
DISCOVERY_REPLY = b"UDP_AUDIO_INTERCOM_HERE"
DISCOVERY_TIMEOUT = 3

METER_WIDTH = 30
MAX_AMPLITUDE = 32768


def discover_receiver_ip(timeout=DISCOVERY_TIMEOUT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)
    try:
        sock.sendto(DISCOVERY_MESSAGE, ('255.255.255.255', DISCOVERY_PORT))
        data, addr = sock.recvfrom(1024)
        if data == DISCOVERY_REPLY:
            return addr[0]
    except OSError:
        pass
    finally:
        sock.close()
    return None


def get_receiver_ip():
    print("Searching for a receiver on the network...")
    discovered_ip = discover_receiver_ip()
    if discovered_ip:
        choice = input(f"Found receiver at {discovered_ip} — use it? [Y/n] ").strip().lower()
        if choice in ("", "y", "yes"):
            return discovered_ip
    else:
        print("No receiver found automatically.")

    while True:
        ip = input("Enter receiver's IP address: ").strip()
        try:
            socket.inet_aton(ip)
            return ip
        except OSError:
            print("Invalid IP address, please try again.")


def choose_device(p, kind):
    key = "maxInputChannels" if kind == "input" else "maxOutputChannels"
    devices = [(i, p.get_device_info_by_index(i)["name"])
               for i in range(p.get_device_count())
               if p.get_device_info_by_index(i)[key] > 0]

    if not devices:
        print(f"No {kind} devices found, using default.")
        return None

    print(f"\nAvailable {kind} devices:")
    for index, name in devices:
        print(f"  [{index}] {name}")

    try:
        get_default = (p.get_default_input_device_info if kind == "input"
                       else p.get_default_output_device_info)
        default_index = get_default()["index"]
    except OSError:
        default_index = None

    valid_indices = {index for index, _ in devices}
    prompt = "Select device index"
    prompt += f" [default: {default_index}]: " if default_index is not None else ": "

    while True:
        choice = input(prompt).strip()
        if choice == "" and default_index is not None:
            return default_index
        if choice.isdigit() and int(choice) in valid_indices:
            return int(choice)
        print("Please enter a valid device number from the list above.")


def audio_level(data):
    samples = struct.unpack(f"<{len(data) // 2}h", data)
    peak = max(abs(s) for s in samples) if samples else 0
    return peak / MAX_AMPLITUDE


def render_meter(level):
    filled = int(level * METER_WIDTH)
    bar = "#" * filled + "-" * (METER_WIDTH - filled)
    sys.stdout.write(f"\rTransmitting [{bar}] ")
    sys.stdout.flush()


def main():
    receiver_ip = get_receiver_ip()

    p = pyaudio.PyAudio()
    device_index = choose_device(p, "input")

    try:
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=device_index,
                        frames_per_buffer=CHUNK)
    except OSError as e:
        print(f"Could not open microphone: {e}")
        p.terminate()
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print(f"Transmitting to {receiver_ip}:{RECEIVER_PORT}...")

    try:
        while True:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
            except OSError as e:
                print(f"\nMicrophone read error: {e}")
                continue

            try:
                sock.sendto(data, (receiver_ip, RECEIVER_PORT))
            except OSError as e:
                print(f"\nFailed to send audio: {e}")
                continue

            render_meter(audio_level(data))
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        sock.close()


if __name__ == "__main__":
    main()
