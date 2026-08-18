# UDP Audio Intercom

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/downloads/)
[![PyAudio](https://img.shields.io/badge/dependency-PyAudio-orange.svg)](https://pypi.org/project/PyAudio/)

A minimal real-time audio intercom over a local network. `transmitter.py` captures microphone audio and streams it via UDP; `receiver.py` listens for that stream and plays it back through the speakers. `server.py` optionally turns it into a group conference by relaying everyone's audio to everyone else.

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

1. Start `receiver.py` first, then pick which speaker/output device to play audio on from the numbered list it prints (press Enter to use the system default).
2. Start `transmitter.py`, then pick which microphone/input device to capture from the same way. It also broadcasts a discovery message on the network and auto-fills the receiver's IP if one answers within a few seconds; otherwise it falls back to prompting you to type it in.
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
Muted        [--------------------------] 
Receiving    [####------------------------] 
```

The transmitter is hands-free by default: it computes the RMS loudness of each captured chunk and only sends it when the level is at or above `VAD_THRESHOLD` (500), so background noise and silence aren't streamed. Adjust `VAD_THRESHOLD` in `transmitter.py` if it's cutting off quiet speech or picking up too much noise.

## Group conference (3+ participants)

Run `server.py` on one machine to act as a relay. Every packet it receives from a participant is forwarded to every *other* known participant, so everyone's `receiver.py` plays a stream made up of everyone else's voices, one packet at a time, back-to-back.

1. Start `server.py` on a machine reachable by all participants. It needs no configuration and doesn't need a microphone or speaker.
2. Each participant runs `receiver.py` (to hear the others) and `transmitter.py` (to be heard), entering the **server's** IP when `transmitter.py` prompts for the receiver's address.
3. Skip auto-discovery in conference mode: since every participant is also running `receiver.py`, a discovery broadcast will get answered by whichever participant's machine responds first — not necessarily the server. Answer `n` when prompted and type the server's IP manually.
4. The server tracks who's connected by source IP and drops anyone it hasn't heard from in 5 minutes (`CLIENT_TIMEOUT` in `server.py`).

This is relay-based, not sample-level mixing — the server doesn't add waveforms together, it just forwards each packet as-is to the other participants. That keeps the server simple and avoids clipping from summed audio, but if two people speak at the same instant, their audio arrives and plays as separate back-to-back packets rather than a blended overlap.

## Error handling

- The transmitter validates the IP address you enter and re-prompts on invalid input.
- Both scripts report and recover from microphone/speaker and socket errors during the audio loop instead of crashing (e.g. a dropped packet or a momentary device glitch won't kill the stream).
- The receiver reports a clear error if the port is already in use, and both scripts report a clear error if the audio device can't be opened.
- The server reports a clear error if the port is already in use, and recovers from forwarding errors to individual clients without dropping the others.

## Notes

- Audio is sent uncompressed (16-bit PCM, mono, 44100 Hz), so this is intended for LAN use — it will use significant bandwidth and has no packet-loss handling.
- No encryption or authentication — anyone who can reach the port can send it audio to play, or answer a discovery request. Don't expose this to the open internet.
- Discovery relies on the subnet's broadcast address (`255.255.255.255`) reaching the receiver, which usually only works within the same LAN segment/Wi-Fi network — it won't cross routers or VPNs.
