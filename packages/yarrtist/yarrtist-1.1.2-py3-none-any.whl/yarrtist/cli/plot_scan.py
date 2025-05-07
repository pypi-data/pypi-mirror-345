from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import List

import numpy as np
import typer
from PIL import Image

from yarrtist.cli.globals import CONTEXT_SETTINGS, OPTIONS, LogLevel
from yarrtist.plotter.core_functions import (
    plot_fe_config,
    plot_fe_histo,
    plot_module_histo,
)
from yarrtist.utils.utils import (
    create_img_grid,
    data_from_config,
    fill_pdf_summary,
    format_broken_data,
    format_data,
    get_configs_chips_from_scandir,
    get_configs_from_connectivity,
    get_configs_from_scanlog,
    get_moduletype_ordered_chips,
    get_tests_chips_from_scandir,
    load_data,
)

logging.basicConfig(format="[%(levelname)s] %(message)s")
log = logging.getLogger("YARRtist")

app = typer.Typer(context_settings=CONTEXT_SETTINGS)


################## plot module chip by chip ######################


def summary_perchip(scan_dir, tests_names, chip_names, summary_title, failing):
    all_imgs = []
    for c in chip_names:
        log.info(f"Plotting for FE {c}")
        for t in tests_names:
            try:
                log.debug(f"Plotting {t}")
                data = load_data(f"{scan_dir}/{c}_{t}.json")
            except Exception:
                log.debug("Test not found for this chip, skipping")
                continue
            try:
                plotter = plot_fe_histo(data, c)
                fill_pdf_summary(plotter, all_imgs)
                if failing and data.get("Name") in [
                    "NoiseMap-0",
                    "ThresholdMap-0",
                    "OccupancyMap",
                    "NoiseOccupancy",
                    "Occupancy",
                ]:
                    data["Name"] = data["Name"] + " - Failures"
                    plotter = plot_fe_histo(data, c, True)
                    fill_pdf_summary(plotter, all_imgs)
            except Exception as e:
                log.warning(f"Failed plotting {t}: {e}")

    if all_imgs:
        summary = [Image.open(p).convert("RGB") for p in all_imgs]

        summary[0].save(
            f"{scan_dir}/{summary_title}.pdf",
            save_all=True,
            append_images=summary[1:],
        )
        log.info(f"Plot summary saved in {scan_dir}/{summary_title}.pdf")
    else:
        log.info("Plot summary is empty")


def config_summary_perchip(scan_dir, files_list, chip_names, summary_title):
    all_imgs = []

    for chip in chip_names:
        configs = {
            "before": [f for f in files_list if ".before" in f and chip in f],
            "after": [f for f in files_list if ".after" in f and chip in f],
        }
        tdac_distr = {}
        for ba, config in configs.items():
            if len(config) == 0:
                continue
            images = []
            config_data = load_data(f"{scan_dir}/{config[0]}")
            try:
                plotters = plot_fe_config(config_data, f"{chip} ({ba})")
                for k in plotters:
                    if k != "TDAC_1d":
                        fill_pdf_summary(plotters[k], images)
                chip_img = create_img_grid(images, (2, 2), f"{chip} ({ba})")
                all_imgs.append(chip_img)
                tdac_distr[f"{ba}"] = plotters["TDAC_1d"]
            except Exception:
                log.warning("Failed to plot: {e}")
        try:
            tdac_imgs = []
            for _k, p in tdac_distr.items():
                fill_pdf_summary(p, tdac_imgs)
            chip_img = create_img_grid(tdac_imgs, (1, 2), "")
            all_imgs.append(chip_img)
        except Exception:
            log.warning("Failed to plot: {e}")

    if all_imgs:
        summary = [p.convert("RGB") for p in all_imgs]
        summary[0].save(
            f"{scan_dir}/{summary_title}.pdf",
            save_all=True,
            append_images=all_imgs[1:],
        )
        log.info(f"Config summary saved in {scan_dir}/{summary_title}.pdf")
    else:
        log.info("Config summary is empty")


################### summary of module from YARR scan directory ###################
def module_summary(
    files_list,
    tests_names,
    module_type,
    ordered_chips,
    scan_dir,
    summary_title,
    failing,
):
    images = []

    for test in tests_names:
        plot = {}
        plot["data"] = {}

        log.info(f"Plotting {test}")
        not_found = 0

        for geomId, item in enumerate(ordered_chips):
            chip = item.get("name")
            ctype = item.get("type")
            file_name = f"{chip}_{test}.json"
            log.debug(f"Plotting for chip {geomId + 1}: {chip}")
            if file_name not in files_list:
                log.debug(f"Chip {chip} not found, filling with 0s")
                not_found += 1
                format_broken_data(plot, test, ctype, geomId)
                continue

            data = load_data(f"{scan_dir}/{file_name}")
            format_data(plot, data, geomId)

        if (not_found == 4 and module_type == "Quad") or (
            not_found == 3 and module_type == "Triplet"
        ):
            log.debug("Skipping whole test for this module")
            continue
        try:
            plotter = plot_module_histo(
                plot, data, module_type, "", [n.get("name") for n in ordered_chips]
            )
            fill_pdf_summary(plotter, images)
            if failing and plot.get("title") in [
                "NoiseMap-0",
                "ThresholdMap-0",
                "OccupancyMap",
                "NoiseOccupancy",
                "Occupancy",
            ]:
                plot["title"] = plot.get("title") + " - Failures"
                plotter = plot_module_histo(
                    plot,
                    data,
                    module_type,
                    "",
                    [n.get("name") for n in ordered_chips],
                    True,
                )
                fill_pdf_summary(plotter, images)
        except Exception:
            log.warning("Failed to plot {test}: {e}")

    if images:
        summary = [Image.open(p).convert("RGB") for p in images]
        summary[0].save(
            f"{scan_dir}/{summary_title}.pdf",
            save_all=True,
            append_images=summary[1:],
        )
        log.info(f"Plot summary saved in {scan_dir}/{summary_title}.pdf")
    else:
        log.info("Plot summary is empty")


################### summary of module config from YARR scan directory ###################
def module_config_summary(
    files_list, module_type, ordered_chips, scan_dir, summary_title
):
    all_data_before = []
    all_data_after = []
    all_imgs = []
    for _geomId, chip in enumerate(ordered_chips):
        ba_configs = [f for f in files_list if chip.get("name") in f]
        if len(ba_configs) == 0:
            all_data_before.append([{}] * 5)
            all_data_after.append([{}] * 5)
            continue
        for conf in ba_configs:
            if ".before" in conf:
                all_data_before.append(
                    data_from_config(load_data(f"{scan_dir}/{conf}"))
                )
            elif ".after" in conf:
                all_data_after.append(data_from_config(load_data(f"{scan_dir}/{conf}")))

    all_data_before = list(map(list, zip(*all_data_before)))
    all_data_after = list(map(list, zip(*all_data_after)))

    for n in range(len(all_data_after)):
        plot_before = {}
        plot_after = {}
        plot_before["data"] = {}
        plot_after["data"] = {}
        images = []
        for geomId, (tb, ta) in enumerate(zip(all_data_before[n], all_data_after[n])):
            if not tb or not ta:
                plot_before["data"].update({geomId: np.zeros((400, 384))})
                plot_after["data"].update({geomId: np.zeros((400, 384))})
                continue
            format_data(plot_before, tb, geomId)
            plot_before["title"] = plot_before["title"] + " (before)"
            format_data(plot_after, ta, geomId)
            plot_after["title"] = plot_after["title"] + " (after)"
        try:
            plotter = plot_module_histo(
                plot_before, tb, module_type, "", [n.get("name") for n in ordered_chips]
            )
            fill_pdf_summary(plotter, images)
            plotter = plot_module_histo(
                plot_after, ta, module_type, "", [n.get("name") for n in ordered_chips]
            )
            fill_pdf_summary(plotter, images)
            all_imgs.append(create_img_grid(images, (1, 2)))
        except Exception as e:
            log.warning(f"Failed plotting: {e}")

    if all_imgs:
        summary = [p.convert("RGB") for p in all_imgs]

        summary[0].save(
            f"{scan_dir}/{summary_title}.pdf",
            save_all=True,
            append_images=all_imgs[1:],
        )
        log.info(f"Config summary saved in {scan_dir}/{summary_title}.pdf")
    else:
        log.info("Config summary is empty")


@app.command()
def main(
    connectivity_files: List[Path] = OPTIONS["connectivity_files"],
    input_folders: List[Path] = OPTIONS["input_folder"],
    scan_directory: Path = OPTIONS["scan_directory"],
    per_chip: bool = OPTIONS["per_chip"],
    config_summary: bool = OPTIONS["config_summary"],
    failing: bool = OPTIONS["failing"],
    verbosity: LogLevel = OPTIONS["verbosity"],
):
    log.setLevel(verbosity.value)

    test_files_list, tests_names, test_chip_names = get_tests_chips_from_scandir(
        scan_directory
    )
    config_files_list, config_chip_names = get_configs_chips_from_scandir(
        scan_directory
    )

    if per_chip:
        log.info("Plotting module scan summary, divided per chip")

        summary_perchip(
            scan_directory, tests_names, test_chip_names, "summary_perchip", failing
        )

        if config_summary:
            log.info("Plotting module config summary, divided per chip")

            config_summary_perchip(
                scan_directory,
                config_files_list,
                config_chip_names,
                "config_summary_perchip",
            )
    else:
        log.info("Plotting module scan summary")

        if not (connectivity_files or input_folders):
            module_configs = get_configs_from_scanlog(
                load_data(f"{scan_directory}/scanLog.json")
            )
        else:
            module_configs = []
            if connectivity_files:
                for connectivity in connectivity_files:
                    chip_configs = []
                    config_dir = Path(connectivity).parent
                    connectivity_data = load_data(connectivity)
                    for chip in get_configs_from_connectivity(connectivity_data):
                        chip_configs.append(f"{config_dir}/{chip}")
                    module_configs.append(chip_configs)
            if input_folders:
                for input_folder in input_folders:
                    chip_configs = [
                        str(input_folder) + "/" + str(f.name)
                        for f in Path(input_folder).iterdir()
                        if f.is_file and "0x" in f.name and ".json" in f.name
                    ]
                    module_configs.append(chip_configs)

        for i, module in enumerate(module_configs):
            log.info(f"Plotting for module {i + 1}")
            module_data = []
            for chip in module:
                module_data.append(load_data(f"{chip}"))

            module_type, ordered_chips = get_moduletype_ordered_chips(module_data)
            if module_type:
                log.debug(f"Module is a {module_type}")
            else:
                sys.exit()

            module_summary(
                test_files_list,
                tests_names,
                module_type,
                ordered_chips,
                scan_directory,
                f"module_summary_{i}",
                failing,
            )
            if config_summary:
                log.info("Plotting module config summary")
                module_config_summary(
                    config_files_list,
                    module_type,
                    ordered_chips,
                    scan_directory,
                    f"module_config_summary_{i}",
                )
