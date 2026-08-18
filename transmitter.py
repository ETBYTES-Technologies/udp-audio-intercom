import socket
import struct
import sys
import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECEIVER_PORT = 5005

METER_WIDTH = 30
MAX_AMPLITUDE = 32768


def get_receiver_ip():
    while True:
        ip = input("Enter receiver's IP address: ").strip()
        try:
            socket.inet_aton(ip)
            return ip
        except OSError:
            print("Invalid IP address, please try again.")


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

    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
    except OSError as e:
        print(f"Could not open microphone: {e}")
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
