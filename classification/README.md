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

To run the `classify script`, it is recommended to pipe it with the `auth` script, so that the output of `auth` is
directly streamed to `classify`:

```bash
poetry run auth | poetry run classify
```

Of course, you can pass any argument you like to the first or the second command.
Note that changing the output `-o` option from `auth` or the input `-i` option from `classify`
will mean that process piping (`|` is a pipe) will not be possibly anymore.

:warning: Please make sure to use the correct number of Mel vectors and the correct length. A default value is automatically set, but you change it
to match the one you are using! See `poetry run classify --help`.

## Extending your training dataset

By default, the soundfiles dataset is quite small. To improve your performances,
you are encouraged to train your model on a large dataset!

To obtain such a dataset, there are two possibilities:

1. record yourself some audio samples, using a smartphone or else;
2. or use already recorded audio samples you can find online, e.g., on YouTube.

### Downloading audio files from YouTube videos

The easiest way to download audio files from Youtube videos is probably with
`youtube-dl`.

#### Install

```bash
pip install 'git+https://github.com/ytdl-org/youtube-dl.git'
```
You also need to install FFMPEG, see install instructions for
your specific OS.

#### Usage

Obtain the link to the video (do not take the one in the URL bar!):

![image](https://github.com/LELEC210X/LELEC210X/assets/27275099/a561bf41-98fe-41b3-9844-cd33470c517b)

```bash
youtube-dl -x '<path-to-video>`
```

### Splitting one large audio file into many

If soundfiles are long enough, it may be intersting to split large audio file into many audio samples,
we provide tools to perform that automatically: <TODO>.
