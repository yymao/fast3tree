import os
import tempfile
from subprocess import check_call

__all__ = ['make_lib']

_TMPDIR = None


def make_lib(dim, use_double, remake=False, path=None):
    global _TMPDIR

    dim = int(dim)
    if dim < 2:
        raise ValueError('`dim` needs to be at least 2.')

    src_dir = os.path.abspath(os.path.dirname(__file__))
    lib_dir = path or src_dir

    lib_name = 'fast3tree_{0}_{1}'.format(dim, 'd' if use_double else 'f')
    lib_so_path = os.path.join(lib_dir, lib_name + '.so')

    if not remake:
        if os.access(lib_so_path, os.R_OK):
            return lib_so_path

        if _TMPDIR is not None:
            lib_so_path = os.path.join(_TMPDIR, lib_name + '.so')
            if os.access(lib_so_path, os.R_OK):
                return lib_so_path

    if not os.access(lib_dir, os.W_OK):
        if _TMPDIR is None:
            _TMPDIR = tempfile.mkdtemp("_fast3tree")
        lib_dir = _TMPDIR

    lib_path = os.path.join(lib_dir, lib_name)
    lib_so_path = lib_path + '.so'
    lib_c_path = lib_path + '.c'

    with open(lib_c_path, 'w') as f:
        f.write('''#include <inttypes.h>
#define FAST3TREE_FLOATTYPE {1}
struct mytype{{int64_t idx; FAST3TREE_FLOATTYPE pos[{0}];}};
#define FAST3TREE_TYPE struct mytype
#define FAST3TREE_DIM {0}
#include "{2}/fast3tree.c"
'''.format(dim, 'double' if use_double else 'float', src_dir))
    check_call('gcc -m64 -D_LARGEFILE_SOURCE -D_LARGEFILE64_SOURCE -D_FILE_OFFSET_BITS=64 -D_DEFAULT_SOURCE -D_POSIX_SOURCE -D_POSIX_C_SOURCE=200809L -D_SVID_SOURCE -D_DARWIN_C_SOURCE -Wall -fno-math-errno -fPIC -shared {0} -o {1} -lm -O3 -std=c99'.format(lib_c_path, lib_so_path).split())
    os.remove(lib_c_path)

    return lib_so_path
