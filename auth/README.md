# Authentification

Files related to the authentification part.

## Installation

All dependencies should be installed with the following command:

```bash
poetry install
```

## Usage

Currently, there is only one script that is installed by `poetry` and that is `auth`:

```bash
poetry run auth --help
```

Many options exist, but you should be able to run with the default ones, i.e., `poetry run auth`, and
read messages from the TCP address that GNU Radio talks to.

> [!TIP]
> If you did not implement authentification, you can bypass it
> with `poetry run auth --no-authenticate`.

> [!WARNING]
> Please make sure to use the correct number of Mel vectors and the correct length.
> A default value is automatically set, but you change it
> to match the one you are using! See `poetry run auth --help`.

> [!TIP]
> For secret variables, such as `--auth-key`,
> it is recommended to store them in an environ variable, e.g.:
>
> ```bash
> echo "export AUTH_KEY=12345678123456781234567812345678  # 16 bytes key" >> ~/.bashrc.
> ```
>
> The script(s) will automatically detect and read environ variables when present.
