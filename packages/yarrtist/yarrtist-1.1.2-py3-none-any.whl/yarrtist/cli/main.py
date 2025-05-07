from __future__ import annotations

import typer

import yarrtist
from yarrtist.cli.globals import CONTEXT_SETTINGS
from yarrtist.cli.plot_config import main as plot_config
from yarrtist.cli.plot_connectivity import main as plot_connectivity
from yarrtist.cli.plot_scan import main as plot_scan
from yarrtist.cli.plot_test import main as plot_test

app = typer.Typer(context_settings=CONTEXT_SETTINGS)
app_plots = typer.Typer(context_settings=CONTEXT_SETTINGS)
app.add_typer(app_plots, name="plots")


@app.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(False, "--version", help="Print the current version."),
    prefix: bool = typer.Option(
        False, "--prefix", help="Print the path prefix for data files."
    ),
) -> None:
    """
    Manage top-level options
    """
    if version:
        typer.echo(f"yarrtist v{yarrtist.__version__}")
        raise typer.Exit()
    if prefix:
        typer.echo(yarrtist.data.resolve())
        raise typer.Exit()


app_plots.command("plot-single-test")(plot_test)
app_plots.command("plot-single-config")(plot_config)
app_plots.command("plot-scan")(plot_scan)
app_plots.command("plot-connectivity")(plot_connectivity)
