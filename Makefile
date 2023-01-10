.PHONY: setup
setup:
	@ echo "Setting up package..."
	@ poetry install

.PHONY: clean
clean:
	@ rm -rf __pycache__

.PHONY: format
format:
	@ echo "formatting..."
	@ poetry run isort src
	@ poetry run black src

.PHONY: lint
lint:
	@ echo "linting..."
	@ poetry run flake8 src

.PHONY: test
test:
	@ echo "testing..."
	@ poetry run pytest -vv --failed-first --new-first

.PHONY: autoci
autoci: format lint test