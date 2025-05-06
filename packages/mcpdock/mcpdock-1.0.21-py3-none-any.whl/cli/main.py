import click
from .commands.install import install
from .commands.run import run
from .commands.query_pid import query_pid
from .commands.uninstall import uninstall


@click.group()
@click.version_option(version="1.0.0", package_name="py-cli")  # Corresponds to program.version("1.0.0")
def cli():
    """A custom CLI tool translated to Python."""
    pass


cli.add_command(install)
cli.add_command(run)
cli.add_command(query_pid)
cli.add_command(uninstall)
