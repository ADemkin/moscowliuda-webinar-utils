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
	$(RUN) ruff check $(PATHS)

typos:
	@typos .

lint: ruff-lint mypy flake8 pylint typos

run:
	$(RUN) python webinar.py

dev:
	$(RUN) gunicorn server:acreate_app --bind localhost:8080 --reload  --worker-class aiohttp.GunicornWebWorker


ruff-fmt:
	$(RUN) ruff format $(PATHS)

black:
	$(RUN) black $(PATHS)

isort:
	$(RUN) isort $(PATHS)

typos-fix:
	@typos -w $(PATHS)

fmt: ruff-fmt isort black typos-fix

backup-db:
	@sqlite3 db.sqlite3 ".backup db.sqlite3.backup"

db-console:
	@sqlite3 db.sqlite3
