#!/usr/bin/env python3

# This is a quick unix socket client

import socket
import sys

socket_path = "/tmp/my_service.sock"

with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
    try:
        client.connect(socket_path)
    except FileNotFoundError:
        print(f"ERROR: Socket file doesn't exist at {socket_path}. Is the server running?")
        sys.exit(1)

    while True:
        # Receive data from server
        data = client.recv(1024)

        # Check if server closed connection (no data received)
        if not data:
            break

        # Print the data we received
        print(data.decode("utf-8"), end="")

    # Close the socket
    client.close()
