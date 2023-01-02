RUN:=poetry
ARGS:=--ff --lf


test:
	$(RUN) run pytest --disable-warnings $(ARGS)

mypy:
	$(RUN) run mypy .

flake8:
	$(RUN) run flake8 --ignore=E501

pylint:
	$(RUN) run mypy *.py

lint: mypy flake8 pylint

run:
	$(RUN) run python webinar.py
