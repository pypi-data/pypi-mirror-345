from __future__ import annotations

import contextlib
import importlib.resources
import json
import logging
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.stats import norm

import yarrtist.utils.fonts

logger = logging.getLogger("YARRtist")


def get_tests_chips_from_scandir(scan_dir):
    tests_names = []
    chip_names = []

    files_list = [
        f.name
        for f in Path(scan_dir).iterdir()
        if f.is_file()
        and "0x" in f.name
        and all(layer not in f.name for layer in ["L0", "L1", "L2", "R0"])
        and ".json" in f.name
    ]

    for f in files_list:
        try:
            c = f.split("_", 1)
            ct = c[1]
            cn = c[0]
            tests_names.append(ct.split(".")[0])
            chip_names.append(cn)
        except IndexError:
            continue

    return files_list, list(set(tests_names)), list(set(chip_names))


def get_configs_chips_from_scandir(scan_dir):
    chip_names = []

    files_list = [
        f.name
        for f in Path(scan_dir).iterdir()
        if (f.is_file() and ".before" in f.name) or (f.is_file() and ".after" in f.name)
    ]

    for f in files_list:
        try:
            cn = f.split("_", 1)[0]
            chip_names.append(cn)
        except IndexError:
            continue

    return files_list, list(set(chip_names))


def load_data(input_data):
    with Path(input_data).open() as file:
        return json.load(file)


def get_configs_from_scanlog(scanlog):
    all_paths = []
    common_path = ""

    logger.info("Trying to find chips configuration files")

    for conn in scanlog.get("connectivity"):
        module_paths = []
        for chip in conn.get("chips"):
            chip_path = Path(chip.get("__config_path__") or chip.get("config"))
            if Path(common_path + str(chip_path)).exists():
                logger.debug(f"Found chip config: {common_path + str(chip_path)}")
                module_paths.append(common_path + str(chip_path))
                continue
            for path in Path("/").rglob(chip_path.name):
                # logger.debug(path)
                if str(path).endswith(str(chip_path)):
                    logger.debug(f"Found chip config: {path}")
                    module_paths.append(str(path))
                    try:
                        common_path = str(path).removesuffix(str(chip_path))
                    except Exception:
                        common_path = str(path)[: -len(str(chip_path))]
                    break
        all_paths.append(module_paths)

    return all_paths


def get_chip_type_from_config(config):
    chiptype = ""
    try:
        chiptype = next(iter(config.keys()))
    except IndexError:
        logger.error("One of your chip configuration files is empty")

    if chiptype not in {"RD53B", "ITKPIXV2"}:
        logger.warning(
            "Chip name in configuration not one of expected chip names (RD53B or ITKPIXV2)"
        )
    return chiptype


def get_geomId_sn_from_config(config_data):
    chip_type = get_chip_type_from_config(config_data)
    config_parameter = config_data[chip_type].get("Parameter", []) if chip_type else {}
    chip_id = config_parameter.get("ChipId", 0)
    chip_name = config_parameter.get("Name", "")

    if chip_id == 12:
        return 1, chip_name
    if chip_id == 13:
        return 2, chip_name
    if chip_id == 14:
        return 3, chip_name
    if chip_id == 15:
        return 4, chip_name
    return chip_id, chip_name


def get_moduletype_ordered_chips(module):
    if len(module) == 3:
        module_type = "Triplet"
    elif len(module) == 4:
        module_type = "Quad"
    else:
        logger.error("Length doesn't match a known module type")
        return None, None

    ordered_chips = [{}] * len(module)
    for chip in module:
        geomId, name = get_geomId_sn_from_config(chip)
        ctype = get_chip_type_from_config(chip)
        ordered_chips[geomId - 1] = {
            "name": name,
            "type": ctype,
            "config": chip,
        }

    return module_type, ordered_chips


def format_broken_data(plot, test, ctype, geomId):
    if "InjVcalDiff_Map" in test:
        plot["data"].update(
            {
                geomId: np.zeros((153600, 101))
                if ctype == "ITKPIXV2"
                else np.zeros((153600, 61))
            }
        )
    elif "InjVcalDiff" in test:
        plot["data"].update(
            {geomId: np.zeros((101, 49)) if ctype == "ITKPIXV2" else np.zeros((61, 49))}
        )
    else:
        plot["data"].update({geomId: np.zeros((400, 384))})


def format_data(plot, data, geomId):
    plot["type"] = data.get("Type")
    plot["title"] = data.get("Name")

    if plot.get("type") == "Histo2d":
        data_arr = np.array(data.get("Data"))
        if None in data_arr:
            data_arr[np.equal(data_arr, None)] = 0
        plot["data"].update({geomId: data_arr})
    else:
        plot["data"].update({geomId: data})


def fill_pdf_summary(plotter, all_imgs, dpi=300):
    buf = BytesIO()
    plotter.savefig(buf, format="png", dpi=dpi)
    all_imgs.append(buf)
    buf.seek(0)
    try:
        plotter.close()
    except Exception:
        contextlib.suppress(Exception)


def create_img_grid(images_buf, grid, text=None):
    spacing = 10
    bkg_color = (255, 255, 255)

    images = [Image.open(p) for p in images_buf]

    max_width = max(img.width for img in images)
    max_height = max(img.height for img in images)

    rows, cols = grid
    total_width = cols * max_width + (cols - 1) * spacing
    total_height = rows * max_height + (rows - 1) * spacing

    text_height = 0
    if text is not None:
        try:
            try:
                with (
                    importlib.resources.files(yarrtist.utils.fonts)
                    .joinpath("Roboto_Condensed-BoldItalic.ttf")
                    .open("rb")
                ) as f:
                    font = ImageFont.truetype(f, 65)
            except Exception:
                with importlib.resources.path(  # pylint: disable=deprecated-method
                    "yarrtist.utils.fonts", "Roboto_Condensed-BoldItalic.ttf"
                ) as font_path:
                    font = ImageFont.truetype(str(font_path), 65)
        except OSError as e:
            logger.debug(e)
            font = ImageFont.load_default()
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        total_height += text_height + spacing

    combined_image = Image.new("RGB", (total_width, total_height), bkg_color)

    for idx, img in enumerate(images):
        row, col = divmod(idx, cols)
        x = col * (max_width + spacing)
        y = row * (max_height + spacing)
        combined_image.paste(img, (x, y))

    if text is not None:
        draw = ImageDraw.Draw(combined_image)
        text_x = (total_width - text_width) // 2
        text_y = total_height - text_height - 150 * spacing
        draw.text((text_x, text_y), text, fill="black", font=font)

    return combined_image


def get_configs_from_connectivity(conn_data):
    configs = []

    for c in conn_data.get("chips", []):
        configs.append(c.get("config"))

    return configs


def data_from_config(config_data):
    plot_data = []

    chip_type = get_chip_type_from_config(config_data)
    config_pixel = config_data[chip_type].get("PixelConfig", []) if chip_type else []

    if config_pixel:
        pixelDataMap = {
            k: [dic[k] for dic in config_pixel] for k in config_pixel[0] if k != "Col"
        }

        for key, data in pixelDataMap.items():
            plot_data.append(
                {
                    "Data": data,
                    "Entries": np.sum(np.array(data)),
                    "Name": key + "-Map",
                    "Overflow": 0.0,
                    "Type": "Histo2d",
                    "Underflow": 0.0,
                    "x": {
                        "AxisTitle": "Column",
                        "Bins": 400,
                        "High": 400.5,
                        "Low": 0.5,
                    },
                    "y": {"AxisTitle": "Row", "Bins": 384, "High": 384.5, "Low": 0.5},
                    "z": {"AxisTitle": key},
                }
            )

            if key == "TDAC":
                flat = np.array(data).flatten()
                bins = np.linspace(-15.5, 15.5, 32)
                hist, _edges = np.histogram(flat, bins=bins)
                plot_data.append(
                    {
                        "Data": hist,
                        "Entries": np.sum(flat),
                        "Name": "TADC-Dist",
                        "Overflow": 0.0,
                        "Type": "Histo1d",
                        "Underflow": 0.0,
                        "x": {
                            "AxisTitle": "TDAC",
                            "Bins": 31,
                            "High": 15.5,
                            "Low": -15.5,
                        },
                        "y": {"AxisTitle": "Number of Pixels"},
                        "z": {"AxisTitle": "z"},
                    }
                )

    else:
        logger.debug("No data for chip")
        for key in ["Enable", "Hitbus", "InjEn", "TDAC"]:
            plot_data.append(
                {
                    "Data": np.zeros((400, 384)),
                    "Entries": 0,
                    "Name": key + "-Map",
                    "Overflow": 0.0,
                    "Type": "Histo2d",
                    "Underflow": 0.0,
                    "x": {
                        "AxisTitle": "Column",
                        "Bins": 400,
                        "High": 400.5,
                        "Low": 0.5,
                    },
                    "y": {"AxisTitle": "Row", "Bins": 384, "High": 384.5, "Low": 0.5},
                    "z": {"AxisTitle": key},
                }
            )

    return plot_data


def fit_Histo1d(freq, bins):
    centers = []
    for i in range(len(bins)):
        centers.append(0.5 * (bins[i] + bins[i - 1]))

    data = np.repeat(centers, freq)

    return norm.fit(data)
