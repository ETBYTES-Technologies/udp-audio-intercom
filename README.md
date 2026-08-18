# UDP Audio Intercom

A minimal real-time audio intercom over a local network. `transmitter.py` captures microphone audio and streams it via UDP; `receiver.py` listens for that stream and plays it back through the speakers.

## Requirements

- Python 3
- [PyAudio](https://pypi.org/project/PyAudio/)

Install dependencies:

```bash
pip install pyaudio
```

On Linux, PyAudio needs PortAudio's headers first:

```bash
sudo apt install portaudio19-dev
pip install pyaudio
```

## Setup

1. Open `transmitter.py` and set `RECEIVER_IP` to the IP address of the machine that will run `receiver.py`.
2. Both scripts use `RECEIVER_PORT = 5005` by default — keep them in sync if you change it.
3. Make sure port 5005/UDP is allowed through any firewall between the two machines.

## Running

On the **receiving** machine (the one that will play the audio):

```bash
python receiver.py
```

On the **transmitting** machine (the one with the microphone):

```bash
python transmitter.py
```

Press `Ctrl+C` on either side to stop.

## Notes

- Audio is sent uncompressed (16-bit PCM, mono, 44100 Hz), so this is intended for LAN use — it will use significant bandwidth and has no packet-loss handling.
- No encryption or authentication — anyone who can reach the port can send it audio to play. Don't expose this to the open internet.
