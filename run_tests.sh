#!/bin/sh

if ! nosetests --with-coverage --cover-package=stacktraces; then
    exit 1
fi

if ! flake8 .; then
    exit 1
fi
