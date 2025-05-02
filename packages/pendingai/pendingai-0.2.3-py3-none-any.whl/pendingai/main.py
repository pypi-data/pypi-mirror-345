#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from __future__ import annotations

import importlib.metadata
import typing

import rich
import typer

from pendingai import Environment, config
from pendingai.commands import command as base_command
from pendingai.commands.auth import command as auth_command
from pendingai.commands.retro import command as retro_command
from pendingai.context import ContextContent
from pendingai.utils import regex_patterns

console = rich.console.Console(
    theme=config.RICH_CONSOLE_THEME, width=config.CONSOLE_WIDTH
)

app = typer.Typer(
    name=config.APPLICATION_NAME,
    help=(
        "Pending AI Command-Line Interface.\n\nCheminformatics services "
        "offered by this CLI are accessible through an API integration "
        "with the Pending AI platform. An authenticated session is required "
        "for use; see <pendingai auth>. Documentation is available with "
        "<pendingai docs>."
    ),
    epilog=(
        "For support, issues, or feature requests, please email support@pending.ai."
    ),
    no_args_is_help=True,
    add_completion=False,
    pretty_exceptions_show_locals=False,
    rich_markup_mode=None,
    context_settings={"max_content_width": config.CONSOLE_WIDTH},
)
app.add_typer(auth_command.app)
app.add_typer(retro_command.app)
app.add_typer(base_command.app)


# region callback: options ---------------------------------------------


def _show_version_flag_callback(show_version_flag: bool) -> None:
    """
    Attempt to read the `importlib` version metadata for `pendingai`
    and print to stdout before exiting. If the version is not found
    then an error message is shown with non-zero status.

    Args:
        show_version_flag (bool): Flag for `--version`.

    Raises:
        typer.Exit: Version cannot be found and yields non-zero status.
        typer.Exit: Version is output with zero status.
    """
    if show_version_flag:
        try:
            version: str = importlib.metadata.version(config.APPLICATION_NAME)
        except importlib.metadata.PackageNotFoundError:
            console.stderr = True
            console.print(f"[error]Unable to find package: '{config.APPLICATION_NAME}'")
            raise typer.Exit(1)
        console.print(f"[reset]{config.APPLICATION_NAME}/{version}")
        raise typer.Exit(0)


def _validate_api_key(api_key: str | None) -> str | None:
    """
    Validate an optional api key follows the expected jwt regex pattern.

    Args:
        api_key (str, optional): Optional value for `--api-key`.

    Raises:
        typer.BadParameter: Provided api key does not match jwt pattern.

    Returns:
        str: Validated jwt api key.
    """
    if api_key and regex_patterns.JWT_PATTERN.match(api_key) is None:
        raise typer.BadParameter("Invalid format for the JWT api key.")
    return api_key


# region callback: app -------------------------------------------------


@app.callback()
def init_app_runtime(
    context: typer.Context,
    show_version_flag: typing.Annotated[
        bool,
        typer.Option(
            "--version",
            is_flag=True,
            is_eager=True,
            callback=_show_version_flag_callback,
            help="Show the application version and exit.",
        ),
    ] = False,
    environment: typing.Annotated[
        Environment,
        typer.Option(
            "--env",
            "-e",
            hidden=True,
            show_default=False,
            envvar="PENDINGAI_ENVIRONMENT",
            help="Selectable runtime deployment server.",
        ),
    ] = Environment.PRODUCTION,
) -> None:
    """
    Primary callback for the application performed before any command is
    executed except for eager flags like `--version`. Responsible for
    creating the application context and loading a cache file seamlessly
    if the resources exist at runtime. Minimal requirements are enforced
    so subcommands require their own callback logic.
    """
    context.obj = ContextContent(environment=environment)


if __name__ == "__main__":
    app()
