# Install Guidelines

Please find here all required steps to setup your project correctly.

All commands are assumed to be run inside a terminal / command prompt.

**Table of Contents:**

+ [Prerequesites](#prerequisites)
   + [Virtual Box](#install-on-virtualbox)
   + [Windows Subsystem for Linux](#install-via-windows-subsystem-for-linux)
   + [Ubuntu](#install-ubuntu-on-your-computer)
+ [Common Installation Steps](#common-installation-steps)
+ [Tips for a Better Environment](#tips-for-a-better-environment)

## Prerequisites

This tutorial assumes your are working under Ubuntu-20.04, and have Python3.8 installed.
Using a different Ubuntu or Python version *might* work, but we cannot guarantee that
everything will work out-of-the-box, and you may need to adapt some commands.

By default, Python3.8 is automatically bundled with Ubuntu-20.04.

If you do not have Ubuntu-20.04 at your disposal, please follow one of next sub-sections.

### Install on VirtualBox

You can get Ubuntu-20.04 running with a virtual machine (VM) using VirtualBox.
As you will have to run a complete Linux image from your Windows system,
this solution has a **significant overhead** in terms of processing capability and also in term of accessibility.
Indeed, you will work in desktop entirely contained in a window which might be impractical.
However, we provide you with a VirtualBox image file on which all installation steps are already performed for you.

For the installation and the configuration of the Virtual machine, please refer to the 
"*Installation of the Virtual Machine with the project softwares*" provided on the Moodle of the course.

Below, you can find the option selected during the installation
of Ubuntu Desktop 20.04.5 LTS:

- [x] keyboard layout set to English US;
- [x] minimal installation;
- [x] (user)name set to marconi;
- [x] password set to faraday;
- [x] automatically log in.

### Install via Windows Subsystem for Linux

Windows Subsystem for Linux (WSL) is a Windows program that makes running a Linux image super simple!
WSL allows for true Windows and Linux interoperability.
You can explore the Linux file system from Windows, and vice versa.
You can also launch programs from each other's command lines.
It is also much lighter on resources (compared to VirtualBox).
It will allow you to clone the git of the course on your windows system and **do most of the work on Windows**,
e.g., programming the MCU, modify the telecom and classification parts,
while **only using WSL to compile** the code and run the Linux applications, such as GNU Radio.

In order to install the WSL and Ubuntu-20.04 on youe Windows system,
we will use the following [guide](https://learn.microsoft.com/en-us/windows/wsl/install) from Microsoft.
Open a PowerShell or Windows Command Prompt in admnistritator mode and enter the following command:

```bat
wsl −−install −d Ubuntu−20.04
```

This will install WSL with the required distribution of Linux.
As we want to use the second version of WSL, named WSL2,
you can check the distribution installed and the version of WSL:

```bat
wsl −l -v
```

If necessary, you can change the version of WSL using: 

```bat
wsl --set-version Ubuntu−20.04 2
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
using a *dual boot*. The internet is full of tutorial on how to install
Ubuntu in dual boot. Please make sure to install the correct version.

This is going to be, by far, the most performant solution, but will also require
much more disk space. This solution is recommended for people that might
want to use Linux later-on, and have at least 60 Go of free memory.

## Common Installation Steps

The following commands **must** be entered inside a Linux terminal, unless specified otherwise.

Terminal windows can be launched via the Ubuntu Launchpad, or with
<kbd>CTRL</kbd>+<kbd>ALT</kbd>+<kbd>T</kbd>.

### Install Pip

Sometimes, Python is not shipped with its package installer, pip.

Please make sure pip is installed by running:

```bash
sudo apt-get install python3-pip
```

### Installing Poetry

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
[Poetry](https://python-poetry.org/):

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Note that the previous command might require installing `curl`:

```bash
sudo apt-get install curl
```

Poetry works in pair with `pyproject.toml` file, so that you can specify
requirements for your project, and much more!

### Installing CMake and Make

```bash
sudo apt-get install cmake
```

### Installing GNU Radio

For the LimeSDR to work, we need to install GNU Radio **3.8** and no any version higher.
To do so:

```bash
sudo add-apt-repository ppa:gnuradio/gnuradio−releases−3.8
sudo apt-get update
sudo apt-get install gnuradio xterm python3-gi gobject-introspection gir1.2-gtk-3.0
```

You should now be able to open GNU Radio with its GUI with the following command.
*If you use Windows with WSL, please refer first to the next section*

```bash
gnuradio-companion
```

To kill GNU Radio, either press the exit button, or press <kbd>CTRL</kbd>+<kbd>C</kbd>.

> On Linux, you can launch processes in the background by appending `&` at the end
> of some command. E.g., `gnuradio-companion &`. To later terminate the process,
> you can use the `pkill` command. E.g., `pkill gnuradio-compagnion`.

### (Only for WSL) Setup of graphical display for WSL

By default, Ubuntu uses X for displaying graphical content, but
Windows uses a different protocol. Therefore, to allow displaying
applications launched with WSL, you must install a X server on Windows.
The X server will then be accessed from WSL applications to display content
directly on your host.

There exist several servers and we propose here to install [Xming](https://sourceforge.net/projects/xming/) with all default settings.
We here follow this [guide](https://wiki.gnuradio.org/index.php/WindowsInstall#WSL_|_Ubuntu) from GNU Radio wiki.
With Xming installed, you can then launch *XLaunch* from the Start Menu and click next until the "Specify parameter settings" screen.
Check "No Access Control" then click next, then finish. In WSL, enter the following command:

```bash
sudo apt install libgtk-3-dev
```

Finally, to forward the display on the proper port,
the following lines should be added to the *.bashrc* file of your Ubuntu distribution:

```bash
export DISPLAY=$(awk '/nameserver / {print $2; exit}' /etc/resolv.conf 2>/dev/null):0 >> ~/.bashrc
export LIBGL_ALWAYS_INDIRECT=1 >> ~/.bashrc
```

> NOTE: using `>>` automatically appends to the file, so that you don't have anything
> to do. If you prefer, you can edit the files from the terminal using programs
> like `nano` or `vim`.

Restart the WSL and you should now be able to launch GNU Radio's GUI as follows:

```bash
gnuradio-companion
```

If this does not work, you might need to change the two exports above to:

```bash
export DISPLAY=:0.0 >> ~/.bashrc
export LIBGL_ALWAYS_INDIRECT=1 >> ~/.bashrc
```

### Installing the different LimeSDR components

We can now install the different components required to use the LimeSDR with GNURadio.
We follow the information provided [here](https://wiki.myriadrf.org/Lime_Suite)
by the company who sells the LimeSDR, *Myriad-RF*.

#### Installing LimeSuite

We start by installing *LimeSuite*, i.e.,
a collection of softwares supporting several hardware platforms including the LimeSDR.

```bash
sudo add-apt-repository -y ppa:myriadrf/drivers
sudo apt-get update
sudo apt-get install limesuite liblimesuite-dev limesuite-udev limesuite-images
sudo apt-get install soapysdr-tools soapysdr-module-lms7
```

#### Installing Gr-LimeSDR

Finally, we need to install *Gr-LimeSDR* which is a low cost, open source software defined radio (SDR) platform.
To do so, we use the following command,
taken from the [official website](https://wiki.myriadrf.org/Gr-limesdr_Plugin_for_GNURadio).

```bash
sudo add-apt-repository ppa:myriadrf/gnuradio
sudo apt-get update
sudo apt-get install gr-limesdr
```

#### Testing the installation of LimeSDR

You can launch GNU Radio companion. On the right part of the window, at the end of the list,
LimeSDR components should now appear.

###  (Only for WSL) Connect the LimeSDR to the WSL via USB pass-through

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

If you want to simplify the connection of a device to WSL,
[a graphical interface](https://gitlab.com/alelec/wsl-usb-gui/-/releases) exist and also provides an auto-attach function.

### Installation of STM32CubeIDE

In order to program and configure the MCU, we will use the *STM32CubeIDE* software from ST.
To download the installer, go to the following [website](https://www.st.com/en/development-tools/stm32cubeide.html)
and select the latest version of the installer for your **host operating system**.
You might be asked to create an account. You can then proceed to the download and installation.

### Installation of Quartus

Most of you probably follow the course LELEC2531 for which you have installed *Quartus Prime Lite 18.1*.
If you have already it installed, you can skip the next paragraph.

To install Quartus, follow this link: [Quartus Website](https://www.intel.com/content/www/us/en/products/details/fpga/development-tools/quartus-prime/resource.html).
Then, click on the *Quartus Prime Lite* version for your OS,
select the 18.1 version and follow the download and install instructions.

Once Quartus is installed,
you might not have the required device support package for the MAX 10 device family that we use in this project.
You can download the package
[here](https://www.intel.com/content/www/us/en/products/details/fpga/development-tools/quartus-prime/resource.html)
by first clicking on your Quartus installation, most probably the Prime Lite.
Then, select the Quartus version installed on your computer.
Under the download section, go in the *"Individual Files"* and download the *"Intel® MAX® 10 Device Support"*.
On your computer, launch the *"Device Installer (Quartus Prime)"* from the start menu.
If you cannot find it, it should be located in your Quartus installation folder at 

```
intelFPGA/18.1/quartus/common/devinfo/dev\_install
```

The programm will ask you to select the folder in which the downloaded file is located,
it will then automatically detect the MAX 10 device support file. You can proceed to the installation.

## Tips for a Better Environment

By default, we **did not install** git and any specific code editor **on purpose**.
When possible, you should use your host OS to edit files, commit changes to git, and so on.

> Example: if you have installed the program via WSL, *Windows* is your host OS. You should only use
> WSL to compile programs, and open softwares (like GNU Radio) that could not be installed on the host.

### With VirtualBox

VirtualBox encapsulates a lot of features, such as sharing the clipboard,
sharing folders, and so on. Please refer to the Moodle page and files.

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

> Important: re-run the `export DISPLAY=...` and `export LIBGL_ALWAYS_INDIRECT=...` lines but
> **changing** the output file to `>> ~/.zshrc`.

Then, you can add plugins to your Zsh shell,
[zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions/blob/master/INSTALL.md)
being a game changer to avoid retyping the same commands again and again.

#### NeoVim for Editing Code Like a Pro

Maybe you find people editing directly in the terminal *super stylées*?
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
