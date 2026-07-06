import time

def get_timestamp() -> str:
    '''Get filename-friendly timestamp.'''

    return time.strftime('%Y-%m-%d_%H.%M')


def get_text_timestamp() -> str:

    return time.strftime("%Y-%m-%d at %H:%M:%S")