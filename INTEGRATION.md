# Integration

This document summarizes the different steps needed to integrate all the
separate parts of this project into one working pipeline.

## Requirements

We assume that you have completed all previous assigments,
and that missing code fragments have been successfully filled.

Make sure that your repository is up-to-date with our main branch, and
that you installed the latest Python dependencies with:

```
poetry install
```

## Steps

Setting-up a working telecommunication chain can be performed with
the following steps[^1]:

1. *(Any)* program your LimeSDR-Mini with Quartus,
   using the following project: <TODO>;
2. *(Any)* program your Nucleo board with STM32CubeIDE,
   using the following project: <TODO>;
3. *(Linux)* open the <TODO> project file with GNU Radio,
   and generate the Python script(s);
4. *(Linux)* run your GNU Radio script either from GNU Radio or from the terminal;
5. *(Any)* in another terminal window, run `poetry run auth | poetry run classify`;
6. and that all!

[^1]: in parentheses, the host / guest OS that is needed to run the commands.
  Any refers to any OS (best to use your host OS here).

## Customizing

Most parameters in scripts have default values that can be changed in the Python
files, via command-line options, or via environ variables.

For parameters that are use in multiple places, like `melvec_length`,
it is very important to use the same values all across your different
project parts.
