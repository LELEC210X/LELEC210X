pdf:
	latexmk main.tex -pdf -shell-escape -jobname=wireless_simulations

clean:
	latexmk -CA main.tex -pdf -jobname=wireless_simulations

check:
	-chktex main.tex -pdf
