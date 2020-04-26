.PHONY: test unit_test it_test

export PYTHONPATH=$PYTHONPATH:$(PWD)

venv: venv/bin/activate

venv/bin/activate: requirements.txt
	test -d venv || python3 -m venv venv
	$(PWD)/venv/bin/pip install -Ur requirements.txt
	touch venv/bin/activate

it_test: venv
	venv/bin/py.test -vvvv -r sxX tests/integration

unit_test: venv
	venv/bin/py.test -vvvv -r sxX tests/unit

test: venv unit_test it_test

fmt: venv
	black src app.py tests
