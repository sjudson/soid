#include "include/car.h"
#include "include/intersection.h"
#include <stdlib.h>
#include <stdio.h>

Car* create_a_car(unsigned int id, int row, int col, CardinalDirection from, CardinalDirection to) {
  Car* newCar = (Car*) malloc(sizeof(Car));
  newCar->id = id;
  newCar->row = row;
  newCar->col = col;
  newCar->from = from;
  newCar->to = to;

  newCar->ego = 0;

  if (from-to == 2 || from-to==-2)
    newCar->needs_turn = 0;   //example: west -> east
  else
    newCar->needs_turn = 1;   //example: west -> south

  newCar->has_turned = 0;

  return newCar;
}

CardinalDirection driving_direction(CardinalDirection orient, CardinalDirection to, int row, int col) {
  if (orient == to) return orient;

  CardinalDirection from = (orient+2) % 4; //flip of orient, example: From West to South. First East and then South
  if (is_at_pos_turn(from, to, row, col)) return to;

  return orient;
}

CardinalDirection turn(Car *car) {
  if (car->needs_turn && !car->has_turned) {
    //check if it's time to make a turn
    if ( is_at_pos_turn(car->from, car->to, car->row, car->col ) )
      car->has_turned = 1;
  }

  return (!car->has_turned)
    ? driving_direction((car->from+2) % 4, car->to, car->row, car->col)
    : driving_direction(car->to, car->to, car->row, car->col);
}

int next_row(CardinalDirection cd) {
  int d = 0;
  switch (cd) {
    case North:
      d = -1;
      break;
    case South:
      d = +1;
      break;
    default:
      d =  0;
  }

  return d;
}

int next_col(CardinalDirection cd) {
  int d = 0;
  switch (cd) {
    case West:
      d = -1;
      break;
    case East:
      d = +1;
      break;
    default:
      d =  0;
  }

  return d;
}

void move(Car* car) {

  CardinalDirection curr_direction;
  curr_direction = turn(car);

  int new_row = car->row + next_row(curr_direction);
  int new_col = car->col + next_col(curr_direction);

  if (is_at_stop_line(car->from, car->row, car->col)) {           // don't enter intersection unless it's currently empty
    if (is_intersection_empty()==0) {
      //not empty -> do not move
      return;
    } else {
      //empty -> I think I can go
      car->row = new_row;
      car->col = new_col;
      return;
    }
  }

  if (is_intersection(car->row, car->col)==0 &&
      is_occupied(new_row, new_col)==0) {                         // if outside intersection and where we're going is empty move up
    car->row = new_row;
    car->col = new_col;

    return;
  } else {                                                        // otherwise
    if (is_intersection(car->row,car->col) &&
        is_intersection(new_row, new_col)  &&
        is_occupied(new_row, new_col)) return;                    // if we're in intersection wait for road to clear

    int proj_row = new_row;
    int proj_col = new_col;
    while (1) {                                                   // and otherwise move forward unless there's no empty space between here and the intersection
      if (is_at_stop_line(car->from, proj_row, proj_col)) return;

      proj_row += next_row(curr_direction);
      proj_col += next_col(curr_direction);

      if (is_occupied(proj_row, proj_col)==0 ||
          is_out_of_boundary(proj_row, proj_col)) break;
    }
    car->row = new_row;
    car->col = new_col;

    return;
  }
}
