# Classification

Files related to the classification part.

## Installation

All dependencies should be installed with the following command:

```bash
uv sync
```

However, you still need to create a Jupyter Python kernel, to be used
within your notebooks:

```bash
uv run python -m ipykernel install --user --name LELEC210X
```

> [!WARNING]
> On some platforms, it is possible that your OS is missing the
> necessary packages to play audio, and it will raise
> an error when trying to do so. If that is the case,
> please read [#27](https://github.com/LELEC210X/LELEC210X/issues/27)
> as it possibly contains a solution to your problem.

## Usage

Notebooks should accessed by running:

```bash
uv run jupyter notebook
# note: on WSL, you cannot open a browser window from the terminal, so run instead
uv run jupyter notebook --no-browser
# and open one of the links manually (see below).
```

> [!NOTE]
> You have to select the `LELEC210X` kernel prior to running any cell,
> otherwise it will probably not work! If you are using VS Code, please
> refer to their documentation, to ensure you are using the correct
> virtual environment or kernel.

If Jupyter does not launch a browser window, you can scroll the terminal
and click (<kbd>CTRL</kbd>+<kbd>LEFT CLICK</kbd>) on one of the HTTP links displayed.

To run the `classify script`, it is recommended to pipe it with the `auth` script, so that the output of `auth` is
directly streamed to `classify`:

```bash
uv run auth | uv run classify
```

> [!WARNING]
> On Windows, the above command might stall and not print anything:
> check-out https://github.com/LELEC210X/LELEC210X/issues/77 for possible solutions.

Of course, you can pass any argument you like to the first or the second command.
Note that changing the output `-o` option from `auth` or the input `-i` option from `classify`
will mean that process piping (`|` is a pipe) will not be possibly anymore.

:warning: Please make sure to use the correct number of Mel vectors and the correct length. A default value is automatically set, but you change it
to match the one you are using! See `uv run classify --help`.

## Extending your training dataset

By default, the dataset of sound files is quite small. To improve your performances,
you are encouraged to train your model on a large dataset!

To obtain such a dataset, there are two possibilities:

1. record some audio samples by yourself, using a smartphone or else;
2. or use already recorded audio samples you can find online, e.g., on YouTube.

### Downloading audio files from YouTube videos

The easiest way to download audio files from YouTube videos is probably with
`youtube-dl`.

#### Install

```bash
uv sync
```

You also need to [install FFmpeg](https://ffmpeg.org/download.html),
see install instructions for your specific OS.

#### Usage

Obtain the link to the video (do not take the one in the URL bar!):

<div align="center">
<img src="https://github.com/LELEC210X/LELEC210X/assets/27275099/a561bf41-98fe-41b3-9844-cd33470c517b" alt="How to get video link from Youtube">
</div>

Then, use to URL to download the audio file directly from your terminal:

```bash
uv run youtube-dl -x --audio-format=wav "<path-to-video>"
```

#### YouTube playlist

The Teaching Assistants created a
[YouTube playlist](https://youtube.com/playlist?list=PLK2PsMuicSN8Y7ovsXjypFADW5EeGVn36&si=SKMsifoMk8CKnWet)
with (**very**) long videos from which you can download audio files,
and split them in a dataset (see below).

If you discover an new YouTube video that you feel could be added to this playlist,
please contact us!

### Splitting one large audio file into many

If sound files are long enough, it may be interesting to split large audio file into many audio samples,
we provide tools to perform that automatically: `uv run split-audio "<my_audio_file>"`.
