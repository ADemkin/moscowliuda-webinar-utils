POETRY:=poetry
RUN:=${POETRY} run
ARGS:=''


test:
	$(RUN) pytest --disable-warnings $(ARGS)

mypy:
	$(RUN) mypy .

flake8:
	$(RUN) flake8 *.py

pylint:
	$(RUN) pylint *.py

lint: mypy flake8 pylint

run:
	$(RUN) python webinar.py

dev:
	$(RUN) gunicorn server:acreate_app --bind localhost:8080 --reload  --worker-class aiohttp.GunicornWebWorker


black:
	$(RUN) black *.py

isort:
	$(RUN) isort *.py

fmt: isort black
