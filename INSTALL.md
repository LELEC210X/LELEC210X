# Install Guidelines

Please find here all required steps to set up your project correctly.

All commands are assumed to be run inside a terminal / command prompt.

**Table of Contents:**

- [Tools Used for This Project](#tools-used-for-this-project)
- [Prerequisites](#prerequisites)
  - [Virtual Box](#install-on-virtualbox)
  - [Windows Subsystem for Linux](#install-via-windows-subsystem-for-linux)
  - [Ubuntu](#install-ubuntu-on-your-computer)
- [Installation Steps](#installation-steps)
- [Tips for a Better Environment](#tips-for-a-better-environment)

## Tools Used for This Project

In this project, will you have to use different software and tools.

- **Python**: employed for various tasks, e.g., classification, modeling;
- **STM32CubeIDE** and **STM32CubeMX**: used to program the microcontroller;
- and **GNU Radio**: used to acquire data from the SDR
  and perform signal processing, e.g., the demodulation. The instructions to install
  this software will be provided to you later when the wireless communication part of 
  the project will start

If possible, every software tool used should be installed and used,
on your host system, i.e., your every-day OS. Moreover,
**the Git associated with the project should be cloned on your host system.**
Python and STM32CubeIDE/MX are supported on every common OS.



## Installation steps

The following steps depend based on the OS of your host system. Please always refer to the corresponding section with respect to your setup. Skip parts that are not related to your system. When **Host** is in the section title, it concerns every OS.


### Ubuntu - APT update

Quick tips: Ubuntu terminal windows can be launched via the Ubuntu Launchpad, or with
<kbd>CTRL</kbd>+<kbd>ALT</kbd>+<kbd>T</kbd>.

You can start by updating your system’s package list. Enter the following command:

```bash
sudo apt update
```

### Ubuntu - Install Pip

Sometimes, Python is not shipped with its package installer, pip.

Please make sure pip is installed by running:

```bash
sudo apt-get install python3-pip
```

### Host - Install uv

Usually, installing Python packages to the global Python environment is a bad idea,
mainly because you can have conflicts with packages that require different versions
of some shared dependencies, and rapidly lose track of what packages are actually
installed on your computer.

A solution to this is to use
[virtual environments (venvs)](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#installing-packages-using-pip-and-virtual-environments),
one venv for each isolated project.

However, venvs can rapidly become hard to maintain, especially because you need to activate
some script
before you can work with them, and it's also possible to have an arbitrary number of nested
venvs, which makes it hard to know which environment is activated.
To avoid this issue, we use
[uv](https://docs.astral.sh/uv/).
uv works in pair with `pyproject.toml` files,
so that you can specify requirements for your project, and much more!

> [!IMPORTANT]
> While uv should work fine on any OS, we highly recommend
> installing it on Ubuntu too, because it is easier for teaching
> assistants to debug.

**Please** read the
[detailed installation guide](https://docs.astral.sh/uv/getting-started/installation/).

### Host - Install FFmpeg

Later in the project, if you want to manipulate audio files,
you need to install FFmpeg.
Otherwise, you might encounter some errors.

[FFmpeg](https://ffmpeg.org/) is a **very comprehensive** toolbox for manipulating
audio and video files.

For this project, this will be used to read and write audio files (via Python modules),
and it must then be installed on the same OS as uv.

#### Linux

On Ubuntu:

```bash
sudo apt install ffmpeg
```

For other Linux distros, see the [download page](https://ffmpeg.org/download.html).

#### macOS

On macOS, either use [Homebrew](https://brew.sh/)
(if installed, which is recommended):

```bash
brew install ffmpeg
```

or download it from the [download page](https://ffmpeg.org/download.html).

#### Windows

Please download it from the [download page](https://ffmpeg.org/download.html).

### Ubuntu - Install CMake and Make

```bash
sudo apt-get install cmake
```

### Host - Installation of STM32CubeIDE and STM32CubeMX

In order to program and configure the MCU, we will use the _STM32CubeIDE_ and _STM32CubeMX_ softwares from ST.
To download the installers, go to the following websites ([_STM32CubeIDE_](https://www.st.com/en/development-tools/stm32cubeide.html) - [_STM32CubeMX_](https://www.st.com/en/development-tools/stm32cubemx.html)), scroll down to the download section and select the latest version of the installer **for your host operating system**.
You will be asked to create an account. You can then proceed to the download and installation.

> [!NOTE]
> _STM32CubeIDE_ may look old and ugly, but it is a powerful tool that embeds a preconfigured compilation chain, the flasher and the debugger tools.
> There exists an extension for VSCode that should do the job too but we did not test it.
> You are free to try and use that extension if you find it more convenient. However we won't provide support for it.
> _STM32CubeMX_ has no alternative. Note that until 2025 MX was embedded into the IDE but they are now two separate tools.

### Ubuntu - STM32CubeIDE additional package

If Ubuntu is your host system and thus _STM32CubeIDE_ is installed on it, you might need to install a package in order to flash the MCU. To do so:

```bash
sudo apt-get install libncurses5
```

### Install Python dependencies

To install the Python dependencies, you can simply run:

```bash
uv sync
```

You should only perform this once (if `pyproject.toml` does not change).

> [!IMPORTANT]
> Note that, in order to work, `uv` commands
> must be done in a terminal session **from inside**
> the root directory of this project, or any of its
> subdirectories.

If you modify any of the packages listed in the `[project]` section
of [`pyproject.toml`](pyproject.toml), the changes will directly apply
to your installation.

To add new Python dependencies to your project, you can use

```bash
uv add package_name
```

and uv will do the rest for you! For other use cases, please
check out their documentation.

> [!NOTE]
> Later in the project, you will install Python packages from
> GNU Radio projects. Those packets are **not installed**
> in the virtual environment created by uv.
> To use those packages (e.g., `fsk`), you should
> then use your system Python (version 3.8!).
>
> We already considered that in the hands-on sessions,
> and the commands we provide should work as expected.

## Tips for a Better Environment

By default, we **did not install** git and any specific code editor **on purpose**.
When possible, you should use your host OS to edit files, commit changes to git, and so on.

> Example: if you have installed the program via WSL, _Windows_ is your host OS. You should only use
> WSL to compile programs, and open software (like GNU Radio) that could not be installed on the host.

### With WSL

With WSL, the file system is already shared between the host and WSL, so you can easily access files
from both OSes.

### List of Nice Programs to Install

If you plan on using Linux more, or that you want to have a nice programmer config so that
you can brag about it, please check out the following programs.

#### Git and GitHub Student Pack

Because we force using git, you should have it installed on your host. On Linux:

```bash
sudo apt-get install git
```

Additionally, GitHub offers a lot of resources for free via [GitHub Student Developer Pack](https://education.github.com/pack).

#### Using a Nicer Shell

By default, the terminal shell is Bash. While it is quite functional, it lacks a few modern features
like history-based command suggestion. A widely used alternative is Zsh. On macOS, this is actually
the default shell program.

We suggest installing Zsh and the [OhMyZsh](https://ohmyz.sh/) theme for a nicer out-of-the-box experience:

```bash
sudo apt-get install zsh
chsh -s $(which zsh)
sh -c "$(wget -O- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

> [!IMPORTANT]
> Re-run all the `export ...=...` commands but
> **change** the output file to `>> ~/.zshrc`.

Then, you can add plugins to your Zsh shell,
[zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions/blob/master/INSTALL.md)
being a game changer to avoid retyping the same commands again and again.

#### NeoVim for Editing Code Like a Pro

Maybe you find people editing directly in the terminal _super stylées_?
Well you can also become such a person by installing [NeoVim](https://neovim.io/),
the code editor for real programmers:

```bash
sudo apt-get install neovim
```

> [!NOTE]
> Jokes aside, NeoVim is a very nice editor, but also quite hard to use, mainly because
> you can only use your keyboard (you are in the terminal!). Learning NeoVim is good if
> you plan on regularly connecting to remote machines (e.g., you train an ML model on a
> powerful workstation), you like to customize every tiny bit of your editor, or you
> don't want an editor that slows down your computer. That being said, editors like
> VS Code are probably a good choice too.
