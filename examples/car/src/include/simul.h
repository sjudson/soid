#ifndef SIMUL_H_
#define SIMUL_H_

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <math.h>
#include <string.h>
#include "learn.h"
#include "lcar.h"
#include "car.h"
#include "intersection.h"
#include "util.h"
#include "cvector.h"
#include "../models/models.h"
#include "../scenarios/scenario.h"

extern cvector_vector_type(Car*) all_cars;
extern Car* ego_vehicle;
extern unsigned int car_id;

typedef struct Overwrite {
  int id;

  int new_locs[2];
  int new_sigs[2];
  int new_orient;
} Overwrite;

unsigned int move_cars( Learn *l, Overwrite *ow );

#endif
