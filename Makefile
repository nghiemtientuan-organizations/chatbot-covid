.DEFAULT_GOAL := help

.PHONY: requirements

requirements: ## Install requirements
	pip install -r requirements/base.txt
	pip install -r requirements/actions.txt
	pip install rasa-x==0.40.0 --extra-index-url https://pypi.rasa.com/simple
