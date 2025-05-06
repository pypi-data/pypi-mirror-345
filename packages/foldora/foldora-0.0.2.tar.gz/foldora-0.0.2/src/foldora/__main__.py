import click
from foldora.commands import b, c, d, f, l, p


@click.group()
@click.version_option("0.0.2")
def cli():
    """
    Foldora - File & Directory Manager CLI Tool.

    A command line utility (CLI) for file and directory operations.
    Provides commands to list, create, and purge directories and files, and more.
    """
    pass


cli.add_command(l)
cli.add_command(d)
cli.add_command(f)
cli.add_command(p)
cli.add_command(c)
cli.add_command(b)
