# Leadeboard

This folder contains everything you need to run a local version of the leadeboard.

> [!NOTE]
> If you are a student,
> the most important section for the contest is **Submitting a guess**
> (see below).
>
> **However**, we will not run the public server every hour
> of every day until the contest. So you are encouraged
> to do all your testing on a local server, deployed on
> your computer. For that purpose, read the sections
> below.

## Installation

All dependencies should be installed with the following command:

```bash
poetry install
```

## Setup

The first time you use this server, you must create a config file:

```bash
poetry run leaderboard config init
```

and populate it when some group(s):

```bash
poetry run leaderboard config generate-key "Teaching Assistants"
```

The key will be useful to send your guesses to the server.

Then, the server must be launched with:

```bash
poetry run leaderboard serve
```

Alernatively, you can open the server in webbrowser window with:

```bash
poetry run leaderboard serve --open
```

> [!TIP]
> There also exists `--open-docs` to open to
> API documentation page, see below.

For other commands, see:

```bash
poetry run leaderboard --help
```

## Usage

Once the server is launched, the configuration file cannot be modified,
so make sure to update it before.

To submit a guess, you need to do a HTTP request.
There exists many HTTP methods,
but this project only uses `POST` (posting a value),
`GET` (getting), and `DELETE` (deleting).

The simplest way to do so is to use the `requests` library, see the example below.

## Example

### (Optional) If you run your own server

```bash
> poetry run leaderboard config generate-key "The Besties"
Group The Besties now has key: aqH27o66E8xz-IotBk11ZZo1ix7Vbs5H2pTXlSra
```

To test everything locally, you also need to create a group with admin rights:

```bash
> poetry run leaderboard config generate-key --admin "Teaching Assistants"
Group Teaching Assistants now has key: EdY7unM6C6ZFwt9uTjmaMv6eX9nM7pljGADmcudJ
```

The first key will be used to submit guesses, while the second will
be used to play to sound files, and also let you control the leaderboard
(see API docs below).

For the contest, you will only have a non-admin key :-)

### Submitting a guess

Then, in Python:

```python
import requests

hostname = "http://localhost:5000"
key = "aqH27o66E8xz-IotBk11ZZo1ix7Vbs5H2pTXlSra"
guess = "fire"

response = requests.post(f"{hostname}/lelec210x/leaderboard/submit/{key}/{guess}")

import json

# All responses are JSON dictionaries
response_as_dict = json.loads(response.text)
```

This is also possible to submit a guess with:

```bash
poetry run leaderboard submit fire --key="aqH27o66E8xz-IotBk11ZZo1ix7Vbs5H2pTXlSra"
```

Please only use this command for testing purposes.

Many more requests are possible!
Please go to the
[API docs](http:localhost:5000/lelec210x/leaderboard/doc/)
for more details.

<!-- prettier-ignore -->
> [!NOTE]
> `http:localhost:5000` is the default hostname (and port)
> that is used if you run the server on your computer.
> For the contest, please use
> `hostname = "https://lelec210x.sipr.ucl.ac.be/lelec210x"`.

> [!TIP]
> If you want to access the server from another computer, on the
> same local network, it is possible (but not needed)!
>
> So you can have computer A running the leaderboard server,
> and compute B receiving packets through the air and sending
> guesses to computer A via the local network.
>
> To do this, you need to find the IP address of computer A
> on the local network. On Linux, you can run `ifconfig`,
> and search for the IP address next to `inet`.
> For example, you could have `192.168.1.132`.
>
> Then, just change `FLASK_RUN_HOST = localhost` to
> `FLASK_RUN_HOST = 192.168.1.132` in
> [`.flaskenv`](.flaskenv).

### Playing sound files

The leaderboard server does not actually play the soundfiles,
because the actual computer does not have access to any speaker.

To play sound files, a group with admin rights, i.e., the teaching
assistants during the contest, need to connect to the leaderboard remotely,
and receiving leaderboard statuses to play the right sound files.

This is done with this command:

```bash
poetry run leaderboard play-sound --key EdY7unM6C6ZFwt9uTjmaMv6eX9nM7pljGADmcudJ
```

## Submitting a Key for the Security Round

> [!IMPORTANT]
> Starting 2023-2024, the cryptographic part of this project
> was removed, so information below is outdated.

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

## Server setup

> [!IMPORTANT]
> This part is only for the teaching assistants that want to deploy the server
> online, such that students can access it remotely.
>
> If you have any issue, contact the UCLouvain desk service
> (https://uclouvain.be/8282) and specify the server adress
> (lelec210x.sipr.ucl.ac.be) in your message.

### Server access

The server address is `lelec210x.sipr.ucl.ac.be` (`130.104.12.28`).

The server access is only possible via SSH, from a specific set of IP addresses.
If you do not have access, you need to ask the I.T. staff (or one of the member
that already has such access).

In the terminal:

```bash
ssh -p 22 username@130.104.12.28
```

where `username` is your username. You will be prompted to enter your password.

Here, for simplicity, the useful folders are placed in a root-owned directory[^1].
So, you need to elevate your privileges with:

```bash
sudo su
```

[^1]:
    In theory, this would be better to create a user group, e.g., "TAs", and add all users
    that need such access to that group.

### First setup

> [!IMPORTANT]
> Only one person needs to do it once. This is kept here for documentation purposes.

Fist, go into super-user mode and clone the repository.

```bash
cd /var/www
git https://github.com/LELEC210X/LELEC210X.git
```

You will only have `pull` rights to the repository, so do not make important changes
because you will not be able to push them.

Install Python3.8 and Poetry:

```bash
sudo apt update
sudo apt upgrade
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.8-venv
curl -sSL https://install.python-poetry.org | python3.8 -
echo 'export PATH="/root/.local/bin:$PATH"' >> /root/.bashrc
source /root/.bashrc
```

#### Apache2 server

*Work in progress*

Create `/etc/apache2/sites-available/LELEC210X.conf`:

```conf
<VirtualHost *:80>
        ServerName http://lelec210x.sipr.ucl.ac.be/
        WSGIScriptAlias /lelec210x /var/www/LELEC210X/leaderboard/app.wsgi
        <Directory /var/www/LELEC210X/>
                Options FollowSymLinks
                AllowOverride None
                Require all granted
        </Directory>
        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

### Update installation

Before starting the server, this is always good to do the following commands:

```bash
cd /var/www/LELEC210X
git pull
poetry install
```

This will download the latest changes and update the packages (if needed).

### Deploying the server

Note that deploying on requires a few changes:

- one in `.faskenv`;
- and a second in `static/js/leadeboard`;

where you need to (un)comment some lines.

Next, everything should run as expected.

A simple way to run the server in background is with `screen`:

```bash
screen -d -m poetry run leaderboard serve
```
