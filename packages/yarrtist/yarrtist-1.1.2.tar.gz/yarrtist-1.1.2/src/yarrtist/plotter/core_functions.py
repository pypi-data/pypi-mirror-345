from __future__ import annotations

import contextlib
import logging

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm
from scipy.stats import norm

from yarrtist.utils.utils import fit_Histo1d, get_chip_type_from_config

logger = logging.getLogger("YARRtist")


def plot_fe_config(config_data, fe_name=""):
    returnMap = {}

    chip_type = get_chip_type_from_config(config_data)
    config_pixel = config_data[chip_type].get("PixelConfig", []) if chip_type else []

    if config_pixel:
        pixelDataMap = {
            k: [dic[k] for dic in config_pixel] for k in config_pixel[0] if k != "Col"
        }

        for key, data in pixelDataMap.items():
            arr = np.array(data)

            vmin, vmax = 0, 1
            ticks = [0, 1]
            if key.lower() == "tdac":
                vmin, vmax = -15, 15
                ticks = [-15, -10, -5, 0, 5, 10, 15]

            cmap = plt.get_cmap("magma", (vmax - vmin) + 1)

            fig, ax = plt.subplots()
            cax = ax.imshow(arr.T, origin="lower", cmap=cmap, vmin=vmin, vmax=vmax)
            ax.set_title(key, fontsize=22)
            ax.set_xlabel("Column", fontsize=18)
            ax.set_ylabel("Row", fontsize=18)
            fig.tight_layout()

            cb = fig.colorbar(cax, label="Value", ax=ax)
            cb.set_ticks(ticks)
            for t in cb.ax.get_yticklabels():
                t.set_fontsize(12)

            returnMap[key] = fig

            plt.close(fig)

            if key == "TDAC":
                flat = arr.flatten()
                bins = np.linspace(-15.5, 15.5, 32)
                fig, ax = plt.subplots()
                cax = ax.hist(flat, bins=bins)
                ax.set_title("TDAC " + fe_name, fontsize=22)
                ax.set_xlabel("TDAC", fontsize=18)
                # fig.tight_layout()

                returnMap["TDAC_1d"] = fig

                plt.close(fig)

    return returnMap


def plot_fe_histo(data, chip_name="", failing_pixels=False):
    if data.get("Type") == "Histo1d":
        bins = np.linspace(
            data.get("x").get("Low"),
            data.get("x").get("High"),
            data.get("x").get("Bins"),
        )

        fit_label = f"(Uf: {data.get('Underflow')},\n Of: {data.get('Overflow')})"
        if data.get("Name") == "ThresholdDist-0" or data.get("Name") == "NoiseDist-0":
            mu, sigma = fit_Histo1d(data.get("Data"), bins)
            y = norm.pdf(bins, mu, sigma) * np.sum(data.get("Data")) * np.diff(bins)[0]
            plt.plot(bins, y, "r--", label="fit")
            fit_label = f"(µ: {mu:.2f}, σ: {sigma:.2f},\n Uf: {data.get('Underflow')},\n Of: {data.get('Overflow')})"

        plt.hist(bins, len(bins), weights=data.get("Data"), label=f"{fit_label}")
        plt.legend()

    elif data.get("Type") == "Histo2d":
        arr = np.array(data.get("Data"))
        if None in arr:
            arr[np.equal(arr, None)] = 0

        is_config = np.all(np.isin(arr, [0, 1]))

        ma = np.ma.MaskedArray(arr, arr <= 0)
        min_nonzero_value = np.ma.min(ma)
        max_nonzero_value = np.ma.max(ma)
        min_max_ratio = max_nonzero_value / (min_nonzero_value + 1.0e-19)

        set_log_scale = min_nonzero_value > 0 and min_max_ratio > 100

        if set_log_scale:
            arr += min_nonzero_value * 1.0e-2
            plt.imshow(
                arr.T,
                origin="lower",
                cmap="turbo",
                norm=LogNorm(min_nonzero_value * 0.5, max_nonzero_value * 2),
            )
        else:
            plt.imshow(
                arr.T, origin="lower", cmap="turbo" if not is_config else "magma"
            )

        cb = plt.colorbar(label=data.get("z").get("AxisTitle"))
        for t in cb.ax.get_yticklabels():
            t.set_fontsize(12)

        if failing_pixels:
            valid_rows = ~(arr == np.zeros((400, 384))).all(axis=1)
            valid_cols = ~(arr == np.zeros((400, 384))).all(axis=0)

            valid_mask = np.zeros((400, 384), dtype=bool)

            valid_mask = np.outer(valid_rows, valid_cols)

            mean_occ = np.mean(arr[valid_mask])

            is_low = (arr < mean_occ / 2) & valid_mask
            is_high = (arr > mean_occ * 2) & valid_mask

            x_low, y_low = np.where(is_low)
            x_high, y_high = np.where(is_high)

            plt.scatter(x_low, y_low, s=3, c="black", marker="s", label="Low Occ.")
            plt.scatter(x_high, y_high, s=3, c="fuchsia", marker="s", label="High Occ.")
            plt.legend(fontsize=5)

    else:
        logger.error("unexpected data type")
        return None

    plt.title(data.get("Name") + f" {chip_name}", fontsize=22)
    plt.xlabel(data.get("x").get("AxisTitle"), fontsize=18)
    plt.ylabel(data.get("y").get("AxisTitle"), fontsize=18)
    plt.tight_layout()

    return plt


def plot_module_histo(
    plot, data, moduleType, serialNumber="", fe_serialNumbers=None, failing_pixels=False
):
    if fe_serialNumbers is None:
        fe_serialNumbers = ["", "", "", ""]

    if plot.get("type") == "Histo2d" and plot.get("title") != "InjVcalDiff":
        if moduleType == "Triplet":
            plt.figure(figsize=(18, 16))
            ax = plt.gca()
            ax.tick_params(axis="both", which="major", labelsize=14)

            module = np.concatenate(
                (
                    plot.get("data")[0].T,
                    plot.get("data")[1].T,
                    plot.get("data")[2].T,
                ),
                axis=1,
            )

            is_config = np.all(np.isin(module, [0, 1]))

            if failing_pixels:
                valid_rows_1 = ~(module[:384, :400] == np.zeros((384, 400))).all(axis=1)
                valid_cols_1 = ~(module[:384, :400] == np.zeros((384, 400))).all(axis=0)
                valid_rows_2 = ~(module[:384, 400:800] == np.zeros((384, 400))).all(
                    axis=1
                )
                valid_cols_2 = ~(module[:384, 400:800] == np.zeros((384, 400))).all(
                    axis=0
                )
                valid_rows_3 = ~(module[:384, 800:1200] == np.zeros((384, 400))).all(
                    axis=1
                )
                valid_cols_3 = ~(module[:384, 800:1200] == np.zeros((384, 400))).all(
                    axis=0
                )

                valid_mask = np.zeros((384, 1200), dtype=bool)

                valid_mask[:384, :400] = np.outer(valid_rows_1, valid_cols_1)
                valid_mask[:384, 400:800] = np.outer(valid_rows_2, valid_cols_2)
                valid_mask[:384, 800:1200] = np.outer(valid_rows_3, valid_cols_3)

                mean_occ = np.mean(module[valid_mask])

                is_low = (module < mean_occ / 2) & valid_mask
                is_high = (module > mean_occ * 2) & valid_mask

                y_low, x_low = np.where(is_low)
                y_high, x_high = np.where(is_high)

            module = np.array(module, dtype=float)
            ma = np.ma.MaskedArray(module, module <= 0)
            min_nonzero_value = np.ma.min(ma)
            max_nonzero_value = np.ma.max(ma)
            min_max_ratio = max_nonzero_value / (min_nonzero_value + 1.0e-19)

            set_log_scale = min_nonzero_value > 0 and min_max_ratio > 100

            if set_log_scale:
                module += min_nonzero_value * 1.0e-2
                plt.imshow(
                    module,
                    origin="lower",
                    cmap="turbo",
                    norm=LogNorm(min_nonzero_value * 0.5, max_nonzero_value * 2),
                )
            else:
                plt.imshow(
                    module, origin="lower", cmap="turbo" if not is_config else "magma"
                )

            plt.title(
                "Triplet Module: " + serialNumber + " " + plot.get("title"),
                fontsize=18,
            )
            ax.text(
                200,
                -20,
                "FE1: " + fe_serialNumbers[0],
                horizontalalignment="center",
                verticalalignment="top",
                size=10,
                color="blue",
            )
            ax.text(
                600,
                -20,
                "FE2: " + fe_serialNumbers[1],
                horizontalalignment="center",
                verticalalignment="top",
                size=10,
                color="blue",
            )
            ax.text(
                1000,
                -20,
                "FE3: " + fe_serialNumbers[2],
                horizontalalignment="center",
                verticalalignment="top",
                size=10,
                color="blue",
            )

            if module.shape == (384, 1200):
                ax.set_xticks(np.arange(0, 1200 + 1, 400))
                ax.set_yticks(np.arange(0, 384 + 1, 384))
                ax.set_xticks(np.arange(0, 1200 + 1, 16), minor=True)
                ax.set_yticks(np.arange(0, 384 + 1, 16), minor=True)

                ax.grid(which="major", color="black", linestyle="solid", linewidth=0.5)

            plt.xlabel("Column", fontsize=18)
            plt.ylabel("Row", fontsize=18)
            cb = plt.colorbar(
                label=data.get("z").get("AxisTitle"), orientation="horizontal"
            )
            for t in cb.ax.get_yticklabels():
                t.set_fontsize(12)

            if failing_pixels:
                plt.scatter(x_low, y_low, s=3, c="black", marker="s", label="Low Occ.")
                plt.scatter(
                    x_high, y_high, s=3, c="fuchsia", marker="s", label="High Occ."
                )
                plt.legend(fontsize=5)

        else:
            up = np.zeros((400, 768))
            logger.debug(f"{plot.get('data')[0].shape}, {plot.get('data')[3].shape}")
            try:
                up = np.concatenate(
                    (
                        np.flip(np.flip(plot.get("data")[0], axis=0), axis=1),
                        plot.get("data")[3],
                    ),
                    axis=1,
                )
            except Exception:
                try:
                    up = np.concatenate(
                        (
                            np.flip(np.flip(plot.get("data")[0], axis=0), axis=1),
                            np.zeros((400, 384)),
                        ),
                        axis=1,
                    )
                except Exception:
                    with contextlib.suppress(Exception):
                        up = np.concatenate(
                            (np.zeros((400, 384)), plot.get("data")[3]), axis=1
                        )

            down = np.zeros((400, 768))
            logger.debug(f"{plot.get('data')[1].shape}, {plot.get('data')[2].shape}")
            try:
                down = np.concatenate(
                    (
                        np.flip(np.flip(plot.get("data")[1], axis=0), axis=1),
                        plot.get("data")[2],
                    ),
                    axis=1,
                )
            except Exception:
                try:
                    down = np.concatenate(
                        (
                            np.flip(np.flip(plot.get("data")[1], axis=0), axis=1),
                            np.zeros((400, 384)),
                        ),
                        axis=1,
                    )
                except Exception:
                    with contextlib.suppress(Exception):
                        down = np.concatenate(
                            (np.zeros((400, 384)), plot.get("data")[1]), axis=1
                        )

            try:
                module = np.concatenate((down, up), axis=0)
            except Exception as e:
                logger.info(f"Plotting failed: str{e}")

            is_config = np.all(np.isin(module, [0, 1]))

            if failing_pixels:
                valid_rows_1 = ~(module[:400, :384] == np.zeros((400, 384))).all(axis=1)
                valid_cols_1 = ~(module[:400, :384] == np.zeros((400, 384))).all(axis=0)
                valid_rows_2 = ~(module[400:800, :384] == np.zeros((400, 384))).all(
                    axis=1
                )
                valid_cols_2 = ~(module[400:800, :384] == np.zeros((400, 384))).all(
                    axis=0
                )
                valid_rows_3 = ~(module[:400, 384:768] == np.zeros((400, 384))).all(
                    axis=1
                )
                valid_cols_3 = ~(module[:400, 384:768] == np.zeros((400, 384))).all(
                    axis=0
                )
                valid_rows_4 = ~(module[400:800, 384:768] == np.zeros((400, 384))).all(
                    axis=1
                )
                valid_cols_4 = ~(module[400:800, 384:768] == np.zeros((400, 384))).all(
                    axis=0
                )

                valid_mask = np.zeros((800, 768), dtype=bool)

                valid_mask[:400, :384] = np.outer(valid_rows_1, valid_cols_1)
                valid_mask[400:800, :384] = np.outer(valid_rows_2, valid_cols_2)
                valid_mask[:400, 384:768] = np.outer(valid_rows_3, valid_cols_3)
                valid_mask[400:800, 384:768] = np.outer(valid_rows_4, valid_cols_4)

                mean_occ = np.mean(module[valid_mask])

                is_low = (module < mean_occ / 2) & valid_mask
                is_high = (module > mean_occ * 2) & valid_mask

                y_low, x_low = np.where(is_low)
                y_high, x_high = np.where(is_high)

            module = module.astype("float")
            ma = np.ma.MaskedArray(module, module <= 0)
            min_nonzero_value = np.ma.min(ma)
            max_nonzero_value = np.ma.max(ma)
            min_max_ratio = max_nonzero_value / (min_nonzero_value)

            set_log_scale = min_nonzero_value > 0 and min_max_ratio > 100

            plt.figure(figsize=(12, 9))

            if set_log_scale:
                module += min_nonzero_value * 1.0e-2
                plt.imshow(
                    module,
                    origin="lower",
                    cmap="turbo",
                    extent=[-384, 384, -400, 400],
                    norm=LogNorm(min_nonzero_value * 0.5, max_nonzero_value * 2),
                )
            else:
                plt.imshow(
                    module,
                    origin="lower",
                    cmap="turbo" if not is_config else "magma",
                    extent=[-384, 384, -400, 400],
                )

            ax = plt.gca()
            ax.tick_params(axis="both", which="major", labelsize=10)

            ax.set_yticks(np.arange(-400, 400 + 1, 400))
            ax.set_xticks(np.arange(-384, 384 + 1, 384))
            ax.set_yticks(np.arange(-400, 400 + 1, 16), minor=True)
            ax.set_xticks(np.arange(-384, 384 + 1, 16), minor=True)

            ax.grid(which="major", color="black", linestyle="solid", linewidth=0.5)

            ax.text(
                -415,
                200,
                "FE1: " + fe_serialNumbers[0],
                horizontalalignment="center",
                verticalalignment="center",
                size=12,
                color="blue",
                rotation=-90,
            )
            ax.text(
                -415,
                -200,
                "FE2: " + fe_serialNumbers[1],
                horizontalalignment="center",
                verticalalignment="center",
                size=12,
                color="blue",
                rotation=-90,
            )
            ax.text(
                415,
                -200,
                "FE3: " + fe_serialNumbers[2],
                horizontalalignment="center",
                verticalalignment="center",
                size=12,
                color="blue",
                rotation=90,
            )
            ax.text(
                415,
                200,
                "FE4: " + fe_serialNumbers[3],
                horizontalalignment="center",
                verticalalignment="center",
                size=12,
                color="blue",
                rotation=90,
            )

            plt.title(
                "Quad Module: " + serialNumber + " " + plot.get("title"),
                fontsize=18,
            )
            plt.xlabel("Row", fontsize=18)
            plt.ylabel("Column", fontsize=18)
            cb = plt.colorbar(label=data.get("z").get("AxisTitle"))
            for t in cb.ax.get_yticklabels():
                t.set_fontsize(12)

            if failing_pixels:
                plt.scatter(
                    x_low - 384,
                    y_low - 400,
                    s=3,
                    c="black",
                    marker="s",
                    label="Low Occ.",
                )
                plt.scatter(
                    x_high - 384,
                    y_high - 400,
                    s=3,
                    c="fuchsia",
                    marker="s",
                    label="High Occ.",
                )
                plt.legend(fontsize=5)

    elif plot.get("type") == "Histo2d" and plot.get("title") == "InjVcalDiff":
        logger.debug(
            f"{plot.get('data')[0].shape}, {plot.get('data')[1].shape}, {plot.get('data')[2].shape}, {plot.get('data')[2].shape}"
        )
        try:
            module = np.sum([d for k, d in plot.get("data").items()], axis=0)
        except Exception as e:
            logger.info(f"Plotting failed: str{e}")

        ma = np.ma.MaskedArray(module, module <= 0)
        min_nonzero_value = np.ma.min(ma)
        max_nonzero_value = np.ma.max(ma)
        min_max_ratio = max_nonzero_value / (min_nonzero_value + 1.0e-19)

        set_log_scale = min_nonzero_value > 0 and min_max_ratio > 100

        plt.figure(figsize=(12, 9))
        if set_log_scale:
            module += min_nonzero_value * 1.0e-2
            plt.imshow(
                module.T,
                origin="lower",
                cmap="turbo",
                norm=LogNorm(min_nonzero_value * 0.5, max_nonzero_value * 2),
            )
        else:
            plt.imshow(
                module.T, origin="lower", cmap="turbo" if not is_config else "magma"
            )

        ax = plt.gca()
        ax.tick_params(axis="both", which="major", labelsize=10)

        plt.title("Module: " + serialNumber + " " + plot.get("title"), fontsize=18)
        plt.xlabel(xlabel=data.get("x").get("AxisTitle"), fontsize=18)
        plt.ylabel(ylabel=data.get("y").get("AxisTitle"), fontsize=18)
        cb = plt.colorbar(label=data.get("z").get("AxisTitle"))
        for t in cb.ax.get_yticklabels():
            t.set_fontsize(12)

    elif plot.get("type") == "Histo1d":  ## add stats
        plt.figure(figsize=(12, 9))
        plt.title("Module: " + serialNumber + " " + plot.get("title"), fontsize=18)

        for geomId, d in plot.get("data").items():
            try:
                bins = np.linspace(
                    d.get("x").get("Low"),
                    d.get("x").get("High"),
                    d.get("x").get("Bins"),
                )

                fit_label = ""
                if (
                    plot.get("title") == "ThresholdDist-0"
                    or plot.get("title") == "NoiseDist-0"
                ):
                    mu, sigma = fit_Histo1d(d.get("Data"), bins)
                    y = (
                        norm.pdf(bins, mu, sigma)
                        * np.sum(d.get("Data"))
                        * np.diff(bins)[0]
                    )
                    plt.plot(bins, y, "r--")
                    fit_label = f"µ: {mu:.2f}, σ: {sigma:.2f}, "

                plt.hist(
                    bins,
                    len(bins),
                    weights=d.get("Data"),
                    histtype="step",
                    label=f"FE{geomId + 1}: "
                    + fe_serialNumbers[geomId]
                    + f"({fit_label}Uf: {data.get('Underflow')}, Of: {data.get('Overflow')})",
                )
                plt.legend(loc="upper right", fontsize=10)
            except AttributeError:
                continue

            with contextlib.suppress(AttributeError):
                plt.xlabel(d.get("x").get("AxisTitle"), fontsize=18)
            plt.ylabel(d.get("y").get("AxisTitle"), fontsize=18)

        plt.tight_layout()

    return plt
