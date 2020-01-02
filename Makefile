
all: run_check run_test autofix_run run_check_full
	
run_check:
	# stop the build if there are Python syntax errors or undefined names
	python3 -m flake8 sarch2 --count --select=E9,F63,F7,F82 --show-source --statistics
	
run_check_full: run_check
	# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
	python3 -m flake8 sarch2 --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

autofix_run:
	autopep8 --in-place --aggressive --aggressive sarch2/*.py tests/*.py


run_test:
	PYTHONPATH=$(shell pwd) python3 -m pytest ./tests --exitfirst
