from __future__ import annotations

import logging
from pathlib import Path

import typer

from yarrtist.cli.globals import CONTEXT_SETTINGS, OPTIONS, LogLevel
from yarrtist.plotter.core_functions import plot_fe_config
from yarrtist.utils.utils import create_img_grid, fill_pdf_summary, load_data

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

    log.info(f"Plotting config file: {input_file}")

    data = load_data(input_file)
    plotters = plot_fe_config(data)

    images = []

    for k in plotters:
        if k != "TDAC_1d":
            fill_pdf_summary(plotters[k], images)
    test_img = create_img_grid(images, (2, 2))

    if output_file is None:
        output_file = Path(input_file).with_suffix(".png")
        log.debug(f"Output file not found, saving in {output_file}")

    test_img.save(f"{output_file}")

    log.info(f"File saved in {output_file}")
