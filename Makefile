POETRY:=poetry
RUN:=${POETRY} run
ARGS:=''


test:
	$(RUN) pytest --cov=lib --cov-report=term-missing --disable-warnings $(ARGS)

mypy:
	$(RUN) mypy .

flake8:
	$(RUN) flake8 lib/ tests/ bin/

pylint:
	$(RUN) pylint lib/ tests/ bin/

lint: mypy flake8 pylint

run:
	$(RUN) python webinar.py

dev:
	$(RUN) gunicorn server:acreate_app --bind localhost:8080 --reload  --worker-class aiohttp.GunicornWebWorker


black:
	$(RUN) black lib/ tests/ bin/

isort:
	$(RUN) isort lib/ tests/ bin/

fmt: isort black
