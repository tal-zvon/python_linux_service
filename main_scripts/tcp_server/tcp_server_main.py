import logging
import time
from socketserver import TCPServer, BaseRequestHandler, ThreadingMixIn

# Get logger
logger = logging.getLogger(f"main.{__name__}")

# IP and Port for TCP Server to listen on
IP='0.0.0.0'
PORT=1234

#####################
# Set Up TCP Server #
#####################

class ThreadingTCPServer(ThreadingMixIn, TCPServer):
    # Exit the threads when main thread dies
    daemon_threads = True

    # Allow server to run even if there are existing active sockets in
    # TIME-WAIT state on this port. Fixes the "address already in use"
    # error when starting server
    allow_reuse_address = True

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

def main():
    # Start TCP Server
    # Note: using a context manager on TCPServer wasn't supported until
    # Python3.6. Before that, use server_close()
    with ThreadingTCPServer((IP, PORT), MyRequestHandler) as server:
        logger.info(f"Listening on {IP}:{PORT}")
        server.serve_forever()
