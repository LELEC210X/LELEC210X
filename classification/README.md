# Classification

Files related to the classification part.

## Installation

All dependencies should be installed with the following command:

```bash
poetry install
```

However, you still need to create a Jupyter Python kernel, to be used
within your notebooks:

```bash
poetry run python -m ipykernel install --user --name LELEC210X
```

## Usage

Notebooks should accessed by running:

```bash
poetry run jupyter notebook
# note: on WSL, you cannot open a browser window from the terminal, so run instead
poetry run jupyter notebook --no-browser
# and open one of the links manually (see below).
```

> **WARNING:** you should select the `LELEC210X` kernel prior to running any cell,
> otherwise it will probably not work!

If Jupter does not launch a browser Windows, you can scroll the terminal
and click (<kbd>CTRL</kbd>+<kbd>LEFT CLICK</kbd>) on one of the HTTP links displayed.
