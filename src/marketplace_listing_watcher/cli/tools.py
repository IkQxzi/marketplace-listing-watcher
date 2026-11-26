from pathlib import Path

import click
from bs4 import BeautifulSoup

from marketplace_listing_watcher.config.dirs import DATA_DIR, TEMP_DATA_DIR
from marketplace_listing_watcher.parsing.parser import ListingParser
from marketplace_listing_watcher.utils.io import write_to_dir


@click.command(name=None)
@click.argument("path", "filepath", "file")
@click.argument("output_dir", "dir", default=TEMP_DATA_DIR)
@click.argument("item_name", "item")
def prettify_html(path: str, output_dir: str, item_name: str):

    html_path = Path(path)
    output_path = Path(output_dir)

    with html_path.open() as f:
        soup = BeautifulSoup(f)

        write_to_dir(
            content=soup.prettify(), dir=(output_path / item_name), file_ext="html"
        )
        print("WARNING: Prettified HTML files break parser. Do not use with parser.")


LOG_DIRS = {"temp": str(TEMP_DATA_DIR)}


@click.command(name=None)  # Nameless so 'main' does not need to be entered
@click.argument("html_file")
@click.argument("item_name")
@click.option("--output_dir", "--dir", default=str(DATA_DIR))
@click.option(
    "--save_df/--no_save_df", "--sd/--nsd", default=True, help="Save the df output."
)  # NOTE: Even if disabled, output_dir always required
def write_html_to_csv(html_file: str, item_name: str, output_dir: str, save_df: bool):
    """
    Convert HTML file to CSV.
    Specify path to HTML file and item name."""

    html_path = Path(html_file)

    output_dir = LOG_DIRS.get(output_dir, output_dir)
    output_dir_path = Path(output_dir)

    parser = ListingParser(save_df=save_df, log_dir=output_dir_path)
    df = parser.parse_sold_listings_html(item_name, html_path)
    return
