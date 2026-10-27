# Build the paper. Run `make results figures` first when the benchmark results change.
#   make            compile main.pdf
#   make results    regenerate tables and the chart from bench/results
#   make figures    render the Mermaid sources to vector PDF
#   make shots      render the terminal screenshots from live auxflow output
#   make clean
#
# IEEEtran selects the Times font. If the Times metrics are missing, fallback-fonts/ maps
# the Times families to Computer Modern so the paper still builds.
ifeq ($(shell kpsewhich ptmr7t.tfm),)
export TEXINPUTS := $(CURDIR)/fallback-fonts:$(TEXINPUTS):
endif

main.pdf: main.tex refs.bib generated/macros.tex $(wildcard figures/*.pdf figures/*.png)
	pdflatex -interaction=nonstopmode main.tex
	bibtex main
	pdflatex -interaction=nonstopmode main.tex
	pdflatex -interaction=nonstopmode main.tex

results:
	python3 make_results.py

figures:
	bash render_figures.sh

shots:
	cd .. && python3 scripts/render_terminal_screenshots.py

clean:
	rm -f main.aux main.bbl main.blg main.log main.out main.pdf mfput.log missfont.log
