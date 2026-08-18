import socket
import struct
import sys
import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

RECEIVER_IP = '0.0.0.0'
RECEIVER_PORT = 5005

METER_WIDTH = 30
MAX_AMPLITUDE = 32768


def audio_level(data):
    samples = struct.unpack(f"<{len(data) // 2}h", data)
    peak = max(abs(s) for s in samples) if samples else 0
    return peak / MAX_AMPLITUDE


def render_meter(level):
    filled = int(level * METER_WIDTH)
    bar = "#" * filled + "-" * (METER_WIDTH - filled)
    sys.stdout.write(f"\rReceiving    [{bar}] ")
    sys.stdout.flush()


def main():
    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True,
                        frames_per_buffer=CHUNK)
    except OSError as e:
        print(f"Could not open speaker: {e}")
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((RECEIVER_IP, RECEIVER_PORT))
    except OSError as e:
        print(f"Could not bind to port {RECEIVER_PORT}: {e}")
        stream.close()
        p.terminate()
        return

    print(f"Receiver listening on port {RECEIVER_PORT}...")

    try:
        while True:
            try:
                data, addr = sock.recvfrom(4096)
            except OSError as e:
                print(f"\nFailed to receive audio: {e}")
                continue

            try:
                stream.write(data)
            except OSError as e:
                print(f"\nPlayback error: {e}")
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
