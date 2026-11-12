# Makefile for entity-resolution-multicut.
# The target names are fixed by spec.md section 3 and CLAUDE.md.
# On Windows, run these from Git Bash or WSL, or use the underlying commands directly.

PYTHON ?= python

.PHONY: help test reproduce-min reproduce report app clean

help:
	@echo "Targets:"
	@echo "  make test           Full test suite with coverage"
	@echo "  make reproduce-min  Regenerate every Level M results file and figure"
	@echo "  make reproduce      Regenerate everything, both levels"
	@echo "  make report         Compile report/report.pdf"
	@echo "  make app            Launch the demonstration application (Level F)"

test:
	$(PYTHON) -m pytest

reproduce-min:
	$(PYTHON) -m ermc.experiments.run --level min

reproduce:
	$(PYTHON) -m ermc.experiments.run --level full

report:
	cd report && latexmk -pdf report.tex

app:
	$(PYTHON) -m streamlit run app/app.py

clean:
	rm -rf .pytest_cache .coverage htmlcov **/__pycache__ *.egg-info
