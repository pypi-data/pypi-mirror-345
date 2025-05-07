# kvlang

[![GitHub version](https://badge.fury.io/gh/keyweeusr%2Fkvlang.svg)
](https://badge.fury.io/gh/keyweeusr%2Fkvlang)
[![PyPI version](https://img.shields.io/pypi/v/kvlang.svg)
](https://pypi.org/project/kvlang/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/kvlang.svg)
](https://pypi.org/project/kvlang/)
[![Latest release deps](https://img.shields.io/librariesio/release/pypi/kvlang.svg)
](https://libraries.io/pypi/kvlang)
[![GitHub repo deps](https://img.shields.io/librariesio/github/keyweeusr/kvlang.svg)
](https://libraries.io/pypi/kvlang)

[![Downloads total](https://pepy.tech/badge/kvlang)
](https://pepy.tech/project/kvlang)
[![Downloads month](https://pepy.tech/badge/kvlang/month)
](https://pepy.tech/project/kvlang)
[![Downloads week](https://pepy.tech/badge/kvlang/week)
](https://pepy.tech/project/kvlang)
[![All Releases](https://img.shields.io/github/downloads/keyweeusr/kvlang/total.svg)
](https://github.com/KeyWeeUsr/kvlang/releases)
[![Code bytes](https://img.shields.io/github/languages/code-size/keyweeusr/kvlang.svg)
](https://github.com/KeyWeeUsr/kvlang)
[![Repo size](https://img.shields.io/github/repo-size/keyweeusr/kvlang.svg)
](https://github.com/KeyWeeUsr/kvlang)

Grammar and parser for [Kv][kv] ([wiki][wiki]) as a more reliable approach for
reading the `.kv` files.

Install from PyPI:

```
pip install kvlang
```

or from the repo:

```
git clone https://github.com/KeyWeeUsr/kvlang
pip install -e .
# or
pip install git+https://github.com/KeyWeeUsr/kvlang.git
# or
pip install https://github.com/KeyWeeUsr/kvlang/zipball/master
# or
pip install https://github.com/KeyWeeUsr/kvlang/zipball/1.0.1
```

then

```python
from kvlang import parse

print(parse("#:kivy 2.3.1"))
# Tree(Token('RULE', 'start'), [Tree(Token('RULE', 'special'), [...])])

print(parse("#:kivy 2.3.1").pretty())
# start
#   special
#     special_directive
#       kivy_version
#         version
#           2
#           3
#           1
```

[kv]: https://kivy.org/doc/stable/guide/lang.html
[wiki]: https://en.wikipedia.org/wiki/Kivy_(framework)#Kv_language
