#!/bin/sh

MIN_COVERAGE=76

if ! diff collect.py stacktraces/native/collect.py >/dev/null 2>&1; then
    echo "collect.py must be the same in both places" 1>&2
    exit 1
fi

if ! nosetests --with-coverage --cover-package=stacktraces --cover-min-percentage=${MIN_COVERAGE}; then
    exit 1
fi

if ! flake8 .; then
    exit 1
fi
