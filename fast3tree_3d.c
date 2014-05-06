#include <inttypes.h>
struct mytype{int64_t idx; float pos[3];};
#define FAST3TREE_TYPE struct mytype
#include "fast3tree.c"
