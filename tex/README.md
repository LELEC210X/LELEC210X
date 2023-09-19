# LaTeX document compilation

Each subdirectory contains a LaTeX project, where the main file is `main.tex`.

Compilation is automated with `latexmk` and `make`.

Namely:

- `make pdf` compiles (recursively) the PDF(s)
- `make clean` removes all build artifacts
- `make zip` creates one zip file with all PDFs

> NOTE: `wireless_*` projects use the `minted` package for code highlighting, which requires `Pygments` to be installed. Read how to install `minted`'s dependencies [here](https://texdoc.org/serve/minted.pdf/0).
