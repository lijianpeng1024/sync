import socket
import threading

SERVER_HOST = "0.0.0.0"  # Listen on all interfaces
SERVER_PORT = 5555

clients = {}  # Stores { "pi": socket, "unity": socket }

def handle_client(client_socket, client_type):
    """Handles incoming messages from Pi or Unity and relays them."""
    global clients

    try:
        while True:
            data = client_socket.recv(4096)
            if not data:
                break  # Connection closed

            if client_type == "pi" and "un" in clients:
                clients["un"].sendall(data)  # Forward data to Unity
            elif client_type == "un" and "pi" in clients:
                clients["pi"].sendall(data)  # Forward data to Pi
    except Exception as e:
        print(f"[ERROR] {client_type} connection lost: {e}")
    
    print(f"[INFO] {client_type} disconnected.")
    client_socket.close()
    del clients[client_type]  # Remove client

def accept_clients():
    """Accepts new clients and assigns them a role (Unity or Pi)."""
    global clients

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)

    print(f"[INFO] Relay Server listening on {SERVER_HOST}:{SERVER_PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"[INFO] Connection from {addr}")

        client_type = client_socket.recv(3).decode("utf-8").strip()
        if client_type in ["pi", "un"]:
            clients[client_type] = client_socket
            print(f"[INFO] {client_type} connected.")
            threading.Thread(target=handle_client, args=(client_socket, client_type), daemon=True).start()
        else:
            print("[ERROR] Invalid client type, closing connection.")
            client_socket.close()

accept_clients()
