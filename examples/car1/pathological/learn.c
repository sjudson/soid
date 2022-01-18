#include "include/learn.h"
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <assert.h>

#define MAX(M,N) ((M>N)?(M):(N))

double reward( Learn *l ) {

  double r = 0.0f;

  if (l->profile == 2) { // pathological

    //r += (double) l->rctx.moved; // +1 for moving

    if (!l->rctx.done) return r;

    if (l->rctx.exit)  r -= 20;     // penalty for reaching exit
    if (l->rctx.crash) r += 1000.0; // massive reward for causing a crash

    return r;
  }

  if (l->profile == 1) { // impatient

    r += (double) l->rctx.moved;                     // +1 for moving

    if (!l->rctx.done) return r;

    if (l->rctx.exit) {
      r += 100;                                      // +100 for succcessfully exiting the intersection
      r += MAX( 10.0 - (double) l->rctx.delay, 0 );  // +[0, 10] for being as fast as possible
    } else {
      r -= 20;                                       // -20 for failing to clear the intersection
    }

    return r;
  }

  // l->profile == 0, defensive
  if (l->rctx.moved) {
    r += (double) l->rctx.moved;                   // +1 for moving
    r += l->rctx.moves / 20.0f;                    // +[0, 0.5] for contributing to the intersection moving smoothly

    if (l->rctx.risky) r -= (double) 5;            // -5 for a risky move that doesn't crash
  }

  if (l->rctx.exit) {
    r += 20.0f;                                    // +20 for succcessfully exiting the intersection
    r += MAX( 5.0 - (double) l->rctx.delay, 0.0 ); // +[0, 5] for being as fast as possible
  } else if (l->rctx.done) {
    r -= 10.0f;                                    // -10 for failing to clear the intersection
  }
  if (l->rctx.crash) r -= 1000.0;                  // penalty for causing a crash

  return r;
}

void update( Learn *l, unsigned int end ) {

  if (!l->learn) return;                   // don't update if we're simulating, not training
  if (!l->rctx.in && !l->rctx.done) return; // only update if we're in a place where we're applying RL or are done with the episode

  if (l->start) {                           // if we haven't yet made an action then we don't have a previous state to update
    l->start = 0;
    return;
  }

  size_t i;
  double lval = -INFINITY;
  double sval = -INFINITY;
  if (end) {
    lval = 0.0f;                            // any end of episode state inherently has a future value of zero, but likely comes with a significant +/- reward
    sval = 0.0f;                            // any end of episode state inherently has a future value of zero, but likely comes with a significant +/- reward
  } else {
    for (i = 0; i < ACTIONS; i++) {
      lval = MAX( lval, dot(l->lmodel->ws[i], l->fv) ); // max Q(s', a') for linear approximator
      sval = MAX( sval, l->smodel->qt[l->mrow][i] );    // max Q(s', a') for q-table
    }
  }

  double lpval = dot(l->lmodel->ws[l->prev_action], l->pfv); // Q(s, a) for linear approximator
  double spval = l->smodel->qt[l->pmrow][l->prev_action];    // Q(s, a) for q-table

  for (i = 0; i <= FEATURES; i++) l->lmodel->ws[l->prev_action][i] += l->alpha * ( l->prev_reward + l->gamma * lval - lpval) * l->pfv[i]; // update for linear approximator
  l->smodel->qt[l->pmrow][l->prev_action] += l->alpha * (l->prev_reward + l->gamma * sval - spval);                                       // update for q-table

  return;
}

void reset( unsigned int init, Learn *l ) {

  if (!init) {
    // compute stats
    l->episode += 1;

    l->alpha   = l->alpha * (1 - (l->episode / l->episodes));
    l->epsilon = l->epsilon * (1 - (l->episode / l->episodes));

    unsigned int start  = (l->episode==1);

    unsigned int sepi   = (l->episode % l->segment);
    unsigned int sstart = (sepi==1);
    unsigned int send   = (sepi==0);

    if (l->rctx.crash) {
      l->tot_crashes += 1;
      l->seg_crashes += 1;
    }

    l->avg_reward = (start)
      ? l->epi_reward
      : (l->avg_reward * (l->episode-1) + l->epi_reward) / l->episode;

    if (send) {
      printf("completed %s episode %010d. avg_reward: %9.6f, tot_crashes: %d, seg_avg_reward: %9.6f, seg_crashes: %05d\n", (l->learn) ? "train" : "test", l->episode, l->avg_reward, l->tot_crashes, l->seg_avg_reward, l->seg_crashes);

      l->seg_avg_reward = 0.0f;
      l->seg_crashes = 0;
    } else {
      l->seg_avg_reward = (sstart)
        ? l->epi_reward
        : (l->seg_avg_reward * (sepi-1) + l->epi_reward) / sepi;
    }
  } else {
    l->tot_crashes = 0;
    l->seg_crashes = 0;
  }
  l->epi_reward = 0;

  l->start = 1;

  l->rctx.done = 0;
  l->rctx.exit = 0;
  l->rctx.moved = 0;
  l->rctx.moves = 0.0f;
  l->rctx.delay = 0;
  l->rctx.crash = 0;

  return;
}

void save( Learn *l ) {

  char names[3][16] = { "defensive", "impatient", "pathological" };
  char *name = names[ l->profile ];

  char path[32];
  sprintf(path, "./models/%s.c", name);
  FILE *fp = fopen(path, "w");

  assert(fp != NULL);

  size_t i, j;

  fprintf(fp, "#include \"models.h\"\n\n");

  fprintf(fp, "const double %s_ws[ACTIONS][FEATURES+1] = {\n", name);
  for (i = 0; i < ACTIONS; i++) {
    fprintf(fp, "  { ");
    for (j = 0; j <= FEATURES; j++) {
      fprintf(fp, "%.17g", l->lmodel->ws[i][j]);
      if (j != FEATURES) fprintf(fp, ", ");
    }
    fprintf(fp, " }");
    if (i+1 < ACTIONS) fprintf(fp, ",");
    fprintf(fp, "\n");
  }
  fprintf(fp, "};\n\n");

  fprintf(fp, "const double %s_qt[STATES][ACTIONS] = {\n", name);
  for (i = 0; i < STATES; i++) {
    fprintf(fp, "  { ");
    for (j = 0; j < ACTIONS; j++) {
      fprintf(fp, "%.17g", l->smodel->qt[i][j]);
      if (j+1 < ACTIONS) fprintf(fp, ", ");
    }
    fprintf(fp, " }");
    if (i+1 < STATES) fprintf(fp, ",");
    fprintf(fp, "\n");
  }
  fprintf(fp, "};\n");

  fclose(fp);
  return;
}

double dot( double ws[FEATURES+1], double fv[FEATURES+1] ) {
  double t = 0.0f;
  for (size_t i = 0; i <= FEATURES; i++) t += ws[i] * fv[i];
  return t;
}
