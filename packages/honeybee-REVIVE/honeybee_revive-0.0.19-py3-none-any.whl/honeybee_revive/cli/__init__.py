"""honeybee-REVIVE commands which will be added to Honeybee command line interface."""

import click
from honeybee.cli import main

from honeybee_revive.cli.graph import graph


# command group for all HB-REVIVE extension commands.
@click.group(help="Honeybee-REVIVE commands.")
@click.version_option()
def revive():
    pass


# add sub-commands to HB-REVIVE
revive.add_command(graph)

# add HB-REVIVE sub-commands to honeybee CLI
main.add_command(revive)
