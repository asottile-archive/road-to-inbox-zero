venv: requirements.txt
	bin/venv-update venv= -ppython3.5 venv install= $(patsubst %,-r %,$^)

.PHONY: test
test: venv
	venv/bin/flake8 *.py
