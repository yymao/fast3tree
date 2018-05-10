import numpy as np
from .core import fast3tree

__all__ = ['find_friends_of_friends']

def find_friends_of_friends(points, linking_length, periodic_box_size=None):
    group_ids = np.repeat(-1, len(points))
    with fast3tree(points) as tree:
        if periodic_box_size:
            tree.set_boundaries(0, periodic_box_size)
        for i, point in enumerate(points):
            idx = tree.query_radius(point, linking_length, bool(periodic_box_size))
            group_ids_this = np.unique(group_ids[idx])
            group_ids_this = group_ids_this[group_ids_this != -1]
            if len(group_ids_this) == 1:
                group_ids[idx] = group_ids_this[0]
            else:
                group_ids[idx] = i
                if len(group_ids_this):
                    group_ids[np.in1d(group_ids, group_ids_this)] = i

    return np.unique(group_ids, return_inverse=True)[1]
