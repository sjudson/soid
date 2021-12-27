#ifndef INTERSECTION_H_ 
#define INTERSECTION_H_ 

#include <limits.h>

#include "car.h"
#include "util.h"

#define CRASH_ID UINT_MAX

void init_map(unsigned int height, unsigned  int width);

unsigned int is_out_of_boundary(int row, int col);

void clear_map();

unsigned int set_map_element(int row, int col, unsigned int val);

unsigned int get_map_element(int row, int col);

unsigned int is_occupied(int row, int col);

unsigned int is_horizontal_road(int row, int col);

unsigned int is_vertcal_road(int row, int col);

unsigned int is_intersection(int row, int col);

unsigned int is_exit(int row, int col);

unsigned int is_road(int row, int col);
    
Coordinate add_a_car_at(unsigned int id, CardinalDirection from, CardinalDirection to);

unsigned int move_car(unsigned int id, int from_row, int from_col, int to_row, int to_col);

Coordinate get_pos_stop_line(CardinalDirection from);

Coordinate get_pos_turn(CardinalDirection from, CardinalDirection to);

unsigned int is_at_pos_turn(CardinalDirection from, CardinalDirection to, int row, int col);

unsigned int is_at_stop_line(CardinalDirection from, int row, int col);

unsigned int is_intersection_empty();
    
void print_intersection();


#endif
