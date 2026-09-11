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
- **STM32CubeIDE**: used to program the microcontroller;
- and **GNU Radio**: used to acquire data from the LimeSDR-mini
  and perform signal processing, e.g., the demodulation.

If possible, every software tool used should be installed and used,
on your host system, i.e., your every-day OS. Moreover,
**the Git associated with the project should be cloned on your host system.**
Python and STM32CubeIDE are supported on every common OS,
**but GNU Radio is only properly supported on Linux distributions**.
The project is supported on GNU Radio 3.10, which can be installed on
Ubuntu 22.04. Ubuntu 24.04 could be supported but has not been tested.

> [!TIP]
> We strongly recommend students with a Windows OS to only
> run GNU Radio inside WSL, and to have all the other software
> installed on their Windows OS.

## Prerequisites

<!---If you plan to use GNU Radio 3.8, installed on Ubuntu 20.04, beware
that it requires Python 3.8, which is the default version installed on this
Ubuntu release. **However**, the rest of the project
works with any version of Python above 3.8. Moreover, uv, the tool
you will need to install later, automatically installs Python 3.10,
so you don't need to bother about that. Again this comment is only
relevant if you plan to use Ubuntu 20.04 with GNU Radio 3.8.
_Only the few Python files that are used by GNU Radio need to
be executed with Python 3.8._

Hence, it is only required to have Python 3.8 installed on
WSL, VB, or your Linux dual-boot, as this will be the place
where GNU Radio will be executed, so you actually don't have to do anything.

Using a different Python version _might_ work,
but **we cannot guarantee** that
everything will work out-of-the-box, and **you may need**
to adapt some commands[^1].

If you do not have Ubuntu-20.04 at your disposal,
please follow one of next subsections.

[^1]:
    The reason is that the default versions for packages installed on
    Ubuntu-20.04 are, most likely, not the same if installed on, e.g.,
    Ubuntu-22.04.
--->

In order to install GNU Radio, you need to have access to a Linux system. If your host system does not run a Linux distribution, you will find some suggestions for obtaining access to one below.

### Install Ubuntu via Windows Subsystem for Linux

Windows Subsystem for Linux (WSL) is a Windows program that makes running a Linux image super simple!
WSL allows for true Windows and Linux interoperability.
You can explore the Linux file system from Windows, and vice versa.
You can also launch programs from each other's command lines.
It is also much lighter on resources (compared to VirtualBox).
It will allow you to clone the git of the course on your Windows system and **do most of the work on Windows**,
e.g., programming the MCU, modify the telecom and classification parts,
while **only using WSL to compile** the code and run the Linux applications, i.e., GNU Radio.

We recommend using Ubuntu-22.04 (**best**) or Ubuntu-24.04, for the project.

In order to install the WSL and Ubuntu-22.04 on your Windows system,
we will use the following [guide](https://learn.microsoft.com/en-us/windows/wsl/install) from Microsoft.

If you have WSL 1 installed (`wsl --version`), please
[upgrade](https://dev.to/adityakanekar/upgrading-from-wsl1-to-wsl2-1fl9)
it to version 2!

Open a PowerShell or Windows Command Prompt in administrator mode and enter the following command:

```bat
wsl --install -d Ubuntu-22.04
```

This will install WSL with the required distribution of Linux.
As we want to use the second version of WSL, named WSL2,
you can check the distribution installed and the version of WSL:

```bat
wsl -l -v
```

If necessary, you can change the version of WSL using:

```bat
wsl --set-version Ubuntu-22.04 2
```

We advise you to set up the default version of WSL and the default distribution as follows:

```bat
wsl --set-default-version 2
wsl --setdefault Ubuntu−22.04
```

You should now be able to launch and terminate a WSL session of Ubuntu-22.04 using:

```bat
wsl
wsl -t Ubuntu−22.04
```

<!--- If you were to use Ubuntu-20.04, just adapt the previous commands with the release version.
If you encounter any issue, please refer to the official website provided at the start of this section. --->

### Install Ubuntu on your computer

On most computers (macOS, Windows, and Linux), you can install another OS
using a _dual boot_. The internet is full of tutorial on how to install
Ubuntu in dual boot. Please make sure to install the correct version.

This is going to be, by far, the most performant solution, but will also require
much more disk space. This solution is recommended for people that might
want to use Linux later-on, and have at least 60 Go of free memory.

### Install on VirtualBox

You can get Ubuntu running with a virtual machine (VM) using VirtualBox.
As you will have to run a complete Linux image from your Windows system,
this solution has a **significant overhead** in terms of processing capability and also in terms of accessibility.
Indeed, you will work in desktop entirely contained in a window which might be impractical.

## Installation steps

The following steps will either need to be performed on your host system,
or on the Ubuntu system on which GNU Radio is installed
(either WSL, or your host).
The subsection titles will therefore include an annotation **Host**,
if the steps must be performed on your host system (Windows, macOS, or Linux), or **Ubuntu**,
if they refer to your Ubuntu installation. If your host system is Ubuntu, perform them in both cases.
Additionally, some steps might be only required for some specific OSes, in which case it will be specified.

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

### Host or Ubuntu - Install uv

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

### Host or Ubuntu - Install FFmpeg

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


### Host - Installation of STM32CubeIDE

In order to program and configure the MCU, we will use the _STM32CubeIDE_ software from ST.
To download the installer, go to the following [website](https://www.st.com/en/development-tools/stm32cubeide.html)
and select the latest version of the installer for your **host operating system**.
You might be asked to create an account. You can then proceed to the download and installation.

### Ubuntu - STM32Cube IDE additional package

If Ubuntu is your host system and thus STM32CubeIDE is installed on it, you might need to install a package in order to flash the MCU. To do so:

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
