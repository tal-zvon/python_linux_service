import logging

logger = logging.getLogger(f"main.{__name__}")

def send_alert(tback, destination_addresses):
    """
        Generates the subject, body, and email destination for the email
        alert we are about to send
    """

    subject = "Service Exception Raised"

    body = "Our service ran into an issue. This is the traceback:\n\n"
    body += tback

    # Send the actual email
    send_mail(subject=subject, body=body, to=destination_addresses)

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
