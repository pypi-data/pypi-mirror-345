# Demo

The `typer-repyt` package includes an "extra" that can be installed to show all its features. Each demo focuses on a
particular feature and runs a few examples that demonstrate how the feature can be used in your CLI app.


## Installation

To install the `demo` with `typer-repyt` you need to supply it as an "extra" when installing `typer-repyt`. The
following command can be used:

```bash
pip install typer-repyt[demo]
```


## Running the demo

An entrypoint for the demo is included when it is installed. Simply run:

```bash
typer-repyt-demo
```

If you provide no arguments, it will run all available demos. If you wish to only see the demos
for a particular feature, you can use the `--feature=<feature>` option to target one feature.

To see all available options, run:

```bash
typer-repyt-demo --help
```

## Running the demo in an isolated environment with uv

If you want to run the demo but not include its dependencies in your system python
or an activated virtual environment, you can execute the demo with uv:

```bash
uvx --from=typer-repyt[demo] typer-repyt-demo
```


## Check out the source

You can also examine the demo source to examine how `typer-repyt` is used.

Check out the [source code on Github](https://github.com/dusktreader/typer-repyt/tree/main/src/typer_repyt_demo).
