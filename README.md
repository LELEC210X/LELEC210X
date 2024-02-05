# LELEC210X project

This repository contains every thing you (student) need for the LELEC210X project.

The current directory, which we will refer to as **root**, contains instructions for:

1. the Git project initialization;
2. how to install dependencies;
3. how to keep your code clean;
4. and how to build the whole project.

> [!NOTE]
> Part 4 will only be useful once you have read and worked through all
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

### 1.1 Understanding Git

For this project, you will need to know more than just the **basic knowledge**
about Git.

You need to make sure to understand the following concepts:

- Staging and committing files;
- Pulling and pushing changes;
- Git branches;
- Clone and Fork;
- Remotes;
- Merge and rebase.

To this end, we recommend the excellent
[Git Tutorial from W3schools](https://www.w3schools.com/git/),
and more specifically the following sections:

- Git Tutorial
  - Git Intro
  - Git Get Started
  - Git New Files
  - Git Staging Environment
  - Git Commit
  - Git Branch
  - Git Branch Merge
- Git and GitHub
  - GitHub Get Started
  - Pull from GitHub
  - Push to GitHub
- Git Contribute
  - GitHub Fork
  - Git Clone from GitHub

> [!NOTE]
> The above tutorial assumes a Unix (e.g., Ubuntu / macOS)
> terminal, so some commands like `ls` may not
> work on Windows.

You are still encouraged to read through all the other sections!

Then, we recommend you to read the excellent
[Mergin vs. rebasing](https://www.atlassian.com/git/tutorials/merging-vs-rebasing)
([French version](https://www.atlassian.com/fr/git/tutorials/merging-vs-rebasing))
guide from Atlassian. This will be important when you will need to synchronize changes
from different people.

### 1.2 Hosting your code

As mentioned in the tutorial, you can host your Git repository
on any platform you would like, as long as we can have access
to it if needed.

We decided to go for [GitHub](https://github.com/), but
you can also choose [UCLouvain's Forge](https://forge.uclouvain.be/),
or any other platform (each platform has its specific free features).

See the [Clone or Work](/wiki/Clone-or-Fork) wiki to understand how to
get create your copy of this project, while maintaining it synchronized
with potential updates.

### 1.3 Recommended Git tools

Advanced Git users may prefer to use it via the terminal (i.e., command-line),
but using a graphical interface can be way more convenient to visual to current
status of your different branches, or to resolve conflicts easily.

There exist plently of applications, but we recommend:

There are plenty of them, and here are a few we recommend:

- [GitKraken](https://www.gitkraken.com/),
  a Git tool for basic and advanced usage,
  with
  [pro-version for free for students](https://www.gitkraken.com/github-student-developer-pack).
  This is maybe the **best solution** for beginners;
- [Git's Visual Studio Code extension](https://code.visualstudio.com/docs/sourcecontrol/overview),
  which offers everything you need inside the Visual Studio Code editor;
- and [GitHub Desktop](https://desktop.github.com/),
  a very simple but good Git application.

## 2. Installing dependencies

As this project requires quite a lot of dependencies, the teaching staff is
providing a [VirtualBox](https://www.virtualbox.org/) (VB) image. Put simply,
VB is a free tool that a allows to run the same set of software, thanks to
**virtualization**, regardless of your computer.

> [!NOTE]
> Quartus is not part of the installed softwares,
> and we assume you have it installed it from a previous class.

### 2.1 Dealing with a slow VB

Despite being very useful, VB has the disavantage that it can be **quite slow**.
To cope with this issue, there exist multiple solutions (from easiest for hardest):

1. Increase the resources allocated to VB (in `Settings->System`): either the
   memory or the number of CPUs;
2. _(Debian only)_ Manually install the software listed on the install page;
3. _(Windows only)_ Install [WSL](https://learn.microsoft.com/en-us/windows/wsl/install)
   and refer to 2;
4. _(Windows or macOS only)_ Install Ubuntu in dual-boot and refer to 2.

Note that the last two steps require the most disk memory, but will most
probably produce that fastest experience in the end.

For the list of softwares needed for this project,
see [INSTALL.md](./INSTALL.md).

## 3. Keeping your code clean

> [!NOTE]
> Please follow the [install guide](INSTALL.md) first.

A good rule when programming in a team is to follow the same formatting rules.

Since it can become tedious to manually format all codes to match a given set
of rules, one can use a formatter or a linter.

While a linter will only warn you about potential problems in your code,
the formatter will automatically edit your code to fix those problems.
Note that using a linter is still useful since the range of rules covered by
linters is usually much larger than those of a formatter.

To this end, we use `pre-commit`. It can be used as follows:

```bash
poetry run pre-commit run --all-files
```

> [!TIP]
> After running `pre-commit`, you will likely see **many** error messages:
> do not run away! Most of them are just good tips to help you
> improving your coding practices, and fixing all of them takes quite some time!
>
> If you want to help us improve this repository, you can do so by
> fixing a few error messages here and there ;-)

If you want to run `pre-commit` on a subset of your files, use the following:

```bash
poetry pre-commit run --files file1 file2 ...
# E.g., on all files in `tex/`
find tex/ | xargs poetry run pre-commit run --files
```

> [!NOTE]
> The above command will likely only work on Linux or macOS.

If you want to disallow you from pushing unformatted code,
you can install a git hook.
A git hook is simply an action that will run every time you try to commit
and check wether you passe or not the format rules.

To this end, please run:

```bash
poetry run pre-commit install
```

After this, you should always run:

```bash
poetry pre-commit run
```

to format staged files, before committing them.

## 4. Building the whole project

See [INTEGRATION](INTEGRATION.md).
