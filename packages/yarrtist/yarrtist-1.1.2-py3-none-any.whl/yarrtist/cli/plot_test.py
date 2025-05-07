from __future__ import annotations

import logging
from pathlib import Path

import typer

from yarrtist.cli.globals import CONTEXT_SETTINGS, OPTIONS, LogLevel
from yarrtist.plotter.core_functions import plot_fe_histo
from yarrtist.utils.utils import load_data

app = typer.Typer(context_settings=CONTEXT_SETTINGS)


@app.command()
def main(
    input_file: Path = OPTIONS["input_file"],
    output_file: Path = OPTIONS["output_file"],
    verbosity: LogLevel = OPTIONS["verbosity"],
):
    logging.basicConfig(format="[%(levelname)s] %(message)s")
    log = logging.getLogger("YARRtist")
    log.setLevel(verbosity.value)

    log.info(f"Plotting single test: {input_file}")

    data = load_data(input_file)
    plotter = plot_fe_histo(data, "", True)

    if output_file is None:
        output_file = Path(input_file).with_suffix(".png")
        log.debug(f"Output file not found, saving in {output_file}")

    plotter.savefig(f"{output_file}")
    plotter.close()

    log.info(f"File saved in {output_file}")
