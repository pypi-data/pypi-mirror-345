from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import List

import typer
from PIL import Image

from yarrtist.cli.globals import CONTEXT_SETTINGS, OPTIONS, LogLevel
from yarrtist.plotter.core_functions import (
    plot_fe_config,
    plot_module_histo,
)
from yarrtist.utils.utils import (
    create_img_grid,
    data_from_config,
    fill_pdf_summary,
    format_data,
    get_configs_from_connectivity,
    get_geomId_sn_from_config,
    get_moduletype_ordered_chips,
    load_data,
)

logging.basicConfig(format="[%(levelname)s] %(message)s")
log = logging.getLogger("YARRtist")

app = typer.Typer(context_settings=CONTEXT_SETTINGS)


def config_summary_perchip(configs_list, absolute_path, summary_title):
    all_imgs = []

    for chip in configs_list:
        images = []
        _, name = get_geomId_sn_from_config(chip)
        try:
            plotters = plot_fe_config(chip, f"{name}")
            for k in plotters:
                if k != "TDAC_1d":
                    fill_pdf_summary(plotters[k], images)
            chip_img = create_img_grid(images, (2, 2), f"{name}")
            all_imgs.append(chip_img)
            tdac_img = []
            fill_pdf_summary(plotters["TDAC_1d"], tdac_img)
            img = create_img_grid(tdac_img, (1, 1), "")
            all_imgs.append(img)
        except Exception as e:
            log.warning(f"Failed plotting: {e}")

    if all_imgs:
        summary = [p.convert("RGB") for p in all_imgs]
        summary[0].save(
            f"{absolute_path}/{summary_title}.pdf",
            save_all=True,
            append_images=all_imgs[1:],
        )
        log.info(f"Config summary saved in {absolute_path}/{summary_title}.pdf")
    else:
        log.info("Config summary is empty")


def config_summary(all_data, module_type, ordered_chips, absolute_path, summary_title):
    all_imgs = []

    plot = {}
    plot["data"] = {}

    for n in range(len(all_data)):
        for geomId, test in enumerate(all_data[n]):
            format_data(plot, test, geomId)
        try:
            plotter = plot_module_histo(
                plot, test, module_type, "", [n["name"] for n in ordered_chips]
            )
            fill_pdf_summary(plotter, all_imgs)
        except Exception as e:
            log.warning(f"Failed plotting: {e}")

    if all_imgs:
        summary = [Image.open(p).convert("RGB") for p in all_imgs]
        summary[0].save(
            f"{absolute_path}/{summary_title}.pdf",
            save_all=True,
            append_images=summary[1:],
        )
        log.info(f"Config summary saved in {absolute_path}/{summary_title}.pdf")
    else:
        log.info("Config summary is empty")


@app.command()
def main(
    connectivity_files: List[Path] = OPTIONS["connectivity_files"],
    input_folders: List[Path] = OPTIONS["input_folder"],
    scan_directory: Path = OPTIONS["scan_directory"],
    per_chip: bool = OPTIONS["per_chip"],
    verbosity: LogLevel = OPTIONS["verbosity"],
):
    log.setLevel(verbosity.value)

    all_modules_configs = []
    all_paths = []

    if connectivity_files:
        for conn in connectivity_files:
            config_list = get_configs_from_connectivity(load_data(conn))
            absolute_path = Path(conn).parent
            all_modules_configs.append(config_list)
            all_paths.append(absolute_path)
    elif input_folders:
        for input_folder in input_folders:
            config_list = [
                str(f.name)
                for f in Path(input_folder).iterdir()
                if f.is_file and "0x" in f.name and ".json" in f.name
            ]
            absolute_path = input_folder
            all_modules_configs.append(config_list)
            all_paths.append(absolute_path)
    else:
        config_list = [
            str(f.name)
            for f in Path(scan_directory).iterdir()
            if f.is_file() and ".after" in f.name
        ]
        absolute_path = scan_directory
        all_modules_configs.append(config_list)
        all_paths.append(absolute_path)
        log.info("Plotting will be done per chip")
        per_chip = True

    for i, (module_config, path) in enumerate(zip(all_modules_configs, all_paths)):
        module_data = []
        for chip_config in module_config:
            module_data.append(load_data(str(path) + "/" + chip_config))

        log.info(f"Plotting module {i + 1}")

        if per_chip:
            config_summary_perchip(module_data, path, f"config_summary_perchip_{i}")
        else:
            module_type, ordered_chips = get_moduletype_ordered_chips(module_data)

            if not module_type:
                sys.exit()

            all_data = []
            for chip in ordered_chips:
                all_data.append(data_from_config(chip["config"]))
            all_data = list(map(list, zip(*all_data)))

            config_summary(
                all_data, module_type, ordered_chips, path, f"config_summary_{i}"
            )
