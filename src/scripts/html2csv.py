import click

from pathlib import Path

from webscraper.parser import ListingParser
from utils.config import LOG_DIR


@click.command(name=None) # Nameless so 'main' does not need to be entered
@click.argument("html_file")
@click.argument("item_name")
@click.option("--output_dir", "--dir", default=str(LOG_DIR))
@click.option("--save_pretty_html/--no-save-pretty-html", "--sph/--nsph",
               default=True, help="Save a formatted copy of the HTML file.")
def main(html_file: str, item_name: str, output_dir: str, save_pretty_html: bool):
    '''
    Convert HTML file to CSV. 
    Specify path to HTML file and item name.'''

    html_path = Path(html_file) 
    output_dir_path = Path(output_dir)

    parser = ListingParser(log_dir=output_dir_path, save_pretty_html=save_pretty_html)
    df = parser.parse_sold_listings_html(item_name, html_path)
    return


if __name__ == '__main__':
    main()

