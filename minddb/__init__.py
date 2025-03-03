import anthropic
import instructor


CLIENT = None
ASYNC_CLIENT = None
MODEL = "claude-3-7-sonnet-latest"


def client():
    """Get the client and current model

    Returns
    -------
    tuple: (client, model)
    """

    global CLIENT
    if CLIENT is None:
        CLIENT = instructor.from_anthropic(anthropic.Anthropic())

    return CLIENT, MODEL


def async_client():
    """Get the async client and current model

    Returns
    -------
    tuple: (client, model)
    """
    global ASYNC_CLIENT
    if ASYNC_CLIENT is None:
        ASYNC_CLIENT = instructor.from_anthropic(anthropic.AsyncAnthropic())

    return ASYNC_CLIENT, MODEL
