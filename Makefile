isort:
	isort pingeon tests

black:
	black pingeon tests

fmt: isort black

test:
	pytest --cov --black --isort --mypy tests
