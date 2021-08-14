import logging

logger = logging.getLogger(f"main.{__name__}")

# Keeps track of hom many times main() has run
RUN=0

def main():
    """
        This is an example of code you want to run on every iteration
        You can, and probably should move this to its own Python module

        This sample code intentionally crashes once in a while to show what
        happens when your code raises an exception
    """

    # Increment run counter
    global RUN
    RUN += 1

    # If the number of times we've run is a multiple of 3, crash!
    if RUN % 3 == 0:
        raise Exception("Something failed!")
    else:
        logger.info("Running our code")
