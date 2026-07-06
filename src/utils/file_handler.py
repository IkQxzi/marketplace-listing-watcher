import os

from utils.misc import get_timestamp

def write_to_file(path, content):
    '''Writes content to file at path, creating a directory if needed'''

    if not os.path.exists(path):
        os.makedirs(path)

    with open(f'{path}/{get_timestamp()}.html', 'w', encoding='utf-8') as f:
        f.write(content)