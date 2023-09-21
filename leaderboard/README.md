# Leadeboard

This folder contains everything you need to run a local version of the leadeboard.

> **NOTE**: if you are a student and your are reading this online,
> you are most probably just interested in reading **Submitting a guess**
> (see below).

## Installation

This project uses [`Poetry`](https://python-poetry.org/docs/) to install
dependencies and command-line tools. For this, you need to run:

```bash
poetry install
```

the first time you use this server, you must create a config file:

```bash
poetry run flask config init
```

and populate it when some group(s):

```bash
poetry run flask config generate-key "Teaching Assistants"
```

The key will be useful to send your guesses to the server.

Then, the server must be launched with:

```bash
poetry run python app.py
```

For other commands, see:

```bash
poetry run flask --help
```

> **WARNING:** using `flask run` will not work properly, do not use it.

## Usage

Once the server is launched, the configuration file cannot be modified,
so make sure to update it before.

To submit a guess, you need to do a HTTP request.
There exists many HTTP methods,
but this project only uses `POST` (posting a value), `PATCH` (editing),
`GET` (getting), and `DELETE` (deleting).

The simplest way to do so is to use the `requests` library, see the example below.

## Example

### (Optional) If you run your own server

```bash
> poetry run flask config generate-key "Teaching Assistants"
Group Teaching Assistants now has key: aqH27o66E8xz-IotBk11ZZo1ix7Vbs5H2pTXlSra
```

### Submitting a guess

Then, in Python:

```python
import requests

hostname = "http://localhost:5000"
key = "aqH27o66E8xz-IotBk11ZZo1ix7Vbs5H2pTXlSra"
guess = "fire"

response = requests.patch(f"{hostname}/leaderboard/submit/{key}/{guess}")

import json

# All responses are JSON dictionaries
response_as_dict = json.loads(response.text)
```

Many more requests are possible!
Please go to the
[API docs](https://perceval.elen.ucl.ac.be/lelec2103/leaderboard/doc/)
for more details.

> **NOTE**: `http:localhost:5000` is the default hostname (and port)
> that is used if you run the server on your computer.
> For the contest, please use
> `hostname = "https://perceval.elen.ucl.ac.be/lelec2103"`.

## Deploying on perceval

First, connect to the server via SSH:

```bash
ssh lelec2103@perceval.elen.ucl.ac.be -p 22
```

> **NOTE**: this requires a valid SSH public key of yours to be on the server.

Next, download the latest changes:

```bash
git pull
```

Note that deploying on perceval requires a few changes:

- one in `.faskenv`;
- and a second in `static/js/leadeboard`;

where you need to (un)comment some lines.

Next, everything should run as expected.

A simple way to run the server in background is with `screen`:

```bash
screen -d -m poetry run python app.py
```

## Submitting a Key for the Security Round

The security round takes place in parallel to all the other rounds,
and submission is therefore always open.

Each group can submit a key guess, and have its score displayed on the scoreboard.

For security concerns, the score will not be returned by the API, and the number
of requests will be limited (to avoid attacking the server instead).

A valid key guess is 16 bytes long.

```python
import urllib

# You guess
guess = [161, 15, 114, 205, 173, 97, 19, 139, 172, 136, 170, 73, 85, 252, 63, 133]

# First, convert that to bytes:
guess_bytes = bytes(guess)

# Then, encode this as an url-safe string:
guess_str = urllib.parse.quote_from_bytes(guess_bytes, safe="")
```
