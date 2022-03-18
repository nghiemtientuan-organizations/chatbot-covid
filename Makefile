.DEFAULT_GOAL := help

.PHONY: requirements

requirements: ## Install requirements
	pip install -r requirements/base.txt
	pip install -r requirements/actions.txt
	pip install rasa-x==0.39.3 --extra-index-url https://pypi.rasa.com/simple
