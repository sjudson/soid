#include "include/intersection.h"
#include "include/lcar.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

unsigned int HEIGHT = 12;
unsigned int WIDTH = 12;

unsigned int* map;

void init_map(unsigned int _height, unsigned int _width) {
    HEIGHT = _height;
    WIDTH = _width;
    map = (unsigned int*) malloc(sizeof(unsigned int)*HEIGHT*WIDTH);
    memset(map, 0, sizeof(unsigned int)*HEIGHT*WIDTH);
}

unsigned int is_out_of_boundary(int row, int col) {
    if ( row>=HEIGHT || col>=WIDTH || row<0 || col<0 )
        return 1;
    else
        return 0;
}

void clear_map() {
  memset(map, 0, sizeof(unsigned int)*HEIGHT*WIDTH);
}

unsigned int set_map_element(int row, int col, unsigned int val) {
    if (is_out_of_boundary(row, col))
        return 0;

    map[row*WIDTH + col] = val;
    return 1;
}

unsigned int get_map_element(int row, int col) {
    if (is_out_of_boundary(row, col))
        return 0;

    return map[row*WIDTH + col];
}

unsigned int is_occupied(int row, int col) {
    if (is_out_of_boundary(row, col))
        return 0;

    if (map[row*WIDTH + col]==0) {
        return 0;
    } else {
        return 1;
    }
}

unsigned int is_horizontal_road(int row, int col) {
    if (row==HEIGHT/2 || row==HEIGHT/2-1)
        return 1;
    return 0;
}

unsigned int is_vertcal_road(int row, int col) {
    if (col==WIDTH/2 || col==WIDTH/2-1)
        return 1;
    return 0;
}

unsigned int is_intersection(int row, int col) {
  return is_horizontal_road(row, col) && is_vertcal_road(row, col);
}

unsigned int is_exit(int row, int col) {
  return (row==HEIGHT/2+1 && col==WIDTH/2-1) || (row==HEIGHT/2 && col==WIDTH/2+1) || (row==HEIGHT/2-1 && col==WIDTH/2-2) || (row==HEIGHT/2-2 && col==WIDTH/2);
}

unsigned int is_road(int row, int col) {
    return is_horizontal_road(row, col) || is_vertcal_road(row, col);
}

Coordinate add_a_car_at(unsigned int id, CardinalDirection from, CardinalDirection to) {
    Coordinate start_pos = {-1, -1};
    int row=0, col=0;
    switch (from)
    {
        case West:
            row = HEIGHT/2;
            col = 0;
            break;
        case East:
            row = HEIGHT/2 - 1;
            col = WIDTH - 1;
            break;
        case North:
            row = 0;
            col = WIDTH/2 - 1;
            break;
        case South:
            row = HEIGHT - 1;
            col = WIDTH/2;
            break;
    }

    if (is_occupied(row, col)) {
        // will return (-1, -1)
    }
    else {
        set_map_element(row, col, id);
        start_pos.row = row;
        start_pos.col = col;
    }
    return start_pos;
}

unsigned int move_car(unsigned int id, int from_row, int from_col, int to_row, int to_col) {
    set_map_element(from_row, from_col, 0);

    if (is_out_of_boundary(to_row, to_col) == 0) {
      //printf("Setting Element %02d at (%02d, %02d)\n", id, to_row, to_col);
      set_map_element(to_row, to_col, id);
      return 0;
    }
    else {
        return 1;    //done
    }
}

Coordinate get_pos_stop_line(CardinalDirection from) {
    int stop_row=0, stop_col=0;

    switch (from)
    {
        case West:
            stop_row = HEIGHT/2;
            stop_col = WIDTH/2 - 2;
            break;
        case East:
            stop_row = HEIGHT/2 - 1;
            stop_col = WIDTH/2 + 1;
            break;
        case North:
            stop_row = HEIGHT/2 - 2;
            stop_col = WIDTH/2 - 1;
            break;
        case South:
            stop_row = HEIGHT/2 + 1;
            stop_col = WIDTH/2;
    }
    Coordinate pos_stop_line = {stop_row, stop_col};
    return pos_stop_line;
}

Coordinate get_pos_turn(CardinalDirection from, CardinalDirection to) {
    int turn_row=0, turn_col=0;
    //Where to make a turn?

    switch (from)
    {
        case West:
            turn_row = HEIGHT/2;
            if (to==South) {
                turn_col = WIDTH/2 - 1;
            } else if (to==North) {
                turn_col = WIDTH/2;
            } else {
                turn_row = turn_col = -1;
            }
            break;
        case East:
            turn_row = HEIGHT/2 - 1;
            if (to==South) {
                turn_col = WIDTH/2 - 1;
            } else if (to==North) {
                turn_col = WIDTH/2 ;
            } else {
                turn_row = turn_col = -1;
            }
            break;
        case North:
            turn_col = WIDTH/2 - 1;
            if (to==West) {
                turn_row = HEIGHT/2 - 1;
            } else if (to==East) {
                turn_row = HEIGHT/2;
            } else {
                turn_row = turn_col = -1;
            }
            break;
        case South:
            turn_col = WIDTH/2;
            if (to==West) {
                turn_row = HEIGHT/2 - 1;
            } else if (to==East) {
                turn_row = HEIGHT/2;
            } else {
                turn_row = turn_col = -1;
            }
            break;
    }
    Coordinate pos_turn = {turn_row, turn_col};
    return pos_turn;
}

unsigned int is_at_pos_turn(CardinalDirection from, CardinalDirection to, int row, int col) {
    Coordinate pos_turn = get_pos_turn(from, to);
    if (pos_turn.row == row && pos_turn.col == col)
        return 1;
    else
        return 0;
}

unsigned int is_at_stop_line(CardinalDirection from, int row, int col) {
    Coordinate pos_stop_line = get_pos_stop_line (from);
    if (pos_stop_line.row == row && pos_stop_line.col == col)
        return 1;
    else
        return 0;
}

unsigned int is_intersection_empty() {
    unsigned int sum = get_map_element(HEIGHT/2, WIDTH/2) + get_map_element(HEIGHT/2-1, WIDTH/2-1) + get_map_element(HEIGHT/2-1, WIDTH/2) + get_map_element(HEIGHT/2, WIDTH/2-1);
    if (sum==0)
        return 1;
    else
        return 0;
}

unsigned int is_intersection_part_empty(int row, int col) {
  unsigned int sum = get_map_element(HEIGHT/2, WIDTH/2) + get_map_element(HEIGHT/2-1, WIDTH/2-1) + get_map_element(HEIGHT/2-1, WIDTH/2) + get_map_element(HEIGHT/2, WIDTH/2-1);

  sum -= (get_map_element(row, col) != 0);

  if (sum==0)
    return 1;
  else
    return 0;
}

void print_status(Learn *l, Car *ego) {
  if (l->rctx.in || l->rctx.exit) {
    printf("\nStatus:\n");
    printf("\t\tIn:               %02d\n", l->rctx.in);
    printf("\t\tDone:             %02d\n", l->rctx.done);
    printf("\t\tExited:           %02d\n", l->rctx.exit);
    printf("\t\tMoved:            %02d\n", l->rctx.moved);
    printf("\t\tRisky:            %02d\n", l->rctx.risky);
    printf("\t\tCrashed:          %02d\n", l->rctx.crash);
    printf("\t\tProportion Moved: %.4f\n", l->rctx.moves);
    printf("\t\tAmount Delayed:   %02d\n", l->rctx.delay);
    printf("\n\t\tReward:           %.4f\n", (l->rctx.in || l->rctx.done) ? l->prev_reward : 0.0f);

    printf("\n\t\tfeatures:         ttc_p00_t01 = %9.6f, ttc_p00_t02 = %9.6f, ttc_p00_t03 = %9.6f, ttc_p00_t04 = %.6f\n", l->fv[0], l->fv[1], l->fv[2], l->fv[3]);
    printf("\t\tfeatures cont:    ttc_p01_t01 = %9.6f, ttc_p01_t02 = %9.6f, ttc_p01_t03 = %9.6f, ttc_p01_t04 = %.6f\n", l->fv[4], l->fv[5], l->fv[6], l->fv[7]);
    printf("\t\tfeatures cont:    ttc_p02_t01 = %9.6f, ttc_p02_t02 = %9.6f, ttc_p02_t03 = %9.6f, ttc_p02_t04 = %.6f\n", l->fv[8], l->fv[9], l->fv[10], l->fv[11]);
    printf("\t\tfeatures cont:    ttc_p03_t01 = %9.6f, ttc_p03_t02 = %9.6f, ttc_p03_t03 = %9.6f, ttc_p03_t04 = %.6f\n", l->fv[12], l->fv[13], l->fv[14], l->fv[15]);
    printf("\t\tfeatures cont:    ttc_p04_t01 = %9.6f, ttc_p04_t02 = %9.6f, ttc_p04_t03 = %9.6f, ttc_p04_t04 = %.6f, cnst = %.6f\n", l->fv[16], l->fv[17], l->fv[18], l->fv[19], l->fv[20]);

    printf("\n\t\tws to move:       ttc_p00_t01 = %9.6f, ttc_p00_t02 = %9.6f, ttc_p00_t03 = %9.6f, ttc_p00_t04 = %.6f\n", l->lmodel->ws[0][0], l->lmodel->ws[0][1], l->lmodel->ws[0][2], l->lmodel->ws[0][3]);
    printf("\t\tws to move cont:  ttc_p01_t01 = %9.6f, ttc_p01_t02 = %9.6f, ttc_p01_t03 = %9.6f, ttc_p01_t04 = %.6f\n", l->lmodel->ws[0][4], l->lmodel->ws[0][5], l->lmodel->ws[0][6], l->lmodel->ws[0][7]);
    printf("\t\tws to move cont:  ttc_p02_t01 = %9.6f, ttc_p02_t02 = %9.6f, ttc_p02_t03 = %9.6f, ttc_p02_t04 = %.6f\n", l->lmodel->ws[0][8], l->lmodel->ws[0][9], l->lmodel->ws[0][10], l->lmodel->ws[0][11]);
    printf("\t\tws to move cont:  ttc_p03_t01 = %9.6f, ttc_p03_t02 = %9.6f, ttc_p03_t03 = %9.6f, ttc_p03_t04 = %.6f\n", l->lmodel->ws[0][12], l->lmodel->ws[0][13], l->lmodel->ws[0][14], l->lmodel->ws[0][15]);
    printf("\t\tws to move cont:  ttc_p04_t01 = %9.6f, ttc_p04_t02 = %9.6f, ttc_p04_t03 = %9.6f, ttc_p04_t04 = %.6f, cnst = %.6f\n", l->lmodel->ws[0][16], l->lmodel->ws[0][17], l->lmodel->ws[0][18], l->lmodel->ws[0][19], l->lmodel->ws[0][20]);

    printf("\n\t\tws no move:       ttc_p00_t01 = %9.6f, ttc_p00_t02 = %9.6f, ttc_p00_t03 = %9.6f, ttc_p00_t04 = %.6f\n", l->lmodel->ws[1][0], l->lmodel->ws[1][1], l->lmodel->ws[1][2], l->lmodel->ws[1][3]);
    printf("\t\tws no move cont:  ttc_p01_t01 = %9.6f, ttc_p01_t02 = %9.6f, ttc_p01_t03 = %9.6f, ttc_p01_t04 = %.6f\n", l->lmodel->ws[1][4], l->lmodel->ws[1][5], l->lmodel->ws[1][6], l->lmodel->ws[1][7]);
    printf("\t\tws no move cont:  ttc_p02_t01 = %9.6f, ttc_p02_t02 = %9.6f, ttc_p02_t03 = %9.6f, ttc_p02_t04 = %.6f\n", l->lmodel->ws[1][8], l->lmodel->ws[1][9], l->lmodel->ws[1][10], l->lmodel->ws[1][11]);
    printf("\t\tws no move cont:  ttc_p03_t01 = %9.6f, ttc_p03_t02 = %9.6f, ttc_p03_t03 = %9.6f, ttc_p03_t04 = %.6f\n", l->lmodel->ws[1][12], l->lmodel->ws[1][13], l->lmodel->ws[1][14], l->lmodel->ws[1][15]);
    printf("\t\tws no move cont:  ttc_p04_t01 = %9.6f, ttc_p04_t02 = %9.6f, ttc_p04_t03 = %9.6f, ttc_p04_t04 = %.6f, cnst = %.6f\n", l->lmodel->ws[1][16], l->lmodel->ws[1][17], l->lmodel->ws[1][18], l->lmodel->ws[1][19], l->lmodel->ws[1][20]);

    printf("\n\t\t(s, to mov) val:  %.6f\n", dot(l->lmodel->ws[0], l->fv));
    printf("\t\t(s, no mov) val:  %.6f\n", dot(l->lmodel->ws[1], l->fv));

    printf("\n\t\tqt row:           %02d\n", l->mrow);
    printf("\t\tqt state:         int = %d, ent = %d, ine = %d\n", (l->mrow & 512) >> 9, (l->mrow & 256) >> 8, (l->mrow & 128) >> 7) ;
    printf("\t\tqt state cont:    s1i = %d, s1o = %d, s2i = %d, s2o = %d,\n", (l->mrow & 64) >> 6, (l->mrow & 32) >> 5, (l->mrow & 16) >> 4, (l->mrow & 8) >> 3);
    printf("\t\tqt state cont:    oce = %d, bin = %d, bot = %d\n", (l->mrow & 4) >> 2, (l->mrow & 2) >> 1, l->mrow & 1);

    printf("\n\t\t(s, to mov) val:  %.6f\n", l->smodel->qt[l->mrow][0]);
    printf("\t\t(s, no mov) val:  %.6f\n", l->smodel->qt[l->mrow][1]);

    printf("\n");
  }

  return;
}

void print_intersection(Learn *l, Car *ego) {

  char* markers[] = {"#","o", "$", "w", "@", "x"};

  //print_status(l, ego);
  system("clear");
  int crash = 0;
  for (size_t i=0; i<HEIGHT; i++) {
      for (size_t j=0; j<WIDTH; j++) {
          if (is_road(i,j)) {
              unsigned int id = get_map_element(i,j);
              char* marker = id==0?".":markers[id% ((sizeof(markers)/sizeof(*markers)))];
              if (ego && id==ego->id) marker = "\033[31me\033[0m";
              if (id==CRASH_ID) marker = "\033[33m*\033[0m";
              printf("%s", marker);
          }
          else
            printf(" ");
      }
      printf("\n");
  }
  printf("\n");

  print_status(l, ego);

  return;
}
