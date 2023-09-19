pdf:
	latexmk main.tex -shell-escape -jobname=wireless_measurements
clean:
	latexmk -CA main.tex -jobname=wireless_measurements

check:
	-chktex main.tex
