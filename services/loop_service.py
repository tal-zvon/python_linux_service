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

#############
# Functions #
#############

def my_code():
    """
        This is an example of code you want to run on every iteration
        You can, and probably should move this to its own Python module

        This sample code intentionally crashes once in a while to show what
        happens when your code raises an exception
    """

    import random
    if random.randint(1,3) == 3:
        raise Exception("Something failed!")
    else:
        logger.info("Running check")

def send_alert(tback):
    """
        Generates the subject, body, and email destination for the email
        alert we are about to send
    """

    subject = "Service Exception Raised"

    body = "Our service ran into an issue. This is the traceback:\n\n"
    body += tback

    # Send the actual email
    send_mail(subject=subject, body=body, to=ADMIN_EMAILS)

def send_mail(subject, body, to):
    """
        Send the email
    """

    # Note: We already printed the exception to the terminal, so this
    # function does NOT need to print the exception again. It just needs to
    # send it. This is just sample code. The real code would send the alert
    # quietly (not print anything to terminal, except maybe a message that
    # an alert was sent)

    logger.warning("="*80)
    logger.warning(f"Sending email to '{to}' with subject '{subject}' about an exception being raised with body:")
    logger.warning(body)
    logger.warning("="*80)

def format_exc_for_journald(ex, indent_lines=False):
    """
        Journald removes leading whitespace from every line, making it very
        hard to read python traceback messages. This tricks journald into
        not removing leading whitespace by adding a dot at the beginning of
        every line
    """

    result = ''
    for line in ex.splitlines():
        if indent_lines:
            result += ".    " + line + "\n"
        else:
            result += "." + line + "\n"
    return result.rstrip()

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
        my_code()
    except Exception:
        logger.error(format_exc_for_journald(traceback.format_exc(), indent_lines=False))
        send_alert(traceback.format_exc())
