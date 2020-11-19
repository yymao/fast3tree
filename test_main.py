import numpy as np
from fast3tree import fast3tree, get_distance, find_friends_of_friends

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


def prepare_fof(n_points=50, n_groups=8, n_dim=2, scale=0.01, seed=0):
    # pylint: disable=no-member
    n_total = n_points * n_groups
    points = np.vstack(
        (
            np.random.RandomState(seed + i).randn(n_points, n_dim) * scale
            + np.random.RandomState(seed + i).rand(n_dim)
            for i in range(n_groups)
        )
    )
    answer = np.hstack((np.repeat(i, n_points) for i in range(n_groups)))
    shuffle = np.random.RandomState(seed).choice(n_total, n_total, replace=False)
    points = points[shuffle]
    answer = answer[shuffle]
    return points, answer


def test_fof_d2():
    scale = 0.01
    n_groups = 8
    points, answer = prepare_fof(n_groups=n_groups, n_dim=2, scale=scale, seed=100)
    fof = find_friends_of_friends(points, scale * 2)
    for i in range(n_groups):
        assert len(np.unique(answer[fof == i])) == 1
        assert len(np.unique(fof[answer == i])) == 1


def test_fof_d3():
    scale = 0.01
    n_groups = 8
    points, answer = prepare_fof(n_groups=n_groups, n_dim=3, scale=scale, seed=200)
    fof = find_friends_of_friends(points, scale * 3)
    for i in range(n_groups):
        assert len(np.unique(answer[fof == i])) == 1
        assert len(np.unique(fof[answer == i])) == 1
