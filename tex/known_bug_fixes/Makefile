pdf:
	latexmk main.tex -pdf -jobname=known_bugs_fixes

clean:
	latexmk -CA main.tex -pdf -jobname=known_bugs_fixes

check:
	-chktex main.tex -pdf
