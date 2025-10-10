pdf:
	python3 ../extract_code.py ../../telecom/python/telecom/chain.py::Chain::modulate > modulate.py

	latexmk main.tex -pdf -shell-escape -jobname=h3a_wireless_simulations

clean:
	latexmk -CA main.tex -jobname=h3a_wireless_simulations

check:
	chktex main.tex
