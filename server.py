import socket
import time

RECEIVER_PORT = 5005
CLIENT_TIMEOUT = 300


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(('0.0.0.0', RECEIVER_PORT))
    except OSError as e:
        print(f"Could not bind to port {RECEIVER_PORT}: {e}")
        return

    print(f"Conference server listening on port {RECEIVER_PORT}...")

    clients = {}

    try:
        while True:
            try:
                data, addr = sock.recvfrom(4096)
            except OSError as e:
                print(f"\nFailed to receive audio: {e}")
                continue

            sender_ip = addr[0]
            now = time.time()

            if sender_ip not in clients:
                print(f"Client joined: {sender_ip} ({len(clients) + 1} connected)")
            clients[sender_ip] = now

            for ip in [ip for ip, last_seen in clients.items() if now - last_seen > CLIENT_TIMEOUT]:
                del clients[ip]
                print(f"Client timed out: {ip} ({len(clients)} connected)")

            for client_ip in clients:
                if client_ip == sender_ip:
                    continue
                try:
                    sock.sendto(data, (client_ip, RECEIVER_PORT))
                except OSError as e:
                    print(f"Failed to forward to {client_ip}: {e}")
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
