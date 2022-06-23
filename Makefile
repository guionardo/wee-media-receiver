.PHONY: frontend

updatepip:
	pipenv update -d

test:
	python -m unittest

coverage:
	bash .github/scripts/generate_coverage.sh	

requirements:
	pipreqs --force

backend:
	docker run --rm -p 8080:8080 -e PORT=8080 -v ${PWD}/tests/backend_responses:/app/custom_responses guionardo/http_helloworld:latest

frontend:
	$(shell cd frontend && yarn dist)