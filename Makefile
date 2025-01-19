VENV = .venv
VENV_BIN = $(VENV)/bin
PYTHON = $(VENV_BIN)/python
PIP = $(VENV_BIN)/pip
PYTHON_VERSION = 3.11.10

# ANSI color codes
GREEN=$(shell tput -Txterm setaf 2)
YELLOW=$(shell tput -Txterm setaf 3)
RED=$(shell tput -Txterm setaf 1)
BLUE=$(shell tput -Txterm setaf 6)
RESET=$(shell tput -Txterm sgr0)

## Install the project
install:
	@echo "$(GREEN)Installing the project...$(RESET)"
	@$(MAKE) -s configure-python-env
	@$(MAKE) -s install-dependencies
	@echo "$(GREEN)Install completed successfully.$(RESET)"

configure-python-env:
	@echo "$(YELLOW)Checking Python installation...$(RESET)"
	@pyenv --version || (echo "$(RED)Pyenv is necessary. If you don't know how to proceed, follow the onboarding guide!!!"; exit 1)
	@poetry --version || (echo "$(RED)Poetry is necessary. If you don't know how to proceed, follow the onboarding guide!!!"; exit 1)

	@if pyenv versions | grep -q "$(PYTHON_VERSION)"; then \
		echo "$(BLUE)Python $(PYTHON_VERSION) found, setting local version and configuring poetry...$(RESET)"; \
		pyenv local $(PYTHON_VERSION); \
		poetry config virtualenvs.create true --local; \
	    poetry config virtualenvs.in-project true --local; \
		poetry env use $(PYTHON_VERSION); \
	else \
		echo "$(RED)Python $(PYTHON_VERSION) is not present. Use pyenv install $(PYTHON_VERSION) to continue."; \
		echo "If you don't know how to proceed, follow the onboarding guide!!!"; \
		exit 1; \
	fi

install-dependencies:
	@echo "$(GREEN)Installing dependencies...$(RESET)"
	@poetry lock
	@poetry install
	@echo "$(GREEN)Dependencies installed successfully.$(RESET)"

## Delete all temporary files
clean:
	@echo "$(YELLOW)Cleaning up caches...$(RESET)"
	@deactivate 2>/dev/null || true
	@rm -rf .ipynb_checkpoints
	@rm -rf **/.ipynb_checkpoints
	@rm -rf .pytest_cache
	@rm -rf **/.pytest_cache
	@rm -rf __pycache__
	@rm -rf **/__pycache__
	@rm -rf build
	@rm -rf dist
	@rm -rf .eggs
	@rm -rf *.egg-info
	@rm -rf $(VENV)
	@rm -f .python-version
	@rm -f poetry.toml
	@echo "$(GREEN)Caches cleaned up successfully.$(RESET)"

build:
	@$(MAKE) -s configure-python-env
	@poetry build
	@pip install dist/*.whl

run:
	@echo "$(YELLOW)Starting monitor...$(RESET)"
	@poetry run monitor

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
help:
	@echo "$$(tput bold)Available commands:$$(tput sgr0)"
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')

.PHONY: install test build clean help compile-aot-files