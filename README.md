# fast3tree
[![PyPI version](https://img.shields.io/pypi/v/fast3tree.svg)](https://pypi.python.org/pypi/fast3tree)


This project and Peter's `fast3tree.c` are both licensed under GPLv3.

## Installation

You can install from pypi:

    pip install fast3tree

or if you need the latest version:

    https://bitbucket.org/yymao/fast3tree/get/master.zip


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