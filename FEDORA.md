# Installation guidelines on Fedora 40

This document summaries all the commands needed to reproduce a development environment on Fedora 40,
as this OS is similar to that of UCLouvain's computers.

> [!NOTE]
> The computers are based on [Fedora EPEL 8](https://docs.fedoraproject.org/en-US/epel/getting-started/),
> that happens to ship [GNU Radio 3.8](https://packages.fedoraproject.org/pkgs/gnuradio/gnuradio/epel-8.html).
>
> However, [it looks impossible (?)](https://stackoverflow.com/a/57317248/14968272)
> to install packages from the EPEL 8 repository, on Fedora 40 OSes...
>
> Therefore, this tutorial is incomplete.

## Install Python 3.8

By default, Fedora 40 comes with Python 3.12 installed, but we need Python 3.8 and pip.

First, set the current version as an alternative (i.e., number `1`):

```bash
sudo alternatives --install /usr/bin/python python /usr/bin/python3.12 1
```

Then, install Python 3.8 and pip:

```bash
sudo dnf install -y python3.8
sudo dfn install -y python3-pip
```

Finally, register the new version as a second alternative (i.e., number `2`) and
switch Python versions:

```bash
sudo alternatives --install /usr/bin/python python /usr/bin/python3.8 2
sudo alternatives --config python
```

You can verify your installation by running the following command:

```bash
python --version
```

## Install Poetry

Installation of Poetry is then straightforward:

```bash
curl -sSL https://install.python-poetry.org | python -
```

## Install FFmpeg

To install FFmpeg, you first need to add a new repository:

```bash
sudo dnf -y install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
sudo dnf -y install https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
sudo dnf update
sudo dnf install -y ffmpeg
```

## Install cmake

```bash
sudo dnf install -y cmake
```

## Install GNU Radio

W.I.P.
