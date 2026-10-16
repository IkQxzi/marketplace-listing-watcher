import click

from pathlib import Path

from parsing.parser import ListingParser
from config.dirs import LOG_DIR, TEMP_LOG_DIR


LOG_DIRS = {
    'temp': str(TEMP_LOG_DIR)
}

@click.command(name=None) # Nameless so 'main' does not need to be entered
@click.argument("html_file")
@click.argument("item_name")
@click.option("--output_dir", "--dir", default=str(LOG_DIR))
@click.option("--save_df/--no_save_df", "--sd/--nsd",
              default=True, help="Save the df output.") # NOTE: Even if disabled, output_dir always required
def main(html_file: str, item_name: str, output_dir: str, save_df: bool):
    '''
    Convert HTML file to CSV. 
    Specify path to HTML file and item name.'''

    html_path = Path(html_file) 

    output_dir = LOG_DIRS.get(output_dir, output_dir)
    output_dir_path = Path(output_dir)

    parser = ListingParser(save_df=save_df, log_dir=output_dir_path)
    df = parser.parse_sold_listings_html(item_name, html_path)
    return


if __name__ == '__main__':
    main()

