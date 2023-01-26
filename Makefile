.PHONY: all
all: format lint cov

.PHONY: format
format:
	$(info Format Python code)
	black --exclude '/\.venv/' .
	isort --skip-glob .venv --profile black .

.PHONY: lint
lint:
	$(info Lint Python code)
	flake8 --exclude=.venv/ --ignore=E203,E501,W503
	isort --check-only --skip-glob venv --profile black .
	black --check --exclude '/\.venv/' .

.PHONY: test
test:
	python -Wall manage.py test

.PHONY: cov
cov:
	coverage run --source='.' manage.py test
	coverage report -m

.PHONY: pginit
pginit:
	$(info Initialising PostgreSQL database files)
	PGDATA=postgres-data/ pg_ctl init
	PGDATA=postgres-data/ pg_ctl start
	createuser oscarator
	psql -U postgres -c "ALTER USER oscarator CREATEDB;"
	psql -U oscarator -d postgres -c "CREATE DATABASE oscarator;"

.PHONY: pgstart
pgstart:
	$(info Start PostgreSQL)
	PGDATA=postgres-data/ pg_ctl start

.PHONY: pgstop
pgstop:
	$(info Stop PostgreSQL)
	PGDATA=postgres-data/ pg_ctl stop

.PHONY: pipupgrade
pipupgrade:
	$(info Running pip-compile -U)
	pip install -U pip-tools
	pip install -U pip
	pip-compile -U --resolver=backtracking
