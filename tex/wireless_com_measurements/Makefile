pdf:
	latexmk main.tex -pdf -shell-escape -jobname=wireless_measurements
clean:
	latexmk -CA main.tex -pdf -jobname=wireless_measurements

check:
	-chktex main.tex -pdf
