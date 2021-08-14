#!/usr/bin/env python3

# This is a quick unix socket client

import socket

socket_path = "/tmp/my_service.sock"

with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
    client.connect(socket_path)

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
