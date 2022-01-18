#include "include/util.h"
#include <stdlib.h>

double rand_0_1() {
    return (double)rand() / (RAND_MAX + 1.0);
}
