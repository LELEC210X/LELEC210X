# Install Guidelines

Please find here all required steps to setup your project correctly.

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
the Git associated with the project should be cloned on your host system.
Python and STM32CubeIDE are supported on every common OS,
but GNU Radio is only properly supported on Linux distributions.
Additionnally, the libraries for the LimeSDR are maintained on Ubuntu-20.04
and not above.
We therefore ask you to have Ubuntu-20.04 installed on your computer,
using one of the methods presented in the following sections.

## Prerequisites

As explained above, to run this project entirely,
you will need an Ubuntu-20.04 installation with Python3.8 installed.
Using a different Ubuntu or Python version _might_ work,
but **we cannot guarantee** that
everything will work out-of-the-box, and **you may need**
to adapt some commands[^1].

By default, Python3.8 is automatically bundled with Ubuntu-20.04.

If you do not have Ubuntu-20.04 at your disposal,
please follow one of next sub-sections.

[^1]:
    The reason is that the default versions for packages installed on
    Ubuntu-20.04 are, most likely, not the same if installed on, e.g.,
    Ubuntu-22.04.

### Install on VirtualBox

You can get Ubuntu-20.04 running with a virtual machine (VM) using VirtualBox.
As you will have to run a complete Linux image from your Windows system,
this solution has a **significant overhead** in terms of processing capability and also in term of accessibility.
Indeed, you will work in desktop entirely contained in a window which might be impractical.
However, we provide you with a VirtualBox image file on which all installation steps are already performed for you.

For the installation and the configuration of the Virtual machine, please refer to the
"_Installation of the Virtual Machine with the project softwares_" provided on the Moodle of the course.

Below, you can find the option selected during the installation
of Ubuntu Desktop 20.04.5 LTS:

- [x] keyboard layout set to English US;
- [x] minimal installation;
- [x] (user)name set to marconi;
- [x] password set to faraday;
- [x] automatically log in.

> Note: after first logging, the French Azerty layout was also added, and should be
> the default one. To switch between the two layouts,
> you can use <kbd>SHIFT</kbd>+<kbd>SUPER</kbd>+<kbd>SPACE</kbd>,
> where <kbd>SUPER</kbd> is usually the Windows key.

### Install via Windows Subsystem for Linux

Windows Subsystem for Linux (WSL) is a Windows program that makes running a Linux image super simple!
WSL allows for true Windows and Linux interoperability.
You can explore the Linux file system from Windows, and vice versa.
You can also launch programs from each other's command lines.
It is also much lighter on resources (compared to VirtualBox).
It will allow you to clone the git of the course on your windows system and **do most of the work on Windows**,
e.g., programming the MCU, modify the telecom and classification parts,
while **only using WSL to compile** the code and run the Linux applications, such as GNU Radio.

In order to install the WSL and Ubuntu-20.04 on your Windows system,
we will use the following [guide](https://learn.microsoft.com/en-us/windows/wsl/install) from Microsoft.

If you have WSL 1 installed (`wsl --version`), please
[upgrade](https://dev.to/adityakanekar/upgrading-from-wsl1-to-wsl2-1fl9)
it to version 2!

Open a PowerShell or Windows Command Prompt in admnistritator mode and enter the following command:

```bat
wsl --install -d Ubuntu-20.04
```

This will install WSL with the required distribution of Linux.
As we want to use the second version of WSL, named WSL2,
you can check the distribution installed and the version of WSL:

```bat
wsl -l -v
```

If necessary, you can change the version of WSL using:

```bat
wsl --set-version Ubuntu-20.04 2
```

We advise you to setup the default version of WSL and the default distribution as follow:

```bat
wsl --set-default-version 2
wsl --setdefault Ubuntu−20.04
```

You should now be able to launch and terminate a WSL session of Ubuntu-20.04 using:

```bat
wsl
wsl -t Ubuntu−20.04
```

If you encounter any issue, please refer to the official website provided at the start of this section.

### Install Ubuntu on your computer

On most computers (macOS, Windows, and Linux), you can install another OS
using a _dual boot_. The internet is full of tutorial on how to install
Ubuntu in dual boot. Please make sure to install the correct version.

This is going to be, by far, the most performant solution, but will also require
much more disk space. This solution is recommended for people that might
want to use Linux later-on, and have at least 60 Go of free memory.

## Installation steps

https://www.howtogeek.com/118594/how-to-edit-your-system-path-for-easy-command-line-access/

The following steps will either need to be performed on your host system, or on the Ubuntu system on which GNU Radio is installed (either a VM, WSL, or your host if it is Ubuntu-20.04).
The subsection titles will therefore include an annotation **Host**, if the steps must be performed on your host system (Windows, MacOS, or Linux), or **Ubuntu**, if they refer to your Ubuntu-20.04 installation. If your host system is Ubuntu-20.04, perform them in both cases.Additionnally, some steps might be only required for some specific OSs, in which case it will be specified.

Quick tips : Ubuntu terminal windows can be launched via the Ubuntu Launchpad, or with
<kbd>CTRL</kbd>+<kbd>ALT</kbd>+<kbd>T</kbd>.

### Ubuntu : Install Pip

Sometimes, Python is not shipped with its package installer, pip.

Please make sure pip is installed by running:

```bash
sudo apt-get install python3-pip
```

### Host AND Ubuntu : Installing Poetry

Usually, installing Python packages to the global Python environment is a bad idea,
mainly because you can have conflicts with packages that require differention versions
of some shared dependencies, and rapidly loose track of what packages are actually
installed on your computer...

A solution to this is to use
[virtual environments (venvs)](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#installing-packages-using-pip-and-virtual-environments),
one venv for each isolated project.

However, venvs can rapidly become hard to maintain, especially because you need to activate
some script
before you can work with them, and it's also possible to have an arbitrary number of nested
venvs, which makes it hard to know which environment is activated.
To avoid this issue, we use
[Poetry](https://python-poetry.org/), which can be installed with the commands below, depending if you are on Mac/Linux or Windows. Poetry works in pair with `pyproject.toml` file, so that you can specify requirements for your project, and much more!

#### Linux/MAC

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Note that the previous command might require installing `curl`:

```bash
sudo apt-get install curl
```

As probably displayed during the installation, you might need to add `~/.local/bin` to your `PATH`:

```bash
echo "export PATH='~/.local/bin:$PATH'" >> ~/.bashrc
```

Then, execute:

```bash
exec bash
```

to apply changes.

> Note: using `>>` automatically appends to the file, so that you don't have anything
> to do. If you prefer, you can edit the files from the terminal using programs
> like `nano` or `vim`.

#### Windows

In the Powershell:

```bash
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

Do not close the terminal, it will probably ask you to add the poetry installation path to your PATH environment variable. To do so, follow [this guide](https://www.howtogeek.com/118594/how-to-edit-your-system-path-for-easy-command-line-access/).

### Ubuntu : Installing CMake and Make

```bash
sudo apt-get install cmake
```

### Ubuntu : Installing GNU Radio

For the LimeSDR to work, we need to install GNU Radio **3.8** and no any version higher.
To do so:

```bash
sudo add-apt-repository ppa:gnuradio/gnuradio−releases−3.8
sudo apt-get update
sudo apt-get install gnuradio xterm python3-gi gobject-introspection gir1.2-gtk-3.0
```

You should now be able to open GNU Radio with its GUI with the following command.
_If you use Windows with WSL, please refer first to the next section_

```bash
gnuradio-companion
```

To kill GNU Radio, either press the exit button, or press <kbd>CTRL</kbd>+<kbd>C</kbd>.

> On Linux, you can launch processes in the background by appending `&` at the end
> of some command. E.g., `gnuradio-companion &`. To later terminate the process,
> you can use the `pkill` command. E.g., `pkill gnuradio-compagnion`.

### (Only for WSL users) Setup of graphical display for WSL

By default, Ubuntu uses X for displaying graphical content, but
Windows uses a different protocol. Therefore, to allow displaying
applications launched with WSL, you must install a X server on Windows.
The X server will then be accessed from WSL applications to display content
directly on your host.

There exist several servers and we propose here to install [Xming](https://sourceforge.net/projects/xming/) with all default settings.
We here follow this [guide](https://wiki.gnuradio.org/index.php/WindowsInstall#WSL_|_Ubuntu) from GNU Radio wiki.
With Xming installed, you can then launch _XLaunch_ from the Start Menu and click next until the "Specify parameter settings" screen.
Check "No Access Control" then click next, then finish. In WSL, enter the following command:

```bash
sudo apt install libgtk-3-dev
```

Finally, to forward the display on the proper port,
the following lines should be added to the _.bashrc_ file of your Ubuntu distribution:

```bash
echo "export DISPLAY=:0.0" >> ~/.bashrc
echo "export LIBGL_ALWAYS_INDIRECT=1" >> ~/.bashrc
```

Restart the WSL and you should now be able to launch GNU Radio's GUI as follows:

```bash
gnuradio-companion
```

If this does not work, you might need to change the two exports above to:

```bash
echo "export DISPLAY=$(awk '/nameserver / {print $2; exit}' /etc/resolv.conf 2>/dev/null):0" >> ~/.bashrc
echo "export LIBGL_ALWAYS_INDIRECT=1" >> ~/.bashrc
```

### Ubuntu - Installing the different LimeSDR components

We can now install the different components required to use the LimeSDR with GNU Radio.
We follow the information provided [here](https://wiki.myriadrf.org/Lime_Suite)
by the company who sells the LimeSDR, _Myriad-RF_.

#### Ubuntu - Installing LimeSuite

We start by installing _LimeSuite_, i.e.,
a collection of softwares supporting several hardware platforms including the LimeSDR.

```bash
sudo add-apt-repository -y ppa:myriadrf/drivers
sudo apt-get update
sudo apt-get install limesuite liblimesuite-dev limesuite-udev limesuite-images
sudo apt-get install soapysdr-tools soapysdr-module-lms7
```

#### Ubuntu - Installing Gr-LimeSDR

Finally, we need to install _Gr-LimeSDR_ which is a low cost, open source software defined radio (SDR) platform.
To do so, we use the following command,
taken from the [official website](https://wiki.myriadrf.org/Gr-limesdr_Plugin_for_GNURadio).

```bash
sudo add-apt-repository ppa:myriadrf/gnuradio
sudo apt-get update
sudo apt-get install gr-limesdr
```

#### Ubuntu - Testing the installation of LimeSDR

You can launch GNU Radio companion. On the right part of the window, at the end of the list,
LimeSDR components should now appear.

### (Only for WSL users) Connect the LimeSDR to the WSL via USB pass-through

The LimeSDR will be connected to your computer but should be interfaced with your Ubuntu and not Windows. To do so, we will need to create a passthrough using [USBIPD-WIN](https://learn.microsoft.com/en-us/windows/wsl/connect-usb) supported by Microsoft. Go to this [git project](https://github.com/dorssel/usbipd-win/releases) and download the `.msi` file of the latest version and install it.
On Ubuntu, you will need to run the two following commands:

```bash
sudo apt install linux-tools-generic hwdata
sudo update-alternatives --install /usr/local/bin/usbip usbip  /usr/lib/linux-tools/*-generic/usbip 20
```

You can now attach any device from your computer to Ubuntu.
To do so, open a PowerShell or prompt in Windows and use the three following commands to respectively list all the USB devices connected to windows, attach to WSL the device with the given busid, detach the device from WSL.

```bat
usbipd wsl list
usbipd wsl attach --busid <busid>
usbipd wsl detach --busid <busid>
```

> Note: if you have `error: Access denied; this operation requires administrator privileges`, you should
> run the same commands but in a administrator terminal. Do forget that `wsl` must be running in a separate
> Windows shell.
>
> Also, the command may tell you to update WSL. If so, please do with `wsl --update`.

### (Only for Windows users) Install PothosSDR to flash the LimeSDR-Mini

Flashing the LimeSDR-Mini, specially its FPGA, can be complicated using WSL. To avoid any issue due to the passthrough, it is recommended to install PothosSDR which support LimeSuite GUI and makes it easy to reprogram the LimeSDR. Go to the following [website](https://downloads.myriadrf.org/builds/PothosSDR/), download and run the latest installer. You should then be able to launch LimeSuite from the Windows start menu. Be careful that the LimeSDR should be attached to Windows and not Ubuntu when flashing this way.

### Host - Installation of STM32CubeIDE

In order to program and configure the MCU, we will use the _STM32CubeIDE_ software from ST.
To download the installer, go to the following [website](https://www.st.com/en/development-tools/stm32cubeide.html)
and select the latest version of the installer for your **host operating system**.
You might be asked to create an account. You can then proceed to the download and installation.

### Ubuntu - STM32Cube IDE additional package

If Ubuntu-20.04 is your host system and thus STM32CubeIDE is installed on it, you might need to install a package in order to flash the MCU. To do so :

```bash
sudo apt-get install libncurses5
```

### Host - Installation of Quartus

Most of you probably follow the course LELEC2531 for which you have installed _Quartus Prime Lite 18.1_.
If you have already it installed, you can skip the next paragraph.

To install Quartus, follow this link: [Quartus Website](https://www.intel.com/content/www/us/en/products/details/fpga/development-tools/quartus-prime/resource.html).
Then, click on the _Quartus Prime Lite_ version for your OS,
select the 18.1 version and follow the download and install instructions.

Once Quartus is installed,
you might not have the required device support package for the MAX 10 device family that we use in this project.
You can download the package
[here](https://www.intel.com/content/www/us/en/products/details/fpga/development-tools/quartus-prime/resource.html)
by first clicking on your Quartus installation, most probably the Prime Lite.
Then, select the Quartus version installed on your computer.
Under the download section, go in the _"Individual Files"_ and download the _"Intel® MAX® 10 Device Support"_.
On your computer, launch the _"Device Installer (Quartus Prime)"_ from the start menu.
If you cannot find it, it should be located in your Quartus installation folder at

```
intelFPGA/18.1/quartus/common/devinfo/dev\_install
```

The programm will ask you to select the folder in which the downloaded file is located,
it will then automatically detect the MAX 10 device support file. You can proceed to the installation.

## Tips for a Better Environment

By default, we **did not install** git and any specific code editor **on purpose**.
When possible, you should use your host OS to edit files, commit changes to git, and so on.

> Example: if you have installed the program via WSL, _Windows_ is your host OS. You should only use
> WSL to compile programs, and open softwares (like GNU Radio) that could not be installed on the host.

### With VirtualBox

VirtualBox encapsulates a lot of features, such as sharing the clipboard,
sharing folders, and so on.

#### Sharing Files Between Host and Guest OSes

When possible, you should avoid duplicating files between your host and the guest, i.e., the VM.
To avoid this, we suggest to setup shared folders betweem the two. Please refer to either
of the following guides:

- [How to share folders between your Ubuntu Virtualbox and your host machine](https://net2.com/how-to-share-folders-between-your-ubuntu-virtualbox-and-your-host-machine/);
- or [How to create a VirtualBox shared folder in Windows 11/10](https://www.thewindowsclub.com/how-to-create-a-virtualbox-shared-folder-in-windows).

### With WSL

With WSL, the filesystem is already shared between the host and WSL, so you can easily access files
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

> Important: re-run all the `export ...=...` commands but
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

> Jokes aside, NeoVim is a very nice editor, but also quite hard to use, mainly because
> you can only use your keyboard (you are in the terminal!). Learning NeoVim is good if
> you plan on regularly connecting to remote machines (e.g., you train a ML model on a
> powerful workstation), you like to customize every tiny bit of or editor, or you
> don't want an editor that slows down your computer. That being said, editors like
> VSCode are probably a good choice too.
