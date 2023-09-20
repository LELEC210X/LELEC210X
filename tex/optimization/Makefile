pdf:
	latexmk main.tex -pdf -jobname=optimization
clean:
	latexmk -CA main.tex -pdf -jobname=optimization

check:
	-chktex main.tex -pdf
