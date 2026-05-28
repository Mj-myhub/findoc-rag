.PHONY: install explore test lint clean

install:  ## Install dependencies and the package
	pip install -r requirements.txt
	pip install -e .

explore:  ## Download FinanceBench and print its structure
	python -m findoc_rag.data.load_financebench

test:  ## Run the test suite
	pytest -q

lint:  ## Check code style
	ruff check .

clean:  ## Remove Python cache files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
