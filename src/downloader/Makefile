.PHONY: help docs
.DEFAULT_GOAL := help

VIRTUAL_HOME := ../.venv
PYTHON_PATH :=

UNAME_S := $(shell uname -s)
ifeq ($(OS),Windows_NT)
	ifeq ($(VIRTUAL_ENV), )
		PYTHON_PATH += $(VIRTUAL_HOME)/bin/
	endif
else
	ifeq ($(UNAME_S),Darwin)
		ifeq ($(VIRTUAL_ENV), )
			PYTHON_PATH += $(VIRTUAL_HOME)/bin/
		endif
	endif

	ifeq ($(UNAME_S),Linux)
		ifeq ($(VIRTUAL_ENV), )
			PYTHON_PATH += $(VIRTUAL_HOME)/bin/
		endif
	endif
endif

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## Install prod requirements
	$(PYTHON_PATH)pip install -r requirements.txt


reinstall: ## Reinstall prod requirements
	$(PYTHON_PATH)pip install --upgrade --force-reinstall -r requirements.txt

install_dev: ## Install dev requirements
	$(PYTHON_PATH)pip install -i https://pypi.python.org/simple pip-tools
	$(PYTHON_PATH)pip install -r requirements.dev.txt


reinstall_dev: ## Reinstall dev requirements
	$(PYTHON_PATH)pip install --upgrade --force-reinstall -r requirements.dev.txt

lock_prod:
	$(PYTHON_PATH)pip-compile --no-header --no-emit-index-url --verbose --output-file requirements.txt requirements.in

lock_dev:
	$(PYTHON_PATH)pip-compile --no-header --no-emit-index-url --verbose --output-file requirements.dev.txt requirements.dev.in

lock: lock_dev lock_prod ## Compile all requirements files

upgrade: ## Upgrade requirements files
	$(PYTHON_PATH)pip-compile --no-header --no-emit-index-url --verbose --upgrade --output-file requirements.txt requirements.in
	$(PYTHON_PATH)pip-compile --no-header --no-emit-index-url --verbose --upgrade --output-file requirements.dev.txt requirements.dev.in

run_pytest:
	$(PYTHON_PATH)python -m pytest --cov

run_updater: ## Run morningstar updater
	$(PYTHON_PATH)python tasks/updater.py

mypy: ## Test types
	python -m mypy --explicit-package-bases .