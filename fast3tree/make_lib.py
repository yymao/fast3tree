import os
from subprocess import check_call

def get_lib_name(dim, use_double):
    return 'fast3tree_{0}_{1}'.format(dim, 'd' if use_double else 'f')

def make_lib(dim, use_double, remake=False, path=None):
    if dim < 2:
        raise ValueError('`dim` needs to be at least 2.')
    here = path or os.path.abspath(os.path.dirname(__file__))
    cwd = os.getcwd()
    os.chdir(here)
    lib_name = get_lib_name(dim, use_double)
    if remake or not os.path.isfile(lib_name + '.so'):
        with open(lib_name + '.c', 'w') as f:
            f.write('''#include <inttypes.h>
#define FAST3TREE_FLOATTYPE {1}
struct mytype{{int64_t idx; FAST3TREE_FLOATTYPE pos[{0}];}};
#define FAST3TREE_TYPE struct mytype
#define FAST3TREE_DIM {0}
#include "fast3tree.c"
'''.format(dim, 'double' if use_double else 'float'))
        check_call('gcc -m64 -D_LARGEFILE_SOURCE -D_LARGEFILE64_SOURCE -D_FILE_OFFSET_BITS=64 -D_BSD_SOURCE -D_POSIX_SOURCE -D_POSIX_C_SOURCE=200809L -D_SVID_SOURCE -D_DARWIN_C_SOURCE -Wall -fno-math-errno -fPIC -shared {0}.c -o {0}.so -lm -O3 -std=c99'.format(lib_name).split())
        os.remove(lib_name + '.c')
    os.chdir(cwd)
    return os.path.join(here, lib_name + '.so')
