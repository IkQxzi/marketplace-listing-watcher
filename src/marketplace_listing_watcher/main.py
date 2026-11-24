import typer

from marketplace_listing_watcher.cli import watch

app = typer.Typer()
app.add_typer(watch.app, name="watch")
# TODO: add auth, tools

if __name__ == "__main__":
    app()
