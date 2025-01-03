POETRY:=poetry
RUN:=${POETRY} run
ARGS:=''
PATHS:=lib/ tests/ bin/


test:
	$(RUN) pytest --cov=lib --cov-report=term-missing --disable-warnings $(ARGS)

mypy:
	$(RUN) mypy --install-types $(PATHS)

mypy-strict:
	$(RUN) mypy --strict --install-types $(PATHS)

flake8:
	$(RUN) flake8 $(PATHS)

pylint:
	$(RUN) pylint $(PATHS)

ruff-lint:
	$(RUN) ruff check  $(PATHS)

typos:
	@typos .

lint: ruff-lint mypy flake8 pylint typos

run:
	$(RUN) python webinar.py

ruff-fmt:
	$(RUN) ruff check --fix $(PATHS)
	$(RUN) ruff format $(PATHS)

isort:
	$(RUN) isort $(PATHS)

typos-fix:
	@typos -w $(PATHS)

fmt: ruff-fmt isort typos-fix

backup-db:
	@sqlite3 db.sqlite3 ".backup db.sqlite3.backup"

db-console:
	@sqlite3 db.sqlite3
