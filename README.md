# PF_Sherlock

A logfile analysis tool with super powers.

Intended to be hackable in all directions. This lead to a modular architecture
which is mostly done by a composition of modules in `sherlock.py`

## Modules

See `sherlock.py` module variables for a full list of currently implemented
and used components.

* `datasources` -- Places to fetch data from
* `parsers`     -- Processing lines from datasources
* `filters`     -- Filter data from parsers
* `outputs`     -- Show results

## Guide

> I want to read many logfiles in parallel to check what happened during an incident

Define logfiles needed in `config.py` and run pf_sherlock on it.
Check the examples to get an idea of what's possible.

```
pf_sherlock --config /path/to/your/config.py
```

### Installation

```
python setup.py install
```

### Usage

```
usage: pf_sherlock [-h] [-c CONFIG] [-f [{lh,kw} [{lh,kw} ...]]]
                   [-a [ARGS [ARGS ...]]]

---> A logfile analysis tool with super powers <---
  Intended to simplify logfile analysis tasks by aggregating logfiles
  defined in config.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to config file
  -f [{lh,kw} [{lh,kw} ...]], --filter [{lh,kw} [{lh,kw} ...]]
                        List of filters to apply
  -a [ARGS [ARGS ...]], --args [ARGS [ARGS ...]]
                        List of filter arguments to apply. Must match filter
                        list order
```

# Roadmap

* Improve Parser implementations, reduce memory footprint and increase performance
* Leverage usage from interactive environments, e.g. ipython
* More Parser / Filter / Display implementations!
* Output modules: Send results to stdout, another host via mail / http / ...
* Daemon/Snapshot-Mode: save/send compressed result as reaction on event XY
