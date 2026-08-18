import socket
import pyaudio

# Audio Settings (Must match the receiver)
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Network Settings
RECEIVER_IP = '192.168.1.100'  # Replace with the receiver's actual IP address
RECEIVER_PORT = 5005

# 1. Setup PyAudio for recording
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# 2. Setup UDP socket to send data
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"Transmitting to {RECEIVER_IP}:{RECEIVER_PORT}...")

# 3. Continuously record and send audio
try:
    while True:
        data = stream.read(CHUNK)  # Record a chunk of audio
        sock.sendto(data, (RECEIVER_IP, RECEIVER_PORT))  # Send it
except KeyboardInterrupt:
    print("Stopping...")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    sock.close()
