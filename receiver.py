import socket
import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

RECEIVER_IP = '0.0.0.0'
RECEIVER_PORT = 5005

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((RECEIVER_IP, RECEIVER_PORT))

print(f"Receiver listening on port {RECEIVER_PORT}...")

try:
    while True:
        data, addr = sock.recvfrom(4096)
        stream.write(data)
except KeyboardInterrupt:
    print("Stopping...")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    sock.close()
