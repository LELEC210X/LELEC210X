# LELEC210x project

This repository contains every thing you (student) need for the LELEC210x project.

The current directory, which we will refer to as **root**, contains instructions for:

1. the Git project initialization;
2. how to install dependencies;
3. how to keep your code clean;
4. and how to build the whole project.

> Note: part 3 will only be useful once you have read and worked through all
> the intermediate hands-on sessions.

Subdirectories are organized as follows:

- [`auth/`](auth/):
  hands-on related to the authentification part.
- [`common/`](common/):
  shared tools across different parts.
- [`classification/`](classification/):
  hands-on related to the classification part.
- [`fpga`](fpga/):
  hands-on related to the FPGA part and Quartus project for the LimeSDR Mini.
- [`leaderboard/`](leaderboard/):
  code to run the leaderboard web-server, useful for locally testing your
  setup before the contest.
- [`mcu/`](mcu/):
  hands-on related to the MCU part and STM32CubeIDE project for the Nucleo board.
- [`telecom/`](telecom/): hands-on related to the telecom part,
  simulation framework and GNU Radio modules.
- [`tex/`](tex/): LaTeX projects for this course.
  PDFs are provided on [Moodle](https://moodle.uclouvain.be/course/view.php?id=4829),
  but you can build them from source, see [`tex/README.md`](tex/README.md).

## 1. Using Git - Mandatory

This project is fully contained within one single git repository.

For this course, we have a "**no git, no help**" policy.
That means that, if you ever need help from a professor or a teaching assistant,
you **must** be able to provide a **git diff** view of your most recent changes.

### 1.1 I am new to Git

You have never used Git? Or your skills are limited to _pushing_ and _pulling_
commits? Then it's worth consedering to follow a few tutorials!

The Internet is full of guides about Git, but we can recommend the following tutorial:

- [What is Git?](https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F);
- [How to use Git and GitHub introduction (video)](https://www.youtube.com/watch?v=HkdAHXoRtos&ab_channel=Fireship);
- [Git, Github, and GitHub desktop for beginners (video)](https://www.youtube.com/watch?v=8Dd7KRpKeaE&ab_channel=CoderCoder);
- or [GitHub's Hello World](https://docs.github.com/en/get-started/quickstart/hello-world).

### 1.2 Hosting your code

You are free to use [GitHub](https://github.com/),
[UCLouvain's Forge](https://forge.uclouvain.be/),
[GitLab](https://about.gitlab.com/) or any other platform to host your code, as long as you use Git. You do not need to give access to your code to the teaching staff.

See the [Clone or Work](/wiki/Clone-or-Fork) wiki.

### 1.3 Recommended Git tools

Advanced Git users may prefer to use it via the terminal (i.e., command-line),
but people may prefer to use a more classical application.
There are plenty of them, and here are a few we recommend:

- [Git's Visual Studio Code extension](https://code.visualstudio.com/docs/sourcecontrol/overview),
  which offers everything you need inside the Visual Studio Code editor;
- [GitHub Desktop](https://desktop.github.com/),
  a very simple but good Git application;
- and [GitKraken](https://www.gitkraken.com/),
  a Git tool for advanced usage,
  with
  [pro-version for free for students](https://www.gitkraken.com/github-student-developer-pack).

---

We **highly recommend** you to start your work from this repository,
to take the benefits of using git!
Feel free the modify the code, commit changes, create branches, etc.

## 2. Installing dependencies

As this project requires quite a lot of dependencies, the teaching staff is
providing a [VirtualBox](https://www.virtualbox.org/) (VB) image. Put simply,
VB is a free tool that a allows to run the same set of software, thanks to
**virtualization**, regardless of your computer.

> **NOTE**: Quartus is not part of the software installed,
> and we assume you have it installed it from a previous class.

### 2.1 Dealing with a slow VB

Despite being very useful, VB has the disavantage that it can be **quite slow**.
To cope with this issue, there exist multiple solutions (from easiest for hardest):

1. Increase the resources allocated to VB (in `Settings->System`): either the
   memory or the number of CPUs;
2. _Debian-only_ Manually install the software listed on the install page;
3. _Windows-only_ Install [WSL](https://learn.microsoft.com/en-us/windows/wsl/install)
   and refer to 2;
4. _Windows-or-macOS-only_ Install Ubuntu in dual-boot and refer to 2.

Note that the last two steps require the most disk memory, but will most
probably produce that fastest experience in the end.

For the list of softwares needed for this project,
see [INSTALL.md](./INSTALL.md).

## 3. Keeping your code clean

A good rule when programming in a team is to follow the same formatting rules.

Since it can become tedious to manually format all codes to match a given set
of rules, one can use a formatter or a linter.

While a linter will only warn you about potential problems in your code,
the formatter will automatically edit your code to fix those problems.
Note that using a linter is still useful since the range of rules covered by
linters is usually much larger than those of a formatter.

To this end, you can use `pre-commit`. Its installation is very simple:

```bash
pip install pre-commit
```

and can be used as follows:

```bash
pre-commit run --all-files
```

If you want to run `pre-commit` on a subset of your files, use the following:

```bash
pre-commit run --files file1 file2 ...
# E.g., on all files in `tex/`
find tex/ | xargs pre-commit run --files
```

If you want to disallow you from pushing unformatted code,
you can install a git hook.
A git hook is simply an action that will run every time you try to commit
and check wether you passe or not the format rules.

To this end, please run:

```bash
pre-commit install
```

After this, you should always run:

```bash
pre-commit run
```

to format staged files, before committing them.

## 4. Building the whole project

See [INTEGRATION](INTEGRATION.md).
