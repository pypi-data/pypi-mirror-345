# nbdotrun

[![Github Actions Status](https://github.com/gnodar01/nbdotrun/workflows/Build/badge.svg)](https://github.com/gnodar01/nbdotrun/actions/workflows/build.yml)

A JupyterLab extension that will listen for code cell changes and run if ending in dot (`.`) by default, or any other configured trigger symbol.

`shift-enter` to run a code cell is just as fast as `enter .`, so why use this?

It's mostly to support my own workflow.
I use [Jupytext](https://jupytext.readthedocs.io/en/latest/) with its [paired notebooks](https://jupytext.readthedocs.io/en/latest/paired-notebooks.html) feature enabled.
Jupytext allows you to edit your text-only files (e.g. `.py` or `.md`) as though they were notebook files (`json` structured in the `.ipynb` format).
It lets you do this in JupyterLab itself, giving you a standard notebook interface even though underneath there is a simple text file.
However I don't like editing in JupyterLab.
Instead, I like to have the JupyterLab interface open to view rich outputs like images and interactive plots, and to tinker with widgets.
The actual writing of cells however, I prefer to do in a text editor.
Jupytext syncs changes I make in the text editor to the notebook (without needing to reload due to the wonderful [jupyter-collaboration](https://github.com/jupyterlab/jupyter-collaboration) extension).
Sometimes I want the cell I edited in the text editor to also run in JupyterLab so that I can see the output.
I want to do this without having to switch over from the text editor to JupyterLab, going to the edited cell, and running it manually.
So instead I just put `.` at the last line of the edited cell in the text editor, and have it run automatically.

## Requirements

- JupyterLab >= 4.0.0

## Install

To install the extension, execute:

```bash
pip install nbdotrun
```

## Uninstall

To remove the extension, execute:

```bash
pip uninstall nbdotrun
```

## Contributing

### Development install

Note: You will need NodeJS to build the extension package.

The `jlpm` command is JupyterLab's pinned version of
[yarn](https://yarnpkg.com/) that is installed with JupyterLab. You may use
`yarn` or `npm` in lieu of `jlpm` below.

```bash
# Clone the repo to your local environment
# Change directory to the nbdotrun directory
# Install package in development mode
pip install -e "."
# Link your development version of the extension with JupyterLab
jupyter labextension develop . --overwrite
# Rebuild extension Typescript source after making changes
jlpm build
```

You can watch the source directory and run JupyterLab at the same time in different terminals to watch for changes in the extension's source and automatically rebuild the extension.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
jlpm watch
# Run JupyterLab in another terminal
jupyter lab
```

With the watch command running, every saved change will immediately be built locally and available in your running JupyterLab. Refresh JupyterLab to load the change in your browser (you may need to wait several seconds for the extension to be rebuilt).

By default, the `jlpm build` command generates the source maps for this extension to make it easier to debug using the browser dev tools. To also generate source maps for the JupyterLab core extensions, you can run the following command:

```bash
jupyter lab build --minimize=False
```

### Development uninstall

```bash
pip uninstall nbdotrun
```

In development mode, you will also need to remove the symlink created by `jupyter labextension develop`
command. To find its location, you can run `jupyter labextension list` to figure out where the `labextensions`
folder is located. Then you can remove the symlink named `nbdotrun` within that folder.

### Packaging the extension

See [RELEASE](RELEASE.md)
