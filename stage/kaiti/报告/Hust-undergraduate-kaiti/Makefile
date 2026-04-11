FILE=Hust-undergraduate-kaiti

.PHONY: run

TEX = xelatex -interaction=errorstopmode
BIB = bibtex
RM = rm -fr

run: $(FILE).pdf
	cmd /c start $(FILE).pdf

$(FILE).pdf: $(FILE).tex $(FILE).aux $(FILE).toc $(FILE).bbl
	$(TEX) $(FILE)
	$(TEX) $(FILE)

$(FILE).bbl: $(FILE).bib $(FILE).aux Hust-undergraduate-kaiti.cls gbt7714-Hust.bst
	$(BIB) $(FILE)

$(FILE).aux: $(FILE).tex Hust-undergraduate-kaiti.cls HustBlack.eps HustGreen.eps
	$(TEX) $(FILE)

$(FILE).toc: $(FILE).aux

push:
	git add *
	git commit -m "fix some bug"
	git push origin main

clean:
	$(RM) $(FILE).pdf $(FILE).toc $(FILE).log $(FILE).aux $(FILE).lof $(FILE).lot $(FILE).bbl $(FILE).blg
