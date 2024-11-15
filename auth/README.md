# Authentification

Files related to the authentification part.

## Installation

All dependencies should be installed with the following command:

```bash
rye sync
```

## Usage

Currently, there is only one script that is installed by `rye` and that is `auth`:

```bash
rye run auth --help
```

Many options exist, but you should be able to run with the default ones, i.e., `rye run auth`, and
read messages from the TCP address that GNU Radio talks to.

> [!TIP]
> If you did not implement authentification, you can bypass it
> with `rye run auth --no-authenticate`.

> [!WARNING]
> Please make sure to use the correct number of Mel vectors and the correct length.
> A default value is automatically set, but you change it
> to match the one you are using! See `rye run auth --help`.

> [!TIP]
> For secret variables, such as `--auth-key`,
> it is recommended to store them in an environment variable (easy on Linux system), e.g.:
>
> ```bash
> echo "export AUTH_KEY=12345678123456781234567812345678  # 16 bytes key" >> ~/.bashrc.
> ```
>
> The script(s) will automatically detect and read environment variables when present.
> 
> If you work on Windows, the easiest way is to modify the default value of the `--auth-key` option to the key selected by your group in the `auth/src/auth/__main__.py` file.
