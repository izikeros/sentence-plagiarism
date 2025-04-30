# Sets the default shell for executing commands as /bin/bash and specifies command should be executed in a Bash shell.
SHELL := /bin/bash

# Color codes for terminal output
COLOR_RESET=\033[0m
COLOR_CYAN=\033[1;36m
COLOR_GREEN=\033[1;32m

SRC_FILES = sentence_plagiarism
SRC_AND_TEST_FILES = sentence_plagiarism tests

# Use conditional logic to adapt commands for macOS vs. Linux.
SED_CMD := $(shell if [ "$(shell uname)" = "Darwin" ]; then echo "gsed"; else echo "sed"; fi)


# Defines the targets help, install, dev-install, and run as phony targets.
#  Phony targets are targets that are not really the name of files that are to be built.
#  Instead, they are treated as commands.
.PHONY: help install create-env create-venv install-deps install-dev-deps poetry-plugins farewell clean test coverage coverage-show format lint lint-stats fix type audit license license-unapproved-licenses license-unapproved-packages requirements-txt bandit

# Sets the default goal to help when no target is specified on the command line.
.DEFAULT_GOAL := help

# Disables echoing of commands. The commands executed by Makefile will not be
#  printed on the console during execution.
.SILENT:

help: ## Show all Makefile targets.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[33m%-30s\033[0m %s\n", $$1, $$2}'

install: create-env create-venv install-with-dev-deps poetry-plugins farewell ## Create .env file, virtual environment, install dependencies, and install dev dependencies.

create-env: ## Create a .env file from the .env.template file.
	@[ ! -f .env ] && echo -e "$(COLOR_CYAN)Creating .env file...$(COLOR_RESET)" && \
	cp .env.template .env || \
	echo -e "$(COLOR_CYAN).env file already exists, skipping creation.$(COLOR_RESET)"

create-venv: ## Create a virtual environment in the .venv folder in current directory.
	@echo -e "$(COLOR_CYAN)Creating virtual environment in the project folder...$(COLOR_RESET)" && \
	poetry config --local virtualenvs.in-project true
	poetry env use python3.11

install-deps: ## Install the dependencies.
	@echo -e "$(COLOR_CYAN)Installing dependencies...$(COLOR_RESET)" && \
	poetry install

install-with-dev-deps: ## Install dev dependencies.
	@echo -e "$(COLOR_CYAN)Installing dev dependencies...$(COLOR_RESET)" && \
	poetry install --with dev

poetry-plugins: ## Install poetry plugins assuming poetry installed via pipx.
	@echo -e "$(COLOR_CYAN)Installing poetry plugins...$(COLOR_RESET)" && \
	pipx inject poetry poetry-audit-plugin
	pipx inject poetry poetry-plugin-export
	pipx inject poetry poetry-dynamic-versioning
	poetry config warnings.export false

farewell: ## Print a farewell message.
	@echo -e "$(COLOR_GREEN)All done!$(COLOR_RESET)"

clean: ## Clean up the project by removing the pycache and pyc files.
	@echo -e "$(COLOR_CYAN)Cleaning up...$(COLOR_RESET)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +

test: ## Run the tests with pytest.
	@echo -e "$(COLOR_CYAN)Running tests...$(COLOR_RESET)"
	pytest --log-cli-level=INFO -rA tests/

test-unit: ## Run the unit tests with pytest.
	@echo -e "$(COLOR_CYAN)Running unit tests...$(COLOR_RESET)"
	pytest --log-cli-level=INFO -rA tests/unit/

coverage: ## Run the tests with pytest and generate a coverage report.
	@echo -e "$(COLOR_CYAN)Running tests with coverage...$(COLOR_RESET)"
	pytest --cov=retriever --cov=qa_plugin --cov-report=html --cov-report=term-missing tests/

coverage-show: ## Open a coverage report in a default browser.
	@echo -e "$(COLOR_CYAN)Opening coverage report in the browser...$(COLOR_RESET)"
	@if [ "$(shell uname)" = "Darwin" ]; then \
		open htmlcov/index.html; \
	elif [ "$(shell uname)" = "Linux" ]; then \
		xdg-open htmlcov/index.html; \
	elif [ "$(shell uname | cut -c1-7)" = "MINGW64" ] || [ "$(shell uname | cut -c1-5)" = "MSYS" ]; then \
		start htmlcov/index.html; \
	else \
		echo "Unsupported OS: Unable to open coverage report"; \
	fi

format: ## Running code formatter: black and isort
	@echo "(isort) Ordering imports..."
	@isort $(SRC_AND_TEST_FILES)
	@echo "(black) Formatting codebase..."
	@black --config pyproject.toml $(SRC_AND_TEST_FILES)
	@echo "(ruff) Running fix only..."
	@ruff check $(SRC_AND_TEST_FILES) --fix-only

lint: ## Run the linter (ruff) to check the code style.
	@echo -e "$(COLOR_CYAN)Checking code style with ruff...$(COLOR_RESET)"
	ruff check $(SRC_AND_TEST_FILES)

lint-stats: ## Run the linter (ruff), display only count of violations.
	@echo -e "$(COLOR_CYAN)Counting ruff violations...$(COLOR_RESET)"
	ruff check $(SRC_AND_TEST_FILES) --statistics

fix: ## Run ruff and fix the issues that are fixable automatically.
	@echo -e "$(COLOR_CYAN)Fixing code style issues with ruff...$(COLOR_RESET)"
	ruff check $(SRC_AND_TEST_FILES) databricks --fix

type: ## Running type checker: pyright
	@echo "(pyright) Typechecking codebase..."
	PYRIGHT_PYTHON_FORCE_VERSION=latest pyright $(SRC_FILES)

audit: ## Run the check for vulnerabilities in the dependencies.
	@echo -e "$(COLOR_CYAN)Running security audit based on 'safety'...$(COLOR_RESET)"
	poetry audit

requirements-txt: ## Export the requirements to a requirements.txt file.
	# NOTE: This requires the 'poetry-plugin-export to be installed.
	# to install, use e.g. $ poetry self add poetry-plugin-export
	@echo -e "$(COLOR_CYAN)Exporting requirements...$(COLOR_RESET)"
	poetry export -f requirements.txt --output $(R_PYPROJECT) --without-hashes
	$(SED_CMD) -E 's/;.*//' $(R_PYPROJECT) > requirements.txt.tmp && \
	rm $(R_PYPROJECT) && \
	echo "# This file is autogenerated by Makefile (requirements-txt) from the pyproject.toml" > $(R_PYPROJECT) && \
	cat requirements.txt.tmp >> $(R_PYPROJECT) && \
	rm requirements.txt.tmp
	echo -e "$(COLOR_GREEN)Requirements exported to $(R_PYPROJECT)$(COLOR_RESET)"

bandit: ## Run the bandit security linter.
	# check for high and medium severity issues
	@echo -e "$(COLOR_CYAN)Running bandit...$(COLOR_RESET)"
	bandit -r $(SRC_FILES) -ll -iiś

changelog: ## Generate a changelog using git-cliff
	git-cliff -o CHANGELOG.md
