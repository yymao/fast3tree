# fast3tree

[![PyPI version](https://img.shields.io/pypi/v/fast3tree.svg)](https://pypi.python.org/pypi/fast3tree)

This Python package is a wrapper of the excellent, lightning fast `fast3tree` C library,
a BSP tree implementation written by [Peter Behroozi](http://www.peterbehroozi.com/).
The C source code `fast3tree.c` was (shamlessly) taken from Peter's
[Rockstar halo finder](https://bitbucket.org/gfcstanford/rockstar).

This project and Peter's `fast3tree.c` are both licensed under GPLv3.

## Installation

You can install from pypi:

```bash
pip install fast3tree
```

## Example

Here's a minimal example of how you use it in your python code

```python
import numpy as np
from fast3tree import fast3tree

data = np.random.rand(10000, 3)
with fast3tree(data) as tree:
    idx = tree.query_radius([0.5, 0.5, 0.5], 0.2)
    # do whatever you like with idx
```
