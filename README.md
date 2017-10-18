# fast3tree

This is a Python wrapper of [Peter Behroozi](http://www.peterbehroozi.com/)'s `fast3tree` code, which was
(shamlessly) taken from his [Rockstar halo finder](https://bitbucket.org/gfcstanford/rockstar).

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