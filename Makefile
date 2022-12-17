RUN:=poetry


test:
	$(RUN) run pytest --ff --lf

mypy:
	$(RUN) run mypy .

flake8:
	$(RUN) run flake8 --ignore=E501

pylint:
	$(RUN) run mypy *.py

lint: mypy flake8 pylint

run:
	$(RUN) run python webinar.py
