export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

activate: ## Activate the virtual environment
	conda activate datapipeline

install: ## Install requirements
	pip install -r requirements.txt

precommit: ## Install requirements
	pre-commit install

setup: activate install precommit ## Setup the environment

black: ## Format code with Black
	black --check datapipeline

test: ## Run unit tests
	pytest datapipeline

clean: ## Remove Python file artifacts
	find . -name '*.pyc' -exec rm -rf {} +
	find . -name '*.pyo' -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -rf {} +