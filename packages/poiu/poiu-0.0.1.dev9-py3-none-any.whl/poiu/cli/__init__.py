# SPDX-FileCopyrightText: 2024-present André P. Santos <andreztz@gmail.com>
#
# SPDX-License-Identifier: MIT
import click

from poiu.__about__ import __version__


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="poiu")
def poiu():
    click.echo("Hello world!")
