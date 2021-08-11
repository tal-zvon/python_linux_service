#!/usr/bin/env python3

###########
# Imports #
###########

import os
import sys
import logging
import signal
import socket
import time
from socketserver import TCPServer, BaseRequestHandler, ThreadingMixIn

####################
# Global Variables #
####################

# If the DEBUG environment variable is set, uses that to set the DEBUG
# global variable
# If the environment variable isn't set, only sets DEBUG to True if we're
# running in a terminal (as opposed to systemd running our script)
if "DEBUG" in os.environ:
    # Use Environment Variable
    if os.environ["DEBUG"].lower() == "true":
        DEBUG = True
    elif os.environ["DEBUG"].lower() == "false":
        DEBUG = False
    else:
        raise ValueError("DEBUG environment variable not set to 'true' or 'false'")
else:
    # Use run mode
    if os.isatty(sys.stdin.fileno()):
        DEBUG = True
    else:
        DEBUG = False

# Script name
script_name = os.path.basename(__file__)

# Get logger
logger = logging.getLogger(script_name)

# IP and Port for TCP Server to listen on
IP='0.0.0.0'
PORT=1234

################
# Setup Logger #
################

# Setup handler
logger.addHandler(logging.StreamHandler())

# Set logging level
if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

########################
# Kill Signal Handlers #
########################

def signal_handler(*_):
    logger.debug("\nExiting...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

#############################################
# Check if another instance already running #
#############################################

# Since systemd will never run 2 instances of a service at once, the only
# time this would happen is if a service was running, and someone tried to
# run the script manually from terminal at the same time

lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

try:
    lock_socket.bind('\0' + script_name)
except socket.error:
    logger.error(f"Another instance of {script_name} is already running")
    sys.exit(1)

#####################
# Set Up TCP Server #
#####################

class ThreadingTCPServer(ThreadingMixIn, TCPServer):
    # Exit the threads when main thread dies
    daemon_threads = True

###################
# Request Handler #
###################

class MyRequestHandler(BaseRequestHandler):
    def handle(self):
        # Write that someone connected
        logger.info(f"Someone connected from {self.client_address[0]}:{self.client_address[1]}")

        for _ in range(5):
            time.sleep(1)

            # Respond
            message = "hello"
            try:
                self.request.send((message + "\n").encode('utf-8'))
            except BrokenPipeError:
                logger.warning(f"{self.client_address[0]}:{self.client_address[1]} disconnected early")
                return

        logger.info(f"{self.client_address[0]}:{self.client_address[1]} disconnected")

########
# Main #
########

# Start TCP Server
# Note: using a context manager on TCPServer wasn't supported until
# Python3.6. Before that, use server_close()
with ThreadingTCPServer((IP, PORT), MyRequestHandler) as server:
    logger.info(f"Listening on {IP}:{PORT}")
    server.serve_forever()
