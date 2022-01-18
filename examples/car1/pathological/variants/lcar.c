#include "include/lcar.h"
#include "include/car.h"
#include "include/intersection.h"
#include "include/util.h"
#include <stdlib.h>

#define ABS(N) ((N<0)?(-N):(N))


Car* create_ego_car(unsigned int id, int row, int col, CardinalDirection from, CardinalDirection to, Learn *l) {
  Car* newCar = (Car*) malloc(sizeof(Car));
  newCar->id = id;
  newCar->row = row;
  newCar->col = col;
  newCar->from = from;
  newCar->to = to;

  newCar->ego = 1;

  if (from-to == 2 || from-to==-2)
    newCar->needs_turn = 0;   //example: west -> east
  else
    newCar->needs_turn = 1;   //example: west -> south

  newCar->has_turned = 0;

  newCar->l = l;

  return newCar;
}


char r[6]  = "right";
char l[5]  = "left";
char st[9] = "straight";
char* sig_name( int sig ) {
  switch(sig) {
  case 0:
    return r;
  case 1:
    return l;
  case 2:
    return st;
  }

  return NULL;
}

char n[6] = "North";
char w[5] = "West";
char s[6] = "South";
char e[5] = "East";
char* dir_name( CardinalDirection dir ) {
  switch(dir) {
  case North:
    return n;
  case West:
    return w;
  case South:
    return s;
  case East:
    return e;
  }

  return NULL;
}

unsigned int empty_intersection( IntCtx *ictx ) {
  unsigned int mult = (1 - ictx->locs[1][1]) * (1 - ictx->locs[1][2]) * (1 - ictx->locs[2][1]) * (1 - ictx->locs[2][2]);
  return (mult!=0);
}

unsigned int full_intersection( IntCtx *ictx ) {
  unsigned int mult = ictx->locs[1][1] * ictx->locs[1][2] * ictx->locs[2][1] * ictx->locs[2][2];
  return (mult!=0);
}



////// ABOVE: Utilities, BELOW: Decision Logic



unsigned int project_path( int cmp, Path *p, CardinalDirection to, CardinalDirection orient, int rrow, int rcol ) {
  // in practice this would be more efficient using dynamic programming to save info between cars
  if (!cmp) {
    p->locs[0][0] = rrow;
    p->locs[0][1] = rcol;
    p->len = 0;
  }

  int proj_row = rrow;
  int proj_col = rcol;

  int delta_row, delta_col;

  size_t i;
  for (i = 1; i < 5; i++) {
    if (cmp && i > p->len) return 0;

    orient = driving_direction(orient, to, proj_row + 4, proj_col + 4);

    delta_row = 0;
    delta_col = 0;

    switch (orient) {
    case North:
      delta_row = -1;
      break;
    case South:
      delta_row = +1;
      break;
    case West:
      delta_col = -1;
      break;
    case East:
      delta_col = +1;
      break;
    }

    proj_row += delta_row;
    proj_col += delta_col;

    if (proj_row < 0 || proj_row > 3 || proj_col < 0 || proj_col > 3) {
      if (!cmp) {
        p->locs[i][0] = -1;
        p->locs[i][1] = -1;
      }

      return 0;
    }

    if (!cmp) {
      p->locs[i][0] = proj_row;
      p->locs[i][1] = proj_col;
      p->len += 1;

      continue;
    }

    // cmp == 1
    if (proj_row == p->locs[i][0] && proj_col == p->locs[i][1]) return i;
  }

  return 0;
}

unsigned int get_to( unsigned int sig, CardinalDirection orient, int rrow, int rcol ) {
  // we assume signal goes off after car has passed the turning point, which is consistent with how driving_direction() works
  switch(sig) {
  case 0:      // right
    if (rrow == 0) return West;
    if (rrow == 1) return North;
    if (rrow == 2) return South;
    if (rrow == 3) return East;
  case 1:      // left
    if (rrow == 0) return East;
    if (rrow == 1) return (orient == West) ? South : (orient == South) ? East : West;
    if (rrow == 2) return (orient == East) ? North : (orient == South) ? East : West;
    if (rrow == 3) return West;
  case 2:      // straight
  default:     // in real code we'd throw an exception here
    return orient;
  }
}

unsigned int compare_path_from_signal( Path *ep, unsigned int sig, CardinalDirection orient, int rrow, int rcol ) {
  return project_path( 1, ep, get_to(sig, orient, rrow, rcol), orient, rrow, rcol );
}

void get_state( int* mrow, NavCtx *nctx, IntCtx *ictx ) {

  *mrow = 0;

  size_t i, j, k;

  int rrow = nctx->row % 4;
  int rcol = nctx->col % 4;

  // state components:
  //           0. in intersection
  //           1. at entry
  //           2. intersection is empty
  //           3. square ahead in intersection
  //           4. square ahead occupied
  //           5. next square of car ahead in intersection
  //           6. next square of car ahead occupied
  //           7. car other than us trying to enter square ahead
  //           8. car behind and inside the intersection trying to enter the square
  //           9. car behind and outside the intersection trying to enter the square

  // 0.
  if (is_intersection(nctx->row, nctx->col))
    *mrow += 512;                                                 // ( STATES / 2 )

  // 1.
  if ((rrow == 0 && rcol == 1) || (rrow == 1 && rcol == 3) ||
      (rrow == 2 && rcol == 0) || (rrow == 3 && rcol == 2))
    *mrow += 256;                                                 // ( STATES / 2 * 2 )

  // 2.
  if (empty_intersection(ictx))
    *mrow += 128;                                                 // ( STATES / 4 * 2 )

  Path ego_path;
  unsigned int _ = project_path(0, &ego_path, nctx->to, nctx->curr_direction, rrow, rcol);

  int nrow = ego_path.locs[1][0];
  int ncol = ego_path.locs[1][1];

  // 3.
  if (is_intersection(nrow+4, ncol+4))
    *mrow += 64;                                                  // ( STATES / 8 * 2 )

  // 4.
  unsigned int sig;
  if (ictx->locs[nrow][ncol]) {
    *mrow += 32;                                                  // ( STATES / 16 * 2 )

    Path other_path;

    sig = 2;
    for (k = 0; k <= 1; k++) sig -= (k+1) * ictx->sigs[nrow][ncol][k];

    _ = project_path(0, &other_path, get_to(sig, ictx->orients[nrow][ncol], nrow, ncol), ictx->orients[nrow][ncol], nrow, ncol);

    nrow = other_path.locs[1][0];
    ncol = other_path.locs[1][1];

    if (other_path.len > 0) {
      // 5.
      if (is_intersection(nrow+4, ncol+4))
        *mrow += 16;                                                  // ( STATES / 32 * 2 )

      // 6.
      if (ictx->locs[nrow][ncol])
        *mrow += 8;                                                   // ( STATES / 64 * 2 )
    }
  }

  Path ego_stationary;
  ego_stationary.len = 1;
  ego_stationary.locs[0][0] = rrow;
  ego_stationary.locs[0][1] = rcol;
  ego_stationary.locs[1][0] = rrow;
  ego_stationary.locs[1][1] = rcol;
  ego_stationary.locs[2][0] = -1;
  ego_stationary.locs[2][1] = -1;

  unsigned int oth  = 0;
  unsigned int bin  = 0;
  unsigned int bout = 0;
  for (i = 0; i < 4; i++) {
    for (j = 0; j < 4; j++) {
      if (!is_road(i+4, j+4)) continue;
      if (!ictx->locs[i][j])  continue;

      sig = 2;
      for (k = 0; k <= 1; k++) sig -= (k+1) * ictx->sigs[i][j][k];

      unsigned int comp = compare_path_from_signal(&ego_stationary, sig, ictx->orients[i][j], i, j) == 1;
      if (comp) {
        if (is_intersection(i+4, j+4)) { bin = 1; } else { bout = 1; }
      }

      oth = oth || (compare_path_from_signal(&ego_path, sig, ictx->orients[i][j], i, j) == 1);
    }
  }

  // 7.
  if (oth)
    *mrow += 4;                                                   // ( STATES / 128 * 2 )

  // 8.
  if (bin)
    *mrow += 2;                                                   // ( STATES / 256 * 2 )

  // 9.
  if (bout)
    *mrow += 1;                                                   // ( STATES / 512 * 2 )

  return;
}

void get_features( double fv[FEATURES+1], NavCtx *nctx, IntCtx *ictx ) {

  int rrow = nctx->row % 4;
  int rcol = nctx->col % 4;

  size_t i, j, k;

  // features:
  //           i. time-to-collision (ttc) indicator for i = (path position * 4) + steps away

  Path ep;
  Path ps[12];

  unsigned int _ = project_path(0, &ep, nctx->to, nctx->curr_direction, rrow, rcol);

  unsigned int loc, sig;
  unsigned int m = 0;
  for (i = 0; i < 4; i++) {
    for (j = 0; j < 4; j++) {
      if (!is_road(i+4,j+4)) continue;
      if (ictx->locs[i][j] == 0) continue;

      sig = 2;
      for (k = 0; k <= 1; k++) sig -= (k+1) * ictx->sigs[i][j][k];

      _ = project_path( 0, &ps[m], get_to(sig, ictx->orients[i][j], i, j), ictx->orients[i][j], i, j );
      m++;
    }
  }

  for (i = 0; i < m; i++) {     // visible car
    loc = 0;
    for (j = 0; j < 5; j++) {   // position in path
      for (k = 1; k < 5; k++) { // time within horizon
        fv[loc++] = (double) (k <= ps[i].len && j <= ep.len && ps[i].locs[k][0] == ep.locs[j][0] && ps[i].locs[k][1] == ep.locs[j][1]);
      }
    }
  }
  fv[20] = 1.0f;

  return;
}

unsigned int imove( Learn *l, NavCtx *nctx, IntCtx *ictx, Decision *d ) {

  int delta_row = 0;
  int delta_col = 0;

  switch (nctx->curr_direction) {
  case North:
    delta_row = -1;
    break;
  case South:
    delta_row = +1;
    break;
  case West:
    delta_col = -1;
    break;
  case East:
    delta_col = +1;
    break;
  }

  int new_row = nctx->row + delta_row;
  int new_col = nctx->col + delta_col;

  // we're going to make a simplifying assumption that the structure of the
  // intersection is integrated into the agent, e.g. with mapping software
  if (is_at_stop_line(nctx->from, nctx->row, nctx->col) || is_intersection(nctx->row, nctx->col)) {

    get_state( &(l->mrow), nctx, ictx );
    get_features( l->fv, nctx, ictx );
    update(l, 0);

    unsigned int m;

    // random
    if (l->learn && rand_0_1() <= l->epsilon) {
      m = (rand_0_1() <= 0.5);

      if (m) { // pick randomly between moving and not
        d->row = new_row;
        d->col = new_col;
      }

      return m;
    }

    double ls0 = dot(l->lmodel->ws[0], l->fv);
    double ls1 = dot(l->lmodel->ws[1], l->fv);

    double ss0 = l->smodel->qt[l->mrow][0];
    double ss1 = l->smodel->qt[l->mrow][1];

    unsigned int guard = (l->profile == 0) ? ss0 >= ss1 : (ss0 >= ss1 || ls0 >= ls1); 

    // add a simple shield that disables entering the intersection if it is full
    m = guard && !full_intersection(ictx);
    if (m) {
      d->row = new_row;
      d->col = new_col;
    }

    return m;
  }

  // outside intersection
  if (is_intersection(nctx->row, nctx->col)==0 &&
      is_occupied(new_row, new_col)==0) {                       // if outside where we're going is empty move up
    d->row = new_row;
    d->col = new_col;

    return 1;
  }

  int proj_row = new_row;
  int proj_col = new_col;
  while (1) {                                                   // and otherwise move forward unless there's no empty space between here and the intersection
    if (is_at_stop_line(nctx->from, proj_row, proj_col)) return 0;

    proj_row += next_row(nctx->curr_direction);
    proj_col += next_col(nctx->curr_direction);

    if (is_occupied(proj_row, proj_col)==0 ||
        is_out_of_boundary(proj_row, proj_col)) break;
  }
  d->row = new_row;
  d->col = new_col;

  return 1;
}

void move_ego(Car* car, IntCtx *ictx) {

  // this method simulates applying the car's sensors and internal preprocessing.

  NavCtx nctx;
  Decision d;

  d.row = car->row;
  d.col = car->col;

  nctx.curr_direction = turn(car);
  nctx.from = car->from;
  nctx.to   = car->to;
  nctx.row  = car->row;
  nctx.col  = car->col;
  nctx.needs_turn = car->needs_turn;
  nctx.has_turned = car->has_turned;

  unsigned int moved = imove(car->l, &nctx, ictx, &d);

  if (moved) {
    car->row = d.row;
    car->col = d.col;
  }
  car->l->prev_action = !(moved); // cause 0->move and 1->do not move

  // for scenario symbolic execution printing:
  size_t i, j, k;
  if (car->l->l_nctx != NULL) {
    car->l->l_nctx->curr_direction = nctx.curr_direction;
    car->l->l_nctx->from = nctx.from;
    car->l->l_nctx->to   = nctx.to;
    car->l->l_nctx->row  = nctx.row;
    car->l->l_nctx->col  = nctx.col;
    car->l->l_nctx->needs_turn = nctx.needs_turn;
    car->l->l_nctx->has_turned = nctx.has_turned;
  }

  if (car->l->l_ictx != NULL) {
    for (i = 0; i < 4; i++) {
      for (j = 0; j < 4; j++) {
        car->l->l_ictx->locs[i][j] = ictx->locs[i][j];
        car->l->l_ictx->orients[i][j] = ictx->orients[i][j];

        for (k = 0; k < 2; k++) car->l->l_ictx->sigs[i][j][k] = ictx->sigs[i][j][k];
      }
    }
  }

  if (car->l->l_decision != NULL) {
    car->l->l_decision->row = d.row;
    car->l->l_decision->col = d.col;
  }

  return;
}
