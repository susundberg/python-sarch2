
check:
	pylint3 --errors-only --output-format=parseable sarch2
	
check_run:
	ls entr sarch2/*.py | entr -rd make check

tests_run:
	PYTHONPATH=$(shell pwd) python3 tests/test_main.py --failfast
	PYTHONPATH=$(shell pwd) python3 tests/test_import.py --failfast
