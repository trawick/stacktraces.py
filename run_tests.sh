if ! nosetests; then
    exit 1
fi

if ! flake8 .; then
    exit 1
fi

