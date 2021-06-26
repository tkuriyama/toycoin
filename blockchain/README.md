# toycoin

[![Build Status](https://travis-ci.com/tkuriyama/toycoin.svg?branch=master)](https://travis-ci.com/tkuriyama/toycoin)

Toy blockchain implemenetaion in Python.

**Purely for learning purposes -- do not assume it's secure or useful in real-world contexts.**

## Install

Install locally with pip from the project root directory: `

```python
pip install -r requirements.txt
pip install .
```

Not tested with Python versions < 3.9.1


## Build

There is no build per se, since this is a pure Python project, but the all.do script at the root collects a number of commands that are run to validate the code (`py.test`, `pyflakes`, `mypy` etc).

The script can be run conveniently with `refo all` on the command line if [redo](https://redo.readthedocs.io/en/latest/) is installed, though the script contents can also be run individually / independently (e.g. as `sh all.do`).

## Notes

See the series of write-ups on the `toycoin` project on GH Pages: [first post](https://tkuriyama.github.io/crypto/2021/06/18/toycoin-part-1.html).




