__all__ = ['fast3tree', 'get_distance']
import numpy as np
import numpy.ctypeslib as C
import warnings

# define types
_mytype = np.dtype([('idx', np.int64), ('pos', np.float32, 3)], align=True)
_mytype_ctype =  C.ndpointer(_mytype, flags='C,A')

_results_dtype =  np.dtype([ \
        ('num_points', np.int64), ('num_allocated_points', np.int64), 
        ('points', np.uint64)], align=True)

_center_ctype = C.ndpointer(dtype=np.float32, ndim=1, shape=(3,), flags='C,A')

# load fast3tree c library
_C_LIB = C.load_library('fast3tree_3d', __path__[0])
_ptr_ctype = C.ctypes.c_uint64

_C_LIB.fast3tree_init.restype = _ptr_ctype
_C_LIB.fast3tree_init.argtypes = [C.ctypes.c_int64, _mytype_ctype]

_C_LIB.fast3tree_rebuild.restype = None
_C_LIB.fast3tree_rebuild.argtypes = [_ptr_ctype, C.ctypes.c_int64, \
        _mytype_ctype]

_C_LIB.fast3tree_maxmin_rebuild.restype = None
_C_LIB.fast3tree_maxmin_rebuild.argtypes = [_ptr_ctype]

_C_LIB.fast3tree_free.restype = None
_C_LIB.fast3tree_free.argtypes = [_ptr_ctype]

_C_LIB.fast3tree_results_init.restype = _ptr_ctype
_C_LIB.fast3tree_results_init.argtypes = None

_C_LIB.fast3tree_find_sphere.restype = None
_C_LIB.fast3tree_find_sphere.argtypes = [_ptr_ctype, _ptr_ctype, _center_ctype,\
        C.ctypes.c_float]

_C_LIB.fast3tree_find_sphere_periodic.restype = C.ctypes.c_int
_C_LIB.fast3tree_find_sphere_periodic.argtypes = [_ptr_ctype, _ptr_ctype, \
        _center_ctype, C.ctypes.c_float]

_C_LIB.fast3tree_results_clear.restype = None
_C_LIB.fast3tree_results_clear.argtypes = [_ptr_ctype]

_C_LIB.fast3tree_results_free.restype = None
_C_LIB.fast3tree_results_free.argtypes = [_ptr_ctype]

_C_LIB.fast3tree_set_minmax.restype = None
_C_LIB.fast3tree_set_minmax.argtypes = [_ptr_ctype, C.ctypes.c_float, \
        C.ctypes.c_float]

# define tool functions
def _read_from_address(ptr, dtype, count):
    return np.frombuffer(np.core.multiarray.int_asbuffer(\
            long(ptr), np.dtype(dtype).itemsize*count), dtype, count=count)

def get_distance(center, pos, box_size=-1):
    pos = np.asarray(pos)
    pos_dtype = pos.dtype.type
    d = pos - np.asarray(center, pos_dtype)
    if box_size > 0:
        box_size = pos_dtype(box_size)
        half_box_size = pos_dtype(box_size*0.5)
        d[d >  half_box_size] -= box_size
        d[d < -half_box_size] += box_size
    return np.sqrt(np.sum(d*d, axis=1))

# define fast3tree class
class fast3tree:
    def __init__(self, data):
        '''
        Initialize a fast3tree from a list of points.
        
        Parameters
        ----------
        data : array_like
            must be a 2-d array with last dim = 3.
        '''
        self._copy_data(data)
        self._tree_ptr =  _C_LIB.fast3tree_init(np.int64(self.data.shape[0]), \
                self.data)
        self._res_ptr = _C_LIB.fast3tree_results_init()
        self._check_opened_by_with = self._check_opened_by_with_warn

    def __enter__(self):
        self._check_opened_by_with = self._check_opened_by_with_pass
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.free()

    def _copy_data(self, data):
        data = np.asarray(data)
        if len(data.shape) != 2 or data.shape[1] != 3:
            raise ValueError('data must be a 2-d array with last dim = 3.')
        self.data = np.empty(data.shape[0], _mytype)
        self.data['idx'] = np.arange(data.shape[0], dtype=np.int64)
        self.data['pos'] = data

    def _check_opened_by_with_warn(self):
        warnings.warn("Please use `with` statment to open a fast3tree object.")

    def _check_opened_by_with_pass(self):
        pass

    def _read_results(self, count_only, index_only):
        res = _read_from_address(self._res_ptr, _results_dtype, 1)[0]
        if count_only:
            return res['num_points']
        if res[0]:
            points = _read_from_address(res['points'], _ptr_ctype, res[0])
            points = (points - self.data.ctypes.data)/_mytype.itemsize
        else:
            points = []
        if index_only:
            return self.data['idx'][points]
        else:
            return self.data['idx'][points], self.data['pos'][points]

    def rebuild(self, data=None):
        '''
        Rebuild a fast3tree from a new (or the same) list of points.

        Parameters
        ----------
        data : array_like
            must be a 2-d array with last dim = 3.
        '''
        self._check_opened_by_with()
        if data is not None:
            self._copy_data(data)
        _C_LIB.fast3tree_rebuild(self._tree_ptr, np.int64(self.data.shape[0]), \
                self.data)

    def rebuild_boundaries(self):
        ''' Rebuilds the tree boundaries, but keeps structure the same. '''
        self._check_opened_by_with()
        _C_LIB.fast3tree_maxmin_rebuild(self._tree_ptr)

    def set_boundaries(self, Min, Max):
        '''
        Set the boundaries for periodic boundary condition

        Parameters
        ----------
        Min : float
        Max : float
        '''
        self._check_opened_by_with()
        _C_LIB.fast3tree_set_minmax(self._tree_ptr, np.float32(Min), \
                np.float32(Max))
        
    def free(self):
        ''' Frees the memory of the tree and the results. '''
        self._check_opened_by_with()
        _C_LIB.fast3tree_results_free(self._res_ptr)
        _C_LIB.fast3tree_free(self._tree_ptr)
        self.data = None
        self._tree_ptr = None
        self._res_ptr = None

    def clear_results(self):
        ''' Frees the memory of the results. '''
        self._check_opened_by_with()
        _C_LIB.fast3tree_results_clear(self._res_ptr)

    def query_radius(self, center, r, periodic=False, count_only=False, \
                index_only=True):
        '''
        Find all points within a sphere centered at center with radius r.

        Parameters
        ----------
        center : array_like
        r : float
        periodic : bool, optional
        count_only : bool, optional
        index_only : bool, optional
        '''
        self._check_opened_by_with()
        center_arr = np.asarray(center, dtype=np.float32)
        if periodic:
            _C_LIB.fast3tree_find_sphere_periodic(self._tree_ptr,self._res_ptr,\
                    center_arr, np.float32(r))
        else:
            _C_LIB.fast3tree_find_sphere(self._tree_ptr, self._res_ptr, \
                    center_arr, np.float32(r))
        return self._read_results(count_only, index_only)

