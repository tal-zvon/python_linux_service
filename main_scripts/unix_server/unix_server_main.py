import logging
import atexit
import time
from pathlib import Path
from socketserver import UnixStreamServer, StreamRequestHandler, ThreadingMixIn

# Get logger
logger = logging.getLogger(f"main.{__name__}")

####################
# Global Variables #
####################

# Path to socket to listen for clients on
# IMPORTANT NOTE: /tmp isn't always the best choice to put this socket
# file, because by default, systemd creates a private /tmp directory for
# every service it runs. If you want 2 services to communicate using unix
# sockets, and one of the services creates a socket under /tmp, the other
# service won't see it there! See systemd's PrivateTmp= setting, or just
# move the socket somewhere else
socket_path = Path("/tmp/my_service.sock")

################
# Exit Handler #
################

# Whenever the program exits, no matter the reason (exception, kill
# signal, etc), run the delete_socket function which will delete the
# socket file on the filesystem

def delete_socket(socket_path):
    if socket_path.exists():
        logger.debug(f"Deleting socket {socket_path}")
        socket_path.unlink()

atexit.register(delete_socket, socket_path)

###########
# Classes #
###########

# The class who's handle() method will be called when a client connects
class MyRequestHandler(StreamRequestHandler):
    def handle(self):
        logger.info(f"Someone connected to our Unix socket!")

        for _ in range(5):
            time.sleep(1)

            # Respond
            message = "hello"
            try:
                self.request.send((message + "\n").encode('utf-8'))
            except BrokenPipeError:
                logger.warning(f"{self.client_address[0]}:{self.client_address[1]} disconnected early")
                return

        logger.info(f"Client disconnected")

# We subclass this, instead of UnixStreamServer directly, so we can use
# the ThreadingMixIn to give us multi-threading
class ThreadedUnixStreamServer(ThreadingMixIn, UnixStreamServer):
    # Exit the threads when main thread dies
    daemon_threads = True

########
# Main #
########

def main():
    # Make sure there's no socket file left over from previous run
    delete_socket(socket_path)

    # Listen to connections from clients requesting camera feeds
    with ThreadedUnixStreamServer(str(socket_path), MyRequestHandler) as server:
        # Listen for connections
        logger.info(f"Listening on {socket_path} for connections...")
        server.serve_forever()
