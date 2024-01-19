POETRY:=poetry
RUN:=${POETRY} run
ARGS:=''


test:
	$(RUN) pytest --cov=lib --disable-warnings $(ARGS)
	$(RUN) coverage report -m

mypy:
	$(RUN) mypy .

flake8:
	$(RUN) flake8 lib/*.py tests/*.py

pylint:
	$(RUN) pylint lib/*.py tests/*.py

lint: mypy flake8 pylint

run:
	$(RUN) python webinar.py

dev:
	$(RUN) gunicorn server:acreate_app --bind localhost:8080 --reload  --worker-class aiohttp.GunicornWebWorker


black:
	$(RUN) black lib/*.py tests/*.py

isort:
	$(RUN) isort lib/*.py tests/*.py

fmt: isort black
