from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from yarrtist.cli import app


@pytest.fixture
def config_path():
    return Path() / "src" / "yarrtist" / "data" / "example_configs"


@pytest.fixture
def scan_path():
    return Path() / "src" / "yarrtist" / "data" / "example_scans"


@pytest.fixture
def runner():
    return CliRunner(mix_stderr=False)


def test_single_plot(runner, scan_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-single-test",
            "-i",
            scan_path.joinpath("010069_std_analogscan/0x22e4d_OccupancyMap.json"),
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "File saved in" in caplog.text


def test_single_config(runner, config_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-single-config",
            "-i",
            config_path.joinpath("20UPGM23211219/L2_warm/0x22e8c_L2_warm.json"),
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "File saved in" in caplog.text


def test_scan(runner, scan_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-scan",
            "-s",
            scan_path.joinpath("010290_std_analogscan"),
            "--highlight-failures",
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Plot summary saved" in caplog.text
    assert "Config summary saved" in caplog.text


def test_scan_perchip(runner, scan_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-scan",
            "-s",
            scan_path.joinpath("010290_std_analogscan"),
            "--highlight-failures",
            "--per-chip",
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Plot summary saved" in caplog.text
    assert "Config summary saved" in caplog.text


def test_config(runner, config_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-connectivity",
            "-i",
            config_path.joinpath("20UPGM23211219/L2_warm"),
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Config summary saved in" in caplog.text


def test_config_perchip(runner, config_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-connectivity",
            "-c",
            config_path.joinpath("20UPGM23211219/20UPGM23211219_L2_warm.json"),
            "--per-chip",
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Config summary saved in" in caplog.text


def test_broken(runner, scan_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-scan",
            "-s",
            scan_path.joinpath("010069_std_analogscan"),
            "--highlight-failures",
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Plot summary saved" in caplog.text
    assert "Config summary saved" in caplog.text


def test_broken_perchip(runner, scan_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-scan",
            "-s",
            scan_path.joinpath("010069_std_analogscan"),
            "--highlight-failures",
            "--per-chip",
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Plot summary saved" in caplog.text
    assert "Config summary saved" in caplog.text


def test_triplet_scan(runner, scan_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-scan",
            "-s",
            scan_path.joinpath("008847_std_analogscan"),
            "--highlight-failures",
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Plot summary saved" in caplog.text
    assert "Config summary saved" in caplog.text


def test_triplet_scan_perchip(runner, scan_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-scan",
            "-s",
            scan_path.joinpath("008847_std_analogscan"),
            "--highlight-failures",
            "--per-chip",
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Plot summary saved" in caplog.text
    assert "Config summary saved" in caplog.text


def test_triplet_config(runner, config_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-connectivity",
            "-c",
            config_path.joinpath("20UPIM52204106/20UPIM52204106_R0.5_warm.json"),
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Config summary saved in" in caplog.text


def test_triplet_config_perchip(runner, config_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-connectivity",
            "-i",
            config_path.joinpath("20UPIM52204106/R0.5_warm"),
            "--per-chip",
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Config summary saved in" in caplog.text


def test_combined(runner, scan_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-scan",
            "-s",
            scan_path.joinpath("combined_analog_scan"),
            "--highlight-failures",
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Plot summary saved" in caplog.text
    assert "Config summary saved" in caplog.text


def test_combined_config_option(runner, config_path, scan_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-scan",
            "-i",
            config_path.joinpath("20UPGM23211219/L2_warm"),
            "-i",
            config_path.joinpath("20UPGM23211190/L2_warm"),
            "-s",
            scan_path.joinpath("combined_analog_scan"),
            "--highlight-failures",
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Plot summary saved" in caplog.text
    assert "Config summary saved" in caplog.text


def test_combined_conn_option(runner, config_path, scan_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-scan",
            "-c",
            config_path.joinpath("20UPGM23211219/20UPGM23211219_L2_warm.json"),
            "-c",
            config_path.joinpath("20UPGM23211190/20UPGM23211190_L2_warm.json"),
            "-s",
            scan_path.joinpath("combined_analog_scan"),
            "--highlight-failures",
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Plot summary saved" in caplog.text
    assert "Config summary saved" in caplog.text


def test_combined_perchip(runner, scan_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-scan",
            "-s",
            scan_path.joinpath("combined_analog_scan"),
            "--highlight-failures",
            "--per-chip",
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Plot summary saved" in caplog.text
    assert "Config summary saved" in caplog.text


def test_conn_combined_config_option(runner, config_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-connectivity",
            "-i",
            config_path.joinpath("20UPGM23211219/L2_warm"),
            "-i",
            config_path.joinpath("20UPGM23211190/L2_warm"),
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Config summary" in caplog.text
