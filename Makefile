.PHONY: format lint

lint:
	flake8 --exclude=venv/,.pyenv/,.direnv/ --ignore=E203,E501,W503
	isort --check-only --skip-glob .pyenv --skip-glob .direnv --profile black .
	black --check --exclude '/(\.direnv|\.pyenv)/' .

format:
	black --exclude '/(\.direnv|\.pyenv|\.direnv)/' .
	isort --skip-glob .pyenv --skip-glob .direnv --profile black .
