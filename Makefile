build:
	docker build --tag aiodisque:latest .

documentation:
	pip install -r docs/requirements.txt
	cd docs && make html
