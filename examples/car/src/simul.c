#include "include/simul.h"

cvector_vector_type(Car*) all_cars = NULL;
Car* ego_vehicle = NULL;
unsigned int car_id = 1;

void get_move(Car* car, IntCtx *ictx, int *dmove) {
  int from_row = car->row;
  int from_col = car->col;

  (car->ego)
    ? move_ego(car, ictx)
    : move(car); //car may or may not move (in car.c)

  int to_row = car->row;
  int to_col = car->col;

  dmove[0] = car->id;
  dmove[1] = from_row;
  dmove[2] = from_col;
  dmove[3] = to_row;
  dmove[4] = to_col;

  return;
}

unsigned int move_cars( Learn *l, Overwrite *ow ) {
  size_t i, j, k;

  IntCtx ictx;
  for (i = 0; i < 4; i++) {
    for (j = 0; j < 4; j++) {
      ictx.locs[i][j] = 0;
      ictx.orients[i][j] = 0;

      for (k = 0; k < 2; k++) ictx.sigs[i][j][k] = 0;
    }
  }

  for (i = 0; i < cvector_size(all_cars); i++) {
    int row = all_cars[i]->row;
    int col = all_cars[i]->col;

    // within intersection frame before intended move
    if (!all_cars[i]->ego && 4 <= row && row <= 7 && 4 <= col && col <= 7) {
      int rrow = row % 4;
      int rcol = col % 4;

      if (ow && ow->id == all_cars[i]->id && ow->new_locs[0] != -1) rrow = ow->new_locs[0] % 4;
      if (ow && ow->id == all_cars[i]->id && ow->new_locs[1] != -1) rrow = ow->new_locs[1] % 4;

      ictx.locs[rrow][rcol] = 1;

      int diff = all_cars[i]->from - all_cars[i]->to;
      int diffabs = abs(diff);

      if (all_cars[i]->needs_turn && !all_cars[i]->has_turned) {
        ictx.sigs[rrow][rcol][0] = ( diff < 0 && diffabs == 1 ) || ( diff > 0 && diffabs == 3 ); // left turn
        ictx.sigs[rrow][rcol][1] = ( diff > 0 && diffabs == 1 ) || ( diff < 0 && diffabs == 3 ); // right turn
      }

      if (ow && ow->id == all_cars[i]->id && ow->new_sigs[0] != -1) ictx.sigs[rrow][rcol][0] = ow->new_sigs[0] % 4;
      if (ow && ow->id == all_cars[i]->id && ow->new_sigs[1] != -1) ictx.sigs[rrow][rcol][1] = ow->new_sigs[1] % 4;

      ictx.orients[rrow][rcol] = (all_cars[i]->has_turned) ? all_cars[i]->to : ((all_cars[i]->from+2) % 4);

      if (ow && ow->id == all_cars[i]->id && ow->new_orient != -1) rrow = ow->new_orient;
    }
  }

  cvector_vector_type(int*) moves = NULL;
  for (i = 0; i < cvector_size(all_cars); i++) {
    cvector_push_back(moves, (int*) malloc(5*sizeof(int)));
    get_move(all_cars[i], &ictx, moves[i]);
  }

  cvector_vector_type(int) rlocs = NULL;
  cvector_vector_type(int) clocs = NULL;

  l->rctx.done = 0;
  l->rctx.exit = 0;
  l->rctx.moved = 0;
  l->rctx.moves = 0.0f;
  l->rctx.crash = 0;
  l->rctx.in = 0;

  int rloc, cloc, tot = 0;
  for (i = 0; i < cvector_size(all_cars);) {
    tot += 1;

    unsigned int done = move_car(moves[i][0], moves[i][1], moves[i][2], moves[i][3], moves[i][4]); // (in intersection.c)

    unsigned int moved = moves[i][1] != moves[i][3] || moves[i][2] != moves[i][4];
    l->rctx.moves = (i==0)
      ? (double) moved
      : ( l->rctx.moves * (tot-1) + (double) moved ) / tot;

    if (all_cars[i]->ego) {
      l->rctx.in = (is_at_stop_line(all_cars[i]->from, moves[i][1], moves[i][2]) || is_intersection(moves[i][1], moves[i][2]));
      l->rctx.exit = is_exit(moves[i][3], moves[i][4]);
      if (moved) {
        l->rctx.moved = 1;
      } else {
        l->rctx.delay += 1;
      }
    }
    rloc = moves[i][3];
    cloc = moves[i][4];

    free(moves[i]);

    if (done) {
      if (all_cars[i] == ego_vehicle) {
        ego_vehicle = NULL; //ego car is done

        l->rctx.done = 1;
      }

      cvector_erase(moves, i);

      free(all_cars[i]);
      cvector_erase(all_cars, i);
    } else {

      for (j = 0; j < i; j++) {
        if (rlocs[j] == rloc && clocs[j] == cloc) {
          l->rctx.done = 1;
          l->rctx.crash = 1;

          set_map_element(rloc, cloc, CRASH_ID);
          break;
        }
      }

      cvector_push_back(rlocs, rloc);
      cvector_push_back(clocs, cloc);

      ++i;
    }
  }

  if (l->rctx.in || l->rctx.exit) {
    l->prev_reward = reward(l);
    l->epi_reward += l->prev_reward;
    l->pmrow = l->mrow;
    memcpy(l->pfv, l->fv, sizeof(double) * (FEATURES+1));
  }

  cvector_free(moves);
  if (l->rctx.done) return 1;

  return 0;
}

Car* generate_a_car(CardinalDirection from, unsigned int ego, Learn *l) {
  CardinalDirection to = from;
  while (to == from)
    to = rand()%4;
  // So, from != to

  Coordinate start_pos = add_a_car_at(car_id, from, to);
  if (start_pos.row != -1) {
    //New car!, learning info will be ignored if not ego
    Car* car = (ego)
      ? create_ego_car(car_id++, start_pos.row, start_pos.col, from, to, l)
      : create_a_car(car_id++, start_pos.row, start_pos.col, from, to);
    cvector_push_back(all_cars, car);
    return car;
  } else {
    return NULL;
  }
}

void generate_cars() {
  if ( rand_0_1() > 0.5 )
    generate_a_car(West, 0, NULL);

  if ( rand_0_1() > 0.5 )
    generate_a_car(North, 0, NULL);

  if ( rand_0_1() > 0.5 )
    generate_a_car(East, 0, NULL);
}

int main(int argc, char const *argv[]) {
  srand( time(NULL) );

  unsigned int height = 12;
  unsigned int width  = 12;
  init_map(height, width);

  size_t i, j;

  Learn l;

  l.test   = 0;
  l.learn  = 1;

  l.gamma   = 0.00f;
  l.epsilon = 0.40f;
  l.alpha   = 0.01f;

  l.profile = 0;

  l.segment  = 10000;
  l.episode  = 0;
  l.episodes = 100000;
  reset(1, &l);

  for (i=1; i < argc; i++) {
    if (strnlen(argv[i], 64) != 2) continue;

    if (strncmp(argv[i], "-x", 64)==0) { l.learn = 0; l.profile = 0; l.scenario = 1; }

    if (strncmp(argv[i], "-d", 64)==0) l.profile = 0;
    if (strncmp(argv[i], "-i", 64)==0) l.profile = 1;
    if (strncmp(argv[i], "-p", 64)==0) l.profile = 2;

    if (strncmp(argv[i], "-a", 64)==0) l.learn = 1;
    if (strncmp(argv[i], "-t", 64)==0) { l.learn = 0; l.test = 1; }
    if (strncmp(argv[i], "-s", 64)==0) { l.learn = 0; l.test = 0; }
  }

  LApprox la;
  l.lmodel = &la;

  QTable qt;
  l.smodel = &qt;

  if (l.learn) {
    for (i = 0; i < ACTIONS; i++)
      for (j = 0; j <= FEATURES; j++) l.lmodel->ws[i][j] = rand_0_1();

    for (i = 0; i < STATES; i++)
      for (j = 0; j <= ACTIONS; j++) l.smodel->qt[i][j] = rand_0_1();
  } else {
    switch(l.profile) {
    case 2:
      memcpy(l.lmodel->ws, pathological_ws, sizeof(double) * ACTIONS * (FEATURES+1));
      memcpy(l.smodel->qt, pathological_qt, sizeof(double) * STATES * ACTIONS);
      break;
    case 1:
      memcpy(l.lmodel->ws, impatient_ws, sizeof(double) * ACTIONS * (FEATURES+1));
      memcpy(l.smodel->qt, impatient_qt, sizeof(double) * STATES * ACTIONS);
      break;
    case 0:
    default:
      memcpy(l.lmodel->ws, defensive_ws, sizeof(double) * ACTIONS * (FEATURES+1));
      memcpy(l.smodel->qt, defensive_qt, sizeof(double) * STATES * ACTIONS);
      break;
    }
  }

  if (l.scenario) return scenario( &l );

  l.l_nctx = NULL;
  l.l_ictx = NULL;
  l.l_decision = NULL;

  printf("\n%s ", (l.learn) ? "Training" : "Simulating");
  printf("with %s reward profile.\n\n", (l.profile == 0) ? "defensive" : (l.profile == 1) ? "impatient" : "pathological");

  if ((!l.learn && !l.test)) usleep(2000*1000);

  unsigned int done;
  while (1) {
    ego_vehicle = NULL;

    if (l.episode >= l.episodes && l.learn) {
      l.learn = 0;
      l.test = 1;

      l.episode = 0;

      printf("\nsaving...");
      save(&l);
      printf(" done.\n\n");
    };

    if (l.episode >= l.episodes && l.test) l.test = 0;

    for (i=0; i<25; i++) {
      if ((!l.learn  && !l.test)) usleep(500*1000);   //=500 ms

      if (!ego_vehicle && (rand_0_1() < 0.15 || i == 10)) {
        ego_vehicle = generate_a_car(South, 1, &l);
        i = 0;
      }

      if (i%5==0)
        generate_cars();    //non-ego vehicles

      done = move_cars(&l, NULL);
      if (done) break;

      if ((!l.learn && !l.test)) print_intersection(&l, ego_vehicle);
    }

    if (l.rctx.in || l.rctx.exit) {
      l.prev_reward = reward(&l);
      l.epi_reward += l.prev_reward;
      l.pmrow = l.mrow;
      memcpy(l.pfv, l.fv, sizeof(double) * (FEATURES+1));
      update(&l, 1);
    }

    if ((!l.learn && !l.test)) {
      print_intersection(&l, ego_vehicle);
      usleep(1000*1000);
    }
    clear_map();

    reset(0, &l);
    while (!cvector_empty(all_cars)) { free(all_cars[0]); cvector_erase(all_cars, 0); }
  }

  cvector_free(all_cars);
  return 0;
}
