import click
from .db import engine, Base
from . import models  # ensure models are imported so tables are registered


@click.command()
def init_db():
    """Create database tables for AyeSpy v2."""
    Base.metadata.create_all(bind=engine)
    click.echo("Database initialized.")


if __name__ == "__main__":
    init_db()


