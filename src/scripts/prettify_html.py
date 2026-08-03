import click
from bs4 import BeautifulSoup

from pathlib import Path

from utils.io import write_to_dir
from utils.config import TEMP_LOG_DIR


@click.command(name=None)
@click.argument('path', 'filepath', 'file')
@click.argument('output_dir', 'dir', default=TEMP_LOG_DIR)
@click.argument('item_name', 'item')
def main(path: str, output_dir: str, item_name: str):

    html_path = Path(path)
    output_path = Path(output_dir)

    with html_path.open() as f:
        soup = BeautifulSoup(f)

        write_to_dir(content=soup.prettify(), dir=(output_path / item_name), file_ext='html')
        print('WARNING: Prettified HTML files break parser. Do not use with parser.')



if __name__ == '__main__': 
    main()