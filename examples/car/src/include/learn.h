#ifndef LEARN_H_
#define LEARN_H_

#include "ctxs.h"

#define STATES 1024
#define FEATURES 20
#define ACTIONS 2

typedef struct RewardCtx {
  unsigned int done;  // are we done with the episode
  unsigned int exit;  // agent has successfully exited the intersection
  unsigned int moved; // agent moved in last step
  double moves;       // proportion of agents in/adjacent to intersection that moved in last step
  unsigned int delay; // number of steps in episode where agent did not move in while in/adjacent to intersection
  unsigned int crash; // whether agent has crashed
  unsigned int in;    // whether the agent is in a position where its using RL
} RewardCtx;

typedef struct QTable {
  double qt[STATES][ACTIONS];
} QTable;

typedef struct LApprox {
  double ws[ACTIONS][FEATURES+1];
} LApprox;

typedef struct Learn {

  // learning
  unsigned int learn;
  unsigned int start;
  unsigned int  test;

  double gamma;
  double epsilon;
  double alpha;

  // lmodel
  LApprox *lmodel;
  double fv[FEATURES+1];
  double pfv[FEATURES+1];

  // smodel
  QTable *smodel;
  int mrow;
  int pmrow;

  // stats
  unsigned int segment;
  unsigned int episode;
  unsigned int episodes;

  double epi_reward;
  double avg_reward;
  double seg_avg_reward;

  int tot_crashes;
  int seg_crashes;

  // rewards
  unsigned int profile;
  RewardCtx rctx;

  double prev_reward;
  unsigned int prev_action;

  // scenarios
  int scenario;
  NavCtx   *l_nctx;
  IntCtx   *l_ictx;
  Decision *l_decision;

} Learn;

double reward( Learn *l );

void update( Learn *l, unsigned int end );

void reset( unsigned int init, Learn *l );

void save( Learn *l );

double dot( double ws[FEATURES+1], double fv[FEATURES+1] );

#endif
