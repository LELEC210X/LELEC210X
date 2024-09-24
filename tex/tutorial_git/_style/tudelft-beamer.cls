\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{_style/tudelft-beamer}[2023/11/17 v2022.0 TU Delft presentation class]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{beamer}}
\ProcessOptions*
\LoadClass{beamer}

\usepackage[absolute,overlay]{textpos}
\setlength{\TPHorizModule}{\paperwidth}
\setlength{\TPVertModule}{\paperheight}
\usepackage{tikz}

\usepackage{mathtools}
%\usepackage{amsfonts}
%\usepackage{amsthm}
\usepackage{siunitx}
%\usepackage{MnSymbol,wasysym}
\usepackage{qrcode}
\usepackage[utf8]{inputenc}

% BIB SETTINGS
\usepackage[
    backend=biber,
    giveninits=true,
    maxnames=30,
    maxcitenames=20,
    uniquename=init,
    url=false,
    style=authoryear,
]{biblatex}
\setlength\bibitemsep{0.3cm} % space between entries in the reference list
\renewcommand{\bibfont}{\normalfont\scriptsize}
\renewcommand{\cite}[1]{\footnote<.->[frame]{\fullcite{#1}}}

\usepackage{_style/tudelft-fonts}
\usepackage{_style/tudelft-colors}
\usepackage{_style/tudelft-frame}

\colorlet{primary}{tud primary}
\setbeamercolor{background canvas}{bg=primary,fg=white}

\if@fourier
  \usefonttheme{serif}
  \let\robotoslab\bfseries
\fi

\setbeamerfont{structure}{series=\robotoslab}
\setbeamercolor{structure}{fg=primary}
\setbeamertemplate{navigation symbols}{}


\newcommand{\tudlogo}[1][]{\begin{tikzpicture}[even odd rule, x=1ex, y=1ex, baseline=0.088ex]
	\begin{scope}
	  %\clip (0, -.04) rectangle (7.356, 2.9) (1.4, -0.01) rectangle (3, 1.6);
	  \includegraphics[height=2.939ex]{figures/uclouvain-logo};
	\end{scope}
	\begin{scope}[fill=#1]
	  %\clip (1.4, -0.01) rectangle (3, 1.6);
	  \includegraphics[height=2.939ex]{figures/uclouvain-logo};
	\end{scope}
  \end{tikzpicture}}
  
  \newcommand{\tudflame}[1][1ex]{%
  \begin{tikzpicture}[x=#1, y=#1]
	  \clip (-2.435, 0) rectangle ++(1, 1);
	  \node[anchor=base] at (0, -1.17) {\scalebox{2.2}{\includegraphics[height=#1]{figures/uclouvain-logo}}};
  \end{tikzpicture}}

  \newcommand{\grid}{%
  \begin{abstikz}[font=\tiny, opacity=0.5]
    \foreach \x in {0.005,0.01,...,1} {
      \draw[gray, very thin] (\x, 0) -- ++(0, 1);}
    \foreach \y in {0.01,0.02,...,1} {
      \draw[gray, very thin] (0, \y) -- ++(1, 0);}
    \foreach \x in {0.00001,0.05002,...,1} {
      \draw[thick] (\x, 0) -- ++(0, 1);
      \node[anchor=south west, rotate=90] at (\x\paperwidth-0.5ex, \paperheight-2.5ex) {\x};}
    \foreach \y in {0.00001,0.05002,...,1} {
      \draw[thick] (0, \y) -- ++(1, 0);
      \node[anchor=south west] at (\paperwidth-2.5ex, \y\paperheight-0.5ex) {\y};
      \node[anchor=south west] at (\paperwidth-2.5ex, \y\paperheight-0.5ex) {\y};}
  \end{abstikz}%
}
