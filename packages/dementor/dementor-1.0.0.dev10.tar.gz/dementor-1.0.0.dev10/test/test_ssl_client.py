import socket
import ssl

def create_tls_client(host, port):
    # Set up the socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    client_socket.connect((host, port))

    # Send an initial message to the server (before upgrading to TLS)
    client_socket.sendall("Hello Server, I want to start a TLS connection!".encode('utf-8'))

    # Wait for the server's response (not encrypted)
    response = client_socket.recv(1024).decode('utf-8')
    print(f"Received from server: {response}")

    # Upgrade the connection to TLS
    print("Upgrading to TLS...")
    tls_socket = ssl.wrap_socket(client_socket, keyfile=None, certfile=None, server_side=False, ssl_version=ssl.PROTOCOL_TLS)

    # Send a message securely
    tls_socket.sendall("Hello from the secure client!".encode('utf-8'))

    # Close the TLS connection after communication
    tls_socket.close()

if __name__ == '__main__':
    create_tls_client('localhost', 5000)
