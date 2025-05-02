# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Honeybee-REVIVE result parsing commands."""

import logging
import sys

import click


@click.group(help="Commands for Graphing Results.")
def graph():
    pass


@graph.command("winter-html-graphs")
@click.argument("result-sql", type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.argument("output-name", type=str)
@click.argument("output-file", type=click.File("w"))
def winter_html_graphs(result_sql: str, output_name: str, output_file: click.utils.LazyFile):
    """Create HTML graphs for the winter resilience results."""
    raise NotImplementedError("This command is not yet implemented.....")
    sys.exit(1)
