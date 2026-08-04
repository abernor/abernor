# AI Orchestrator — convenience targets.
# Delegates to run.sh, which handles venv, deps, and .env bootstrap.

.PHONY: help run web cli setup clean

help:  ## Show this help
	@echo "AI Orchestrator — make targets:"
	@echo "  make run             Launch the Streamlit dashboard"
	@echo "  make cli GOAL=\"...\"  Run the pipeline from the CLI"
	@echo "  make setup           Create venv + install deps + scaffold .env"
	@echo "  make clean           Remove venv, caches, and workspace output"

run web:  ## Launch the Streamlit dashboard
	./run.sh web

cli:  ## Run the pipeline from the CLI (requires GOAL="your goal")
	@if [ -z "$(GOAL)" ]; then \
		echo 'Usage: make cli GOAL="Build a REST API"'; exit 1; \
	fi
	./run.sh cli "$(GOAL)"

setup:  ## Create venv, install deps, scaffold .env (no launch)
	./run.sh setup

clean:  ## Remove venv, caches, and workspace output
	rm -rf .venv workspace
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
