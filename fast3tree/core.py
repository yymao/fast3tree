import warnings
import numpy as np
import numpy.ctypeslib as C
from .make import make_lib

try:
    range = xrange
except NameError:
    pass

__all__ = ["fast3tree", "get_distance"]


_ptr_dtype = np.uint64
_ptr_ctype = C.ctypes.c_uint64
_results_dtype = np.dtype(
    [
        ("num_points", np.int64),
        ("num_allocated_points", np.int64),
        ("points", np.uint64),
    ],
    align=True,
)


class _fast3tree_lib:
    def __init__(self, dim, use_double):
        self.dim = int(dim)
        self.use_double = bool(use_double)

        if self.use_double:
            float_dtype = np.float64
            float_ctype = C.ctypes.c_double
        else:
            float_dtype = np.float32
            float_ctype = C.ctypes.c_float

        mytype = np.dtype(
            [("idx", np.int64), ("pos", float_dtype, self.dim)], align=True
        )
        mytype_ctype = C.ndpointer(mytype, ndim=1, flags="C")
        center_ctype = C.ndpointer(dtype=float_dtype, ndim=1, shape=(dim,), flags="C")
        box_ctype = C.ndpointer(dtype=float_dtype, ndim=2, shape=(2, dim), flags="C")
        tree_ptr_ptr = C.ndpointer(dtype=_ptr_dtype, ndim=1, shape=(1,), flags="C")

        c_lib = C.ctypes.cdll[make_lib(self.dim, self.use_double)]

        c_lib.fast3tree_init.restype = _ptr_ctype
        c_lib.fast3tree_init.argtypes = [C.ctypes.c_int64, mytype_ctype]

        c_lib.fast3tree_rebuild.restype = None
        c_lib.fast3tree_rebuild.argtypes = [_ptr_ctype, C.ctypes.c_int64, mytype_ctype]

        c_lib.fast3tree_maxmin_rebuild.restype = None
        c_lib.fast3tree_maxmin_rebuild.argtypes = [_ptr_ctype]

        c_lib.fast3tree_free.restype = None
        c_lib.fast3tree_free.argtypes = [tree_ptr_ptr]

        c_lib.fast3tree_results_init.restype = _ptr_ctype
        c_lib.fast3tree_results_init.argtypes = None

        c_lib.fast3tree_find_sphere.restype = None
        c_lib.fast3tree_find_sphere.argtypes = [
            _ptr_ctype,
            _ptr_ctype,
            center_ctype,
            float_ctype,
        ]

        c_lib.fast3tree_find_sphere_periodic.restype = C.ctypes.c_int
        c_lib.fast3tree_find_sphere_periodic.argtypes = [
            _ptr_ctype,
            _ptr_ctype,
            center_ctype,
            float_ctype,
        ]

        c_lib.fast3tree_find_inside_of_box.restype = None
        c_lib.fast3tree_find_inside_of_box.argtypes = [
            _ptr_ctype,
            _ptr_ctype,
            box_ctype,
        ]

        c_lib.fast3tree_find_outside_of_box.restype = None
        c_lib.fast3tree_find_outside_of_box.argtypes = [
            _ptr_ctype,
            _ptr_ctype,
            box_ctype,
        ]

        c_lib.fast3tree_results_clear.restype = None
        c_lib.fast3tree_results_clear.argtypes = [_ptr_ctype]

        c_lib.fast3tree_results_free.restype = None
        c_lib.fast3tree_results_free.argtypes = [_ptr_ctype]

        c_lib.fast3tree_set_minmax.restype = None
        c_lib.fast3tree_set_minmax.argtypes = [_ptr_ctype, float_ctype, float_ctype]

        c_lib.fast3tree_find_next_closest_distance.restype = float_ctype
        c_lib.fast3tree_find_next_closest_distance.argtypes = [
            _ptr_ctype,
            _ptr_ctype,
            center_ctype,
        ]

        self.run = c_lib
        self.float_dtype = float_dtype
        self.input_dtype = mytype


if hasattr(C.ctypes.pythonapi, "PyMemoryView_FromMemory"):

    def _read_from_address(ptr, dtype, count):
        buf_from_mem = C.ctypes.pythonapi.PyMemoryView_FromMemory
        buf_from_mem.restype = C.ctypes.py_object
        buf_from_mem.argtypes = (_ptr_ctype, C.ctypes.c_int, C.ctypes.c_int)
        buffer = buf_from_mem(ptr, np.dtype(dtype).itemsize * count, 0x100)
        return np.frombuffer(buffer, dtype, count=count)


else:
    # Used in Python2 only
    def _read_from_address(ptr, dtype, count):
        return np.frombuffer(
            np.core.multiarray.int_asbuffer(
                long(ptr),  # pylint: disable=undefined-variable # noqa: F821
                np.dtype(dtype).itemsize
                * count,
            ),
            dtype,
            count=count,
        )


def get_distance(center, pos, box_size=None):
    pos = np.asarray(pos)
    pos_dtype = pos.dtype.type
    d = pos - np.asarray(center, pos_dtype)
    if box_size and box_size > 0:
        box_size = pos_dtype(box_size)
        half_box_size = pos_dtype(box_size * 0.5)
        d[d > half_box_size] -= box_size
        d[d < -half_box_size] += box_size
    d *= d
    d = d.sum(axis=1)
    np.sqrt(d, out=d)
    return d


class fast3tree:
    def __init__(self, data=None, data_indices=None, force_double=False, raw_data=None):
        """
        Initialize a fast3tree from a list of points.
        Please call fast3tree with the `with` statement to ensure memory safe.

            with fast3tree(data) as tree:

        Parameters
        ----------
        data : array_like
            data to build the tree. must be a 2-d array.
        data_indices : array_like

        Member functions
        ----------------
        rebuild_boundaries()
        set_boundaries(Min, Max)
        query_nearest_distance(center)
        query_radius(center, r)
        query_box(corner1, corner2)
        """
        self._lib = None
        self._force_double = bool(force_double)
        if raw_data is not None:
            if data is not None or data_indices is not None:
                warnings.warn(
                    "`data` and `data_indices` are ignored when `raw_data` is specified"
                )
            self._load_raw_data(raw_data)
        elif data is not None:
            self._load_data(data, data_indices)
        else:
            raise ValueError("Must specified `data` or `raw_data`")
        self._tree_ptr = self._lib.run.fast3tree_init(
            np.int64(self.data.shape[0]), self.data
        )
        self._res_ptr = self._lib.run.fast3tree_results_init()
        self._check_opened_by_with = self._check_opened_by_with_warn

    def __enter__(self):
        self._check_opened_by_with = self._check_opened_by_with_pass
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.free()

    def _load_raw_data(self, raw_data):
        if self._lib is None:
            dt = raw_data.dtype[1]
            self._lib = _fast3tree_lib(dt.shape[1], (dt.type == np.float64))
        if raw_data.dtype != self._lib.input_dtype:
            raise ValueError("raw data not in correct format.")
        self.data = raw_data

    def _load_data(self, data, data_indices=None):
        data = np.asarray(data)
        s = data.shape
        if len(s) != 2:
            raise ValueError("data must be a 2-d array.")
        if self._lib is None:
            self._lib = _fast3tree_lib(
                s[1], self._force_double or (data.dtype.type != np.float32)
            )
        elif s[1] != self._lib.dim:
            raise ValueError("data must have the last dim = %d." % self._lib.dim)

        self.data = np.empty(s[0], self._lib.input_dtype)
        self.data["idx"][:] = range(s[0]) if data_indices is None else data_indices
        self.data["pos"][:] = data

    @staticmethod
    def _check_opened_by_with_warn():
        warnings.warn("Please use `with` statement to open a fast3tree object.")

    @staticmethod
    def _check_opened_by_with_pass():
        pass

    def _read_results(self, output):
        o = output[0].lower()
        res = _read_from_address(self._res_ptr, _results_dtype, 1)[0]
        if o == "c":
            return res["num_points"]
        if res[0]:
            points = _read_from_address(res["points"], _ptr_ctype, res[0]).copy()
            points -= self.data.ctypes.data
            points //= self._lib.input_dtype.itemsize
        else:
            points = []
        if o == "i":
            return self.data["idx"][points]
        elif o == "p":
            return self.data["pos"][points]
        elif o == "b":
            return self.data["idx"][points], self.data["pos"][points]
        elif o == "r":
            return self.data[points]
        else:
            return self.data["idx"][points]

    def rebuild(self):
        """
        Rebuild a fast3tree.
        """
        self._check_opened_by_with()
        self._lib.run.fast3tree_rebuild(
            self._tree_ptr, np.int64(self.data.shape[0]), self.data
        )

    def rebuild_boundaries(self):
        """ Rebuilds the tree boundaries, but keeps structure the same. """
        self._check_opened_by_with()
        self._lib.run.fast3tree_maxmin_rebuild(self._tree_ptr)

    def set_boundaries(self, Min, Max):
        """
        Set the tree boundaries (for periodic boundary condition).

        Parameters
        ----------
        Min : float
        Max : float
        """
        self._check_opened_by_with()
        self._lib.run.fast3tree_set_minmax(
            self._tree_ptr, self._lib.float_dtype(Min), self._lib.float_dtype(Max)
        )

    def free(self):
        """ Frees the memory of the tree and the results. """
        self._check_opened_by_with()
        self._lib.run.fast3tree_results_free(self._res_ptr)
        self._lib.run.fast3tree_free(np.asarray([self._tree_ptr], dtype=_ptr_dtype))
        self._lib = None
        self.data = None
        self._tree_ptr = None
        self._res_ptr = None

    def clear_results(self):
        """ Frees the memory of the results. """
        self._check_opened_by_with()
        self._lib.run.fast3tree_results_clear(self._res_ptr)

    def query_nearest_distance(self, center):
        """
        Find the distance to the nearest point.

        Parameters
        ----------
        center : array_like

        Returns
        -------
        distance : float
        """
        self._check_opened_by_with()
        center_arr = np.asarray(center, dtype=self._lib.float_dtype)
        d = self._lib.run.fast3tree_find_next_closest_distance(
            self._tree_ptr, self._res_ptr, center_arr
        )
        return self._lib.float_dtype(d)

    def query_radius(self, center, r, periodic=False, output="index"):
        """
        Find all points within a sphere centered at center with radius r.

        Parameters
        ----------
        center : array_like
            center of the sphere
        r : float
            radius of the sphere
        periodic : bool, optional
            whether to use periodic boundary condition or not
        output : str, optional
            specify what to return

        Returns
        -------
        Could be one of the followings.
        count : int         [if output=='count']
        index : array_like  [if output=='index']
        pos : array_like    [if output=='pos']
        index, pos : tuple  [if output=='both']
        data : array_like   [if output=='raw']
        """
        self._check_opened_by_with()
        center_arr = np.array(center, dtype=self._lib.float_dtype)
        if periodic:
            _ = self._lib.run.fast3tree_find_sphere_periodic(
                self._tree_ptr, self._res_ptr, center_arr, self._lib.float_dtype(r)
            )
        else:
            self._lib.run.fast3tree_find_sphere(
                self._tree_ptr, self._res_ptr, center_arr, self._lib.float_dtype(r)
            )
        return self._read_results(output)

    def query_box(self, corner1, corner2, inside=True, output="index"):
        """
        Find all points within a box.

        Parameters
        ----------
        corner1 : array_like
            position of the lower left corner of the box.
        corner2 : array_like
            position of the upper right corner of the box.
        inside : bool, optional
            whether to find the particles inside or outside the box
        output : str, optional
            specify what to return

        Returns
        -------
        Could be one of the followings.
        count : int         [if output=='count']
        index : array_like  [if output=='index']
        pos : array_like    [if output=='pos']
        index, pos : tuple  [if output=='both']
        data : array_like   [if output=='raw']
        """
        self._check_opened_by_with()
        box_arr = np.array([corner1, corner2], dtype=self._lib.float_dtype)
        if inside:
            self._lib.run.fast3tree_find_inside_of_box(
                self._tree_ptr, self._res_ptr, box_arr
            )
        else:
            self._lib.run.fast3tree_find_outside_of_box(
                self._tree_ptr, self._res_ptr, box_arr
            )
        return self._read_results(output)
