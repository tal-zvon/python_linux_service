import logging

logger = logging.getLogger(f"main.{__name__}")

def main():
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
