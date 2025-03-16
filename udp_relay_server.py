#!/usr/bin/env python3
import socket

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 5555  # The port for both clients to send/receive through.

def run_two_client_relay_with_kick():
    """
    A minimal UDP relay:
      - Binds to a public IP/port.
      - Keeps track of up to 2 clients (most recent addresses).
      - If a 3rd new address arrives, the oldest is removed, and
        the new client is added.
      - Packets from one client are forwarded to the other.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LISTEN_IP, LISTEN_PORT))
    print(f"[Relay] Listening on {LISTEN_IP}:{LISTEN_PORT} ...")

    clients = []  # will store up to 2 (ip, port) pairs

    while True:
        data, addr = sock.recvfrom(65507)  # max safe UDP payload size

        # If this address is new to our 'clients' list
        if addr not in clients:
            if len(clients) < 2:
                # We have room; just add
                clients.append(addr)
                print(f"[Relay] New client {addr} added. Current clients: {clients}")
            else:
                # We already have 2; kick the oldest (index 0)
                oldest = clients.pop(0)
                print(f"[Relay] Kicking oldest client {oldest}")
                clients.append(addr)
                print(f"[Relay] New client {addr} added. Current clients: {clients}")

        # Now forward data if we indeed have 2 clients
        if len(clients) == 2:
            # If packet came from the first client, forward to the second
            if addr == clients[0]:
                sock.sendto(data, clients[1])
            # If it came from the second, forward to the first
            elif addr == clients[1]:
                sock.sendto(data, clients[0])
            # If it's brand-new and replaced an old client,
            # the code above has already updated 'clients'.

if __name__ == "__main__":
    run_two_client_relay_with_kick()
