cpgame.mpy: cpgame.py
	python3 -m mpy_cross cpgame.py

src := cpgame.py setup.py examples/

setup:
	python3 -m pip install -Ur requirements-dev.txt

venv:
	python3 -m venv .venv
	source .venv/bin/activate && make setup
	@echo 'run `source .venv/bin/activate` to use virtualenv'

black:
	isort --apply --recursive $(src)
	black $(src)

lint:
	mypy $(src)
	isort --diff --recursive $(src)
	black --check $(src)

release: lint clean
	python3 setup.py sdist
	python3 -m twine upload dist/*

clean:
	rm -rf build dist README MANIFEST cpgame.egg-info cpgame.mpy

distclean: clean
	rm -rf venv .venv
