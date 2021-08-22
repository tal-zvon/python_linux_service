#!/usr/bin/env python3

# This alternative_service Python module is very similar to the regular
# service.py, but with one additional feature: if this service receives a
# USR1 kill signal, it will trigger main() right away. This lets you have a
# service that periodically monitors something to see if action needs to be
# taken, but also listen for the USR1 kill signal, which would cause the
# service to check immediately if action needs to be taken
#
# To signal the process from bash would look something like this:
#
#   pkill -USR1 -f alternative_service.py
#
# This will search for a process with "alternative_service.py" in the name,
# and send it the USR1 kill signal.
#
# If this process (alternative_service.py) runs as root, but your
# signalling process runs as a different user, that user will need
# permissions to send a signal to this process. One of the simplest ways to
# do that is sudo. Add something like this to
# /etc/sudoers.d/010_custom_rule:
#
#   USERNAME ALL=NOPASSWD:/usr/bin/pkill -f alternative_service.py -USR1
#
# Where USERNAME is the username you want to allow the ability to signal
# your process.
#
# This will let USERNAME run:
#
#   sudo /usr/bin/pkill -f alternative_service.py -USR1
#
# without asking them for a password.
#
# If your signalling process is Python, rather then bash, you might need to
# do something like this instead:
#
# import subprocess
# subprocess.run("sudo /usr/bin/pkill -f alternative_service.py -USR1".split(), capture_output=True)

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

# USR1 flag
USR1_KILL_SIGNAL_SET = False

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

def set_usr1_flag(*_):
    global USR1_KILL_SIGNAL_SET
    USR1_KILL_SIGNAL_SET = True

# If another process requests us to run main without waiting, do it
signal.signal(signal.SIGUSR1, set_usr1_flag)

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

#############
# Functions #
#############

def get_time_waited(last_run):
    """
        Given the lat time main() was run, looks at the current time
        (represented by time.perf_counter()) and figures out how long it's
        been (in seconds)
    """
    return time.perf_counter() - last_run

########
# Main #
########

# Keep track of the last time main() ran
# We start with -1000 so that on the first run, main() always triggers
# without waiting
last_run = -1000

while True:
    ###########################
    # Wait Between Iterations #
    ###########################

    time.sleep(1)


    if USR1_KILL_SIGNAL_SET:
        # Reset the flag and go on to run main()
        USR1_KILL_SIGNAL_SET = False
    elif DEBUG and get_time_waited(last_run) >= DEBUG_SLEEP_TIME:
        # Go on to run main()
        pass
    elif not DEBUG and get_time_waited(last_run) >= PRODUCTION_SLEEP_TIME:
        # Go on to run main()
        pass
    else:
        # Keep waiting
        continue

    try:
        main()
    except Exception:
        logger.error(format_exc_for_journald(traceback.format_exc(), indent_lines=False))
        send_alert(traceback.format_exc(), destination_addresses=ADMIN_EMAILS)
    finally:
        last_run = time.perf_counter()
        logger.debug(f"Waiting {DEBUG_SLEEP_TIME} seconds...")
