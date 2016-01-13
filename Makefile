SHELL := $(shell which bash)
PROJECT := phonelocator
ACTIVATE_VENV = source activate ${PROJECT}
TEST_MARKS := "slow" 
CONDA_REQS := "conda-requirements.txt"
PIP_REQS := "pip-requirements.txt"
TEST_REQS := "test-requirements"

setup:
	-conda create -n ${PROJECT} ipython
	${ACTIVATE_VENV} && \
	  conda install --file ${CONDA_REQS} && \
	  pip install -r ${PIP_REQS}

test-setup: setup
	${ACTIVATE_VENV} && pip install -r ${TEST_REQS}

test: clean validate
	${ACTIVATE_VENV} && \
	export PYTHONPATH=./$(PROJECT):$$PYTHONPATH && \
	py.test -m 'not $(TEST_MARKS)' --cov $(PROJECT)/ --cov-report=term --cov-report=html --junitxml=nosetests.xml -s -v tests/test_*.py

test-full: clean validate
	${ACTIVATE_VENV} && \
	export PYTHONPATH=./$(PROJECT):$$PYTHONPATH && \
	py.test --cov $(PROJECT)/ --cov-report=term --cov-report=html --junitxml=nosetests.xml -s -v tests/test_*.py

clean:
	find ./tests/ -name '*.py[co]' -exec rm {} \;
	rm -rf build dist $(PROJECT).egg-info
	rm -f nosetests.xml
	rm -rf htmlcov/

validate:
	${ACTIVATE_VENV} && flake8 $(PROJECT)/ tests/

all:
	$(error please pick a target)

.PHONY: clean validate

