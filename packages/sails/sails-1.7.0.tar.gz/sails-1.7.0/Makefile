# vim: set noexpandtab ts=4 sw=4:

# There must be a nicer way to do this
PYTHONARCH=$(shell python utils/pythonarch)
PYTHONARCH3=$(shell python utils/pythonarch)

BINS=$(shell python setup.py --list-scripts)

DEVELVERSION ?= 0.DEVEL.$(shell date +%Y%m%d%H%M)
RELEASEVERSION ?= $(DEVELVERSION)

all: all-python

doc: doc-html

doc-html: all
	python setup.py build_sphinx

clean:
	python setup.py clean
	# Stupid python setuptools don't even clean the build directory
	rm -fr build
	rm -fr doc/build
	rm -fr sails.egg-info

test:
	python -m pytest sails
	coverage html

all-python:
	python setup.py build

all-clean: install-clean
	python setup.py build

install-clean: clean
	python setup.py install

install-python: all-python
	python setup.py install --prefix=$(DESTDIR)/usr

spell:
	codespell -s --ignore-words=ignore_words.txt `find . -type f -name \*.py`

sphinx:
	sphinx-build -M html doc/source doc/build

# Make single reqs file for readthedocs
# https://github.com/readthedocs/readthedocs.org/issues/1112
reqs:
	cat requirements.txt requirements_dev.txt > requirements_rtd.txt

.PHONY: clean doc doc-html all all-python test testv pythonarch install-python codespell
