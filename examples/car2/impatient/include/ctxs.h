#ifndef CTXS_H_
#define CTXS_H_

typedef enum _CardinalDirection {North, East, South, West} CardinalDirection;

typedef struct NavCtx {
  CardinalDirection curr_direction;
  CardinalDirection from;
  CardinalDirection to;

  int row;
  int col;

  int needs_turn;
  int has_turned;
} NavCtx;

typedef struct IntCtx {
  int locs[4][4];
  int sigs[4][4][2];
  CardinalDirection orients[4][4];
} IntCtx;

typedef struct Decision {
  int row;
  int col;
} Decision;

#endif
