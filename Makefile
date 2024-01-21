POETRY:=poetry
RUN:=${POETRY} run
ARGS:=''


test:
	$(RUN) pytest --cov=lib --cov-report=term-missing --disable-warnings $(ARGS)

mypy:
	$(RUN) mypy --install-types lib/ tests/ bin/

mypy-strict:
	$(RUN) mypy --strict --install-types lib/ tests/ bin/

flake8:
	$(RUN) flake8 lib/ tests/ bin/

pylint:
	$(RUN) pylint lib/ tests/ bin/

ruff-lint:
	$(RUN) ruff check lib/ tests/ bin/

typos:
	@typos .

lint: ruff-lint mypy flake8 pylint typos

run:
	$(RUN) python webinar.py

dev:
	$(RUN) gunicorn server:acreate_app --bind localhost:8080 --reload  --worker-class aiohttp.GunicornWebWorker


ruff-fmt:
	$(RUN) ruff format lib/ tests/ bin/

black:
	$(RUN) black lib/ tests/ bin/

isort:
	$(RUN) isort lib/ tests/ bin/

fmt: ruff-fmt isort black

backup-db:
	@sqlite3 db.sqlite3 ".backup db.sqlite3.backup"
