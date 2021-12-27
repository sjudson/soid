#ifndef LCAR_H_
#define LCAR_H_

#include "ctxs.h"
#include "car.h"
#include "util.h"

typedef struct Path {
  int locs[5][2];
  int len;
} Path;

Car* create_ego_car(unsigned int id, int row, int col, CardinalDirection from, CardinalDirection to, Learn *l);

void imove( Learn *l, NavCtx *nctx, IntCtx *ictx, Decision *d );

void move_ego(Car* car, IntCtx *ictx);

char* sig_name( int sig );

char* dir_name( CardinalDirection dir );

#endif
