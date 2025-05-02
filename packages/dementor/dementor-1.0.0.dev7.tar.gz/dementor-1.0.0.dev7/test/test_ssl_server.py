import socket
import ssl

def create_tls_server(host, port):
    # Set up the socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}...")

    # Accept client connection
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address}")

    # Perform the initial handshake (not encrypted)
    initial_message = client_socket.recv(1024).decode('utf-8')
    print(f"Received initial message: {initial_message}")

    # Upgrade the connection to TLS
    print("Upgrading to TLS...")
    tls_socket = ssl.wrap_socket(client_socket, server_side=True, keyfile="server.key", certfile="server.crt")

    # Now communicate securely
    tls_socket.sendall("Hello, TLS-secure client!".encode('utf-8'))

    # Close the TLS connection after communication
    tls_socket.close()
    server_socket.close()

if __name__ == '__main__':
    create_tls_server('localhost', 5000)
