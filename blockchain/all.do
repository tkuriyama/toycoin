
# echo "> Running pytest" >&2
# py.test >&2

echo "\n> PyTest coverage" >&2
pytest --cov-config=.coveragerc --cov=toycoin tests/ >&2


echo "\n> Running pyflakes" >&2
pyflakes toycoin/ >&2

echo "\n> Running mypy" >&2
mypy toycoin >&2

