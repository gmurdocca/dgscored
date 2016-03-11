SRC_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
EXTRA_PKGS := uwsgi
.SILENT:

help:
	echo "  env		create/activate a development environment using virtualenv"
	echo "  rpm		build a release rpm"
	echo "  deps	update any dependencies if their version was changed"
	echo "  clean	clean this repo of superfluous files"

env:
	which virtualenv >/dev/null || (echo "Please install virtualenv (`pip install virtualenv`)" && exit 1)

	# create the virtualenv if it doesn't already exist
	test -d .env || virtualenv .env >&2
	. .env/bin/activate >&2 && \
	pip install -r requirements.txt >&2 && \
	pip install -e . >&2
	test ! -t 1 || (echo 'To activate the virtualenv, please source the output of this command. Eg: . $$(make env)' && exit 1)
	echo .env/bin/activate

deps:
	. .env/bin/activate && \
	pip install -r requirements.txt --upgrade

clean:
	find . \( -name '*.pyc' -o -name '*.pyo' \) -exec rm -f {} \;
	rm -rf BUILD BUILDROOT RPMS SOURCES SPECS SRPMS
	rm -rf */static/public/*/common.*
	rm -rf dgscored*.rpm

rpm:
	QA_SKIP_BUILD_ROOT=1 rpmbuild --define "srcdir $(SRC_DIR)" --define "_topdir $(SRC_DIR)" -bb support/dgscored.spec
	mv RPMS/x86_64/*.rpm .
	make clean

erd:
	dgscored graph_models dgs -o dgs/static/img/dgs_models.png
