import socket
import pyaudio

# Audio Settings
CHUNK = 1024  # Number of audio frames per buffer
FORMAT = pyaudio.paInt16  # 16-bit audio format
CHANNELS = 1  # Mono audio
RATE = 44100  # Sampling rate (Hz)

# Network Settings
RECEIVER_IP = '0.0.0.0'  # Listen on all available network interfaces
RECEIVER_PORT = 5005

# 1. Setup PyAudio for playback
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK)

# 2. Setup UDP socket to receive data
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((RECEIVER_IP, RECEIVER_PORT))

print(f"Receiver listening on port {RECEIVER_PORT}...")

# 3. Continuously receive and play audio
try:
    while True:
        data, addr = sock.recvfrom(4096)  # Buffer size
        stream.write(data)  # Play the audio
except KeyboardInterrupt:
    print("Stopping...")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    sock.close()
