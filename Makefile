.PHONY: install test docs clean docker-up docker-down

install:
	pip install -r requirements.txt

test:
	pytest

test-coverage:
	pytest --cov=src/contacts_api --cov-report=html --cov-report=term-missing

docs:
	cd docs && sphinx-build -b html . _build/html

docs-clean:
	cd docs && rm -rf _build

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

run-local:
	uvicorn src.contacts_api.main:app --reload --host 0.0.0.0 --port 8000