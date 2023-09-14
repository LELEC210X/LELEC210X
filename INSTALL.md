# Install Guidelines

Please find here all required steps to setup your project correctly.

All commands are assumed to be run inside a terminal / command prompt.

## Prerequesites

This tutorial assumes your are working under Ubuntu-20.04, and have Python3.8 installed.
Using a different Ubuntu or Python version *might* work, but we cannot guarantee that
everything will work out-of-the-box, and you may need to adapt some commands.

By default, Python3.8 is automatically bundled with Ubuntu-20.04.

If you do not have Ubuntu-20.04 at your disposal, please follow one of next sub-sections.

### Install on VirtualBox

You can get a Ubuntu-20.04 running with a virtual machine (VM) using VirtualBox. As you will have to run a complete Linux image from your Windows system, this solution has a significant overhead in terms of processing capability and also in term of accessibility. Indeed, you will work in desktop entirely contained in a window which might be impractical. However, we provide you with a VirtualBox image file on which all installation steps are already performed for you.

For the installation and the configuration of the Virtual machine, please refer to the 
"*Installation of the Virtual Machine with the project softwares*" provided on the Moodle of the course.  


### Install via Windows Subsystem for Linux

Windows Subsystem for Linux (WSL) is a Windows program that makes running a Linux image super simple! WSL allows for true Windows and Linux interoperability. You can explore the Linux file system from Windows, and vice versa. You can also launch programs from each other's command lines. It is also much lighter on resources. It will allow you to clone the git of the course on your windows system and do most of the work on windows, e.g., programming the MCU, modify the telecom and classification parts, while only using WSL to compile the code and run the Linux applications, such as GNU Radio.

In order to install the WSL and thereby Ubuntu-20.04 on you Windows system, we will follow the following [guide](https://learn.microsoft.com/en-us/windows/wsl/install) from Microsoft. Open PowerShell or Windows Command Prompt in admnistritator mode and use the following command:

```bash
wsl −−install −d Ubuntu−20.04
```
This will install WSL with the required distribution of linux. As we want to use the latest version of WSL, named WSL2, you can type the following command to check the distribution installed and the version of WSL:

```bash
wsl −l -v
```

If necessary, you can change the version of WSL using: 
```bash
wsl --set-version Ubuntu−20.04 2
```
We advise you to setup the default version of WSL and the default distribution as follow:

```bash
wsl --set-default-version 2
wsl --setdefault Ubuntu−20.04
```

You should now be able to launch and terminate a WSL session of Ubuntu-20.04 using:

```bash
wsl 
wsl -t Ubuntu−20.04
```

If you encounter any issue, please refer to the official website provided at the start of this section.

<!-- Write WSL-specific installs -->

### Install Ubuntu on your computer

On most computers (macOS, Windows, and Linux), you can install another OS
using a *dual boot*. The internet is full of tutorial on how to install
Ubuntu in dual boot. Please make sure to install the correct version.

## Common Installation Steps

<!-- Write all common installs -->

### Installing CMake and Make

```bash
sudo apt-get install cmake
```

### Installing GNU Radio

For the LimeSDR to work, we need to install GNU Radio **3.8** and no any version higher. To do so:

```bash
sudo add-apt-repository ppa:gnuradio/gnuradio−releases−3.8
sudo apt-get update
sudo apt-get install gnuradio xterm python3-gi gobject-introspection gir1.2-gtk-3.0
```

You should now be able to open GNU Radio with its GUI with the following command. *If you use Windows with WSL, please refer first to the next section*

```bash
gnuradio-companion
```

### (Specific to Windows user of WSL) : Setup of graphical display for WSL

WSL 2 does not have an X server for displaying graphical applications. A X server is a program whose primary task is to coordinate the input and output of its clients to and from the rest of the operating system, the hardware, and each other. They exist several ones and we propose here to install [Xming](https://sourceforge.net/projects/xming/) with all default settings. We here follow this [https://wiki.gnuradio.org/index.php/WindowsInstall#WSL_|_Ubuntu](guide) from GNU Radio wiki. With Xming installed, you can then launch *XLaunch* from the Start Menu and click next until the "Specify parameter settings" screen. Check "No Access Control" then click next, then finish. On your Ubuntu distribution, enter the following command:

```bash
sudo apt install libgtk-3-dev
```

Finally to forward the display on the proper port, the following lines should be added to the *.bashrc* file of your Ubuntu distribution:

```bash
export DISPLAY=$(awk '/nameserver / {print $2; exit}' /etc/resolv.conf 2>/dev/null):0
export LIBGL_ALWAYS_INDIRECT=1
```
Restart the terminal and you should now be able to launch GNU Radio GUI as follow:

```bash
gnuradio-companion
```

If this does not work, you might need to change the two exports above to:
```bash
export DISPLAY=:0.0
export LIBGL_ALWAYS_INDIRECT=1
```

### Installing the different LimeSDR components

We can now install the different components required to use the LimeSDR with GNURadio. We here follow the information provided [here](https://wiki.myriadrf.org/Lime_Suite
) by the company who sells the LimeSDR, *Myriad-RF*.

#### Installing LimeSuite
We start by installing *LimeSuite*, i.e., a collection of software supporting several hardware platforms including the LimeSDR.

```bash
sudo add-apt-repository -y ppa:myriadrf/drivers
sudo apt-get update
sudo apt-get install limesuite liblimesuite-dev limesuite-udev limesuite-images
sudo apt-get install soapysdr-tools soapysdr-module-lms7
```

#### Installing Gr-LimeSDR

Finally, we need to install *LimeSDR* which is a low cost, open source software defined radio (SDR) platform. To do so, we use the following command, taken from the [official website](https://wiki.myriadrf.org/Gr-limesdr_Plugin_for_GNURadio).

```bash
sudo add-apt-repository ppa:myriadrf/gnuradio
sudo apt-get update
sudo apt-get install gr-limesdr
```

#### Testing the installation of LimeSDR

You can launch GNU Radio companion. On the right part of the window, scroll. LimeSDR components should now appear at the end of the list.

###  (Specific to Windows user of WSL) Connect the LimeSDR to the WSL via USB pass-through

The LimeSDR will be connected to your computer but should be interfaced with your Ubuntu and not Windows. To do so, we will need to create a passthrough using [USBIPD-WIN](https://learn.microsoft.com/en-us/windows/wsl/connect-usb) supported by Microsoft. Go to this [git project](https://github.com/dorssel/usbipd-win/releases) and download the *.msi* file of the latest version and install it. On Ubuntu, you will need to run the two following commands:

```bash
sudo apt install linux-tools-generic hwdata
sudo update-alternatives --install /usr/local/bin/usbip usbip  /usr/lib/linux-tools/*-generic/usbip 20
```

You can now attach any device from your computer to Ubuntu. To do so, open a PowerShell or prompt in Windows and use the three following commands to respectively list all the USB devices connected to windows, attach to WSL the device with the given busid, detach the device from WSL.

```bash
usbipd wsl list
usbipd wsl attach --busid <busid>
usbipd wsl detach --busid <busid>
```

If you want to simplify the connection of a device to WSL, a graphical interface exist, additionally providing an auto-attach function. The latest installer can be found [here](https://gitlab.com/alelec/wsl-usb-gui/-/releases)

### Installation of STM32CubeIDE

In order to program and configure the MCU, we will use the software *STM32CubeIDE* from ST. To download the installer, go to the following [website](https://www.st.com/en/development-tools/stm32cubeide.html) and select the latest version of the installer for your operating system. You might be asked to create an account. You can then proceed to the download and installation.

### Installation of Quartus

Most of you probably follow the course LELEC2531 for which you have installed *Quartus Prime Lite 18.1*. If you have already  it installed, you can skip this paragraph. To install Quartus, follow this link: [Quartus Website](https://www.intel.com/content/www/us/en/products/details/fpga/development-tools/quartus-prime/resource.html). Then click on the *Quartus Prime Lite* version for you OS, select the 18.1 version and follow the download and install instructions.


If you already have Quartus installed, you might not have the required device support package for the MAX 10 device family that we use in this project. You can download the package [here](https://www.intel.com/content/www/us/en/products/details/fpga/development-tools/quartus-prime/resource.html) by first clicking on your Quartus installation, most probably the Prime Lite. Then select the Quartus version installed on your computer.
Under the download section, go in the *"Individual Files"* and download the *"Intel® MAX® 10 Device Support"*. On your computer, launch the *"Device Installer (Quartus Prime)"* from the start menu. If you cannot find it, it should be located in your Quartus installation folder at 
```bash
intelFPGA/18.1/quartus/common/devinfo/dev\_install"
```
The programm will ask you to select the folder in which the downloaded file is located, it will then automatically detect the MAX 10 device support file. You can proceed to the installation.