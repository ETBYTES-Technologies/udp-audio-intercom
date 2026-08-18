import socket
import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

RECEIVER_IP = input("Enter receiver's IP address: ").strip()
RECEIVER_PORT = 5005

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"Transmitting to {RECEIVER_IP}:{RECEIVER_PORT}...")

try:
    while True:
        data = stream.read(CHUNK)
        sock.sendto(data, (RECEIVER_IP, RECEIVER_PORT))
except KeyboardInterrupt:
    print("Stopping...")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    sock.close()
