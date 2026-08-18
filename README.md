# UDP Audio Intercom

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/downloads/)
[![PyAudio](https://img.shields.io/badge/dependency-PyAudio-orange.svg)](https://pypi.org/project/PyAudio/)

A minimal real-time audio intercom over a local network. `transmitter.py` captures microphone audio and streams it via UDP; `receiver.py` listens for that stream and plays it back through the speakers.

## Requirements

- Python 3
- [PyAudio](https://pypi.org/project/PyAudio/)

Install dependencies:

```bash
pip install -r requirements.txt
```

On Linux, PyAudio needs PortAudio's headers first:

```bash
sudo apt install portaudio19-dev
pip install -r requirements.txt
```

## Setup

1. Start `receiver.py` first — no configuration needed.
2. Start `transmitter.py`. It broadcasts a discovery message on the network and auto-fills the receiver's IP if one answers within a few seconds; otherwise it falls back to prompting you to type it in.
3. Both scripts use `RECEIVER_PORT = 5005` and `DISCOVERY_PORT = 5006` by default — edit both files if you change either.
4. Make sure ports 5005/UDP and 5006/UDP are allowed through any firewall between the two machines, and that broadcast traffic isn't blocked on the network.

## Running

On the **receiving** machine (the one that will play the audio):

```bash
python receiver.py
```

On the **transmitting** machine (the one with the microphone):

```bash
python transmitter.py
```

Each script shows a live VU meter in the terminal that fills up with incoming/outgoing audio level, and press `Ctrl+C` on either side to stop.

```
Transmitting [########----------------------]
Receiving    [####------------------------] 
```

## Error handling

- The transmitter validates the IP address you enter and re-prompts on invalid input.
- Both scripts report and recover from microphone/speaker and socket errors during the audio loop instead of crashing (e.g. a dropped packet or a momentary device glitch won't kill the stream).
- The receiver reports a clear error if the port is already in use, and both scripts report a clear error if the audio device can't be opened.

## Notes

- Audio is sent uncompressed (16-bit PCM, mono, 44100 Hz), so this is intended for LAN use — it will use significant bandwidth and has no packet-loss handling.
- No encryption or authentication — anyone who can reach the port can send it audio to play, or answer a discovery request. Don't expose this to the open internet.
- Discovery relies on the subnet's broadcast address (`255.255.255.255`) reaching the receiver, which usually only works within the same LAN segment/Wi-Fi network — it won't cross routers or VPNs.
