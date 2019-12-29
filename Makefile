
check:
	pylint3 --errors-only --output-format=parseable sarch2
	
check_run:
	ls entr sarch2/*.py | entr -rd make check


