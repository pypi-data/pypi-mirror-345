# Plots

## Overview

Four different commands are available:

- plot-single-test
- plot-single-config
- plot-scan
- plot-connectivity

For general help, use

```
yarrtist plots -h
yrts plots -h

```

while for help with a specific command

```
yarrtist plots <command> -h
yrts plots <command> -h

```

by substituting `<command>` with one of the ones listed above.

## Single test

Single 1d or 2d plot for a single map or distribution `json` inside `YARR` scan

```
yarrtist plots plot-single-test -i <data>
yrts plots plot-single-test -i <data>

```

Output is a `png` file inside the same directory of the `json` file.

## Single configuration

Summary of the `json` config file for a single chip

```
yarrtist plots plot-single-config -i <config>
yrts plots plot-single-config -i <config>

```

Output is a `png` file inside the same directory of the `config` file.

## Scan plot

Plot of all the data inside `YARR` scan directory, `connectivity` file of the
module has to be provided in order to define the geometry of the module, by
default a full module plot is done, as well as a comparison of the chips
configuration before and after the scan

```
yarrtist plots plot-scan -c <connectivity> -s <scan_directory>
yrts plots plot-scan -c <connectivity> -s <scan_directory>

```

if the option `--per-chip` is provided, the plot is divided chip by chip (the
position of the plots in the page follows the position of the chips in the
module), while `--config-summary` can be provided to disable configuration
summary plots.

If the scan directory contains results from more than one module, the summary is
done for all of them, by providing more connectivity files

```
yarrtist plots plot-scan -s <scan_directory> -c <connectivity_0> -c <connectivity_1> -c ...
yrts plots plot-scan -s <scan_directory> -c <connectivity_0> -c <connectivity_1> -c ...

```

The summaries are saved in `pdf` files inside the scan directory.

## Connectivity plot

Summary of the chips configuration in a module from its `connectivity` file

```
yarrtist plots plot-connectivity -i <connectivity>
yrts plots plot-connectivity -i <connectivity>

```

The summary is saved in `pdf` files inside the `connectivity` file directory.
