# LaTeX document compilation

<!-- prettier-ignore -->
> [!TIP]
> [_You can **download** the latest version of the PDF here._][latest-pdf-url]

Each subdirectory contains a LaTeX project, where the main file is `main.tex`.

Compilation is automated with `latexmk` and `make`.

Namely:

- `make pdf` compiles (recursively) the PDF(s)
- `make clean` removes all build artifacts
- `make zip` creates one zip file with all PDFs

> [!TIP]
> To speed-up the compilation process, run
> `make pdf -j$(nproc)` to use all cores/threads.

> [!NOTE]
> The `wireless_*` projects use the `minted` package for code highlighting, which requires `Pygments` to be installed. Read how to install `minted`'s dependencies [here](https://texdoc.org/serve/minted.pdf/0).

[latest-pdf-url]: https://nightly.link/LELEC210X/LELEC210X/workflows/build_tex/main/tex-documents.zip
