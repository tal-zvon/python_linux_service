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
import traceback
from main import main
from lib import send_alert, format_exc_for_journald

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
logger = logging.getLogger("main")

# How long to sleep, in seconds, when running in DEBUG mode
DEBUG_SLEEP_TIME = 10

# How long to sleep, in seconds, when running in non-DEBUG mode
PRODUCTION_SLEEP_TIME = 60

# List of email addresses to send emails to when something crashes
ADMIN_EMAILS = ["user@gmail.com"]

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

########
# Main #
########

first_run = True
while True:
    ###########################
    # Wait Between Iterations #
    ###########################

    # If this is the first run, don't wait at all
    # If not, the wait time depends on if we're running in DEBUG mode or not
    # In DEBUG mode, we're troubleshooting, and don't want to wait a long
    # time between iterations

    if first_run:
        first_run = False
    else:
        if DEBUG:
            logger.debug(f"Waiting {DEBUG_SLEEP_TIME} seconds...")
            time.sleep(DEBUG_SLEEP_TIME)
        else:
            time.sleep(PRODUCTION_SLEEP_TIME)

    try:
        main()
    except Exception:
        logger.error(format_exc_for_journald(traceback.format_exc(), indent_lines=False))
        send_alert(traceback.format_exc())
