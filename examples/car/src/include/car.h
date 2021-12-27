#ifndef CAR_H_
#define CAR_H_

#include "learn.h"
#include "util.h"

typedef struct stCar {
  unsigned int id;
  int row;
  int col;

  CardinalDirection from;
  CardinalDirection to;

  unsigned int ego;

  unsigned int needs_turn;
  unsigned int has_turned;

  Learn *l;
} Car;

void test();

Car* create_a_car(unsigned int id, int row, int col, CardinalDirection from, CardinalDirection to);

CardinalDirection driving_direction(CardinalDirection orient, CardinalDirection to, int row, int col);

CardinalDirection turn(Car* car);

int next_row(CardinalDirection cd);

int next_col(CardinalDirection cd);

void move(Car* car);

#endif
