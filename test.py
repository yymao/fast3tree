import numpy as np
from fast3tree import fast3tree, get_distance

points = np.random.rand(1000, 3)

def find_sphere(c, points, r, box_size=-1):
    return np.where(get_distance(c, points, box_size) < r)[0]

def test_fast3tree():
    c = np.array([0.5, 0.5, 0.5])
    r = 0.1
    with fast3tree(points) as tree:
        ind = tree.query_radius(c, r)

    ind.sort()
    ind_true = find_sphere(c, points, r)

    assert len(ind) == len(ind_true)
    assert (ind == ind_true).all()


def test_fast3tree_periodic():
    c = np.array([0, 0, 0])
    r = 0.2
    with fast3tree(points) as tree:
        tree.set_boundaries(0, 1)
        ind = tree.query_radius(c, r, periodic=True)

    ind.sort()
    ind_true = find_sphere(c, points, r, box_size=1.0)

    assert len(ind) == len(ind_true)
    assert (ind == ind_true).all()


def test_fast3tree_index():
    c = np.array([0.5, 0.5, 0.5])
    r = 0.1
    index = np.random.randint(0, 100000, size=len(points))
    with fast3tree(points, index) as tree:
        ind = tree.query_radius(c, r)

    ind.sort()
    ind_true = index[find_sphere(c, points, r)]
    ind_true.sort()

    assert len(ind) == len(ind_true)
    assert (ind == ind_true).all()
