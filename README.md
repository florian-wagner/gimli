<!---
Readme for Github repository only. (Get's selected before *.rst file)
-->

![GIMLi](https://raw.githubusercontent.com/gimli-org/gimli/master/doc/_themes/gimli/static/gimli.png)

# GIMLi - Geophysical Inversion and Modelling Library

[![Build Status](https://travis-ci.org/gimli-org/gimli.svg)](https://travis-ci.org/gimli-org/gimli)
[![Code Health](https://landscape.io/github/gimli-org/gimli/master/landscape.svg)](https://landscape.io/github/gimli-org/gimli/master)


GIMLi is an open-source multi-method library for solving inverse
and forward modelling tasks.

##### What GIMLi is good for?:

- creating inversion applications (C++) and scripts (Python) for existing modules
- add your own forward calculations and build a robust inversion quickly
- combining different geophysical methods in various ways
- doing modelling of different PDEs

##### What GIMLi is **NOT** good for?:

- for people that expect a ready-made GUI for interpreting their data

##### Build from source
```bash
git clone https://github.com/gimli-org/gimli.git
mkdir gimli_build && cd gimli_build
cmake ../gimli
make pygimli
```

##### Usage
```python
import pygimli as pg
print(pg.__version__)
```

<!---
Link to www.gimli.org at some point
-->
