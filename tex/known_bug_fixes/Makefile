pdf:
	latexmk main.tex -jobname=known_bugs_fixes

clean:
	latexmk -CA main.tex -jobname=known_bugs_fixes

check:
	-chktex main.tex
