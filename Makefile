POETRY:=poetry
RUN:=${POETRY} run
ARGS:='--live'
PATHS:=lib/ tests/ bin/


test:
	$(RUN) pytest --live --cov=lib --cov-report=term-missing $(ARGS)

mypy:
	$(RUN) mypy $(PATHS)

mypy-strict:
	$(RUN) mypy --strict $(PATHS)

ruff-lint:
	$(RUN) ruff check  $(PATHS)

typos:
	@typos .

lint: ruff-lint mypy typos

run:
	$(RUN) python webinar.py

ruff-fmt:
	$(RUN) ruff check --fix $(PATHS)
	$(RUN) ruff format $(PATHS)

typos-fix:
	@typos -w $(PATHS)

fmt: ruff-fmt typos-fix

backup-db:
	@sqlite3 db.sqlite3 ".backup db.sqlite3.backup"

db-console:
	@sqlite3 db.sqlite3
