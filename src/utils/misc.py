import time

def get_timestamp() -> str:
    '''Get filename-friendly timestamp.'''

    # Uses dash instead of dot between H & M 
    # to prevent suffix problems with pathlib
    return time.strftime('%Y-%m-%d_%H-%M')


def get_text_timestamp() -> str:

    return time.strftime("%Y-%m-%d at %H:%M:%S")