#include <inttypes.h>
struct mytype{int64_t idx; float pos[2];};
#define FAST3TREE_TYPE struct mytype
#define FAST3TREE_DIM 2
#include "fast3tree.c"
