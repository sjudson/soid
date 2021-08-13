#include "klee.h"
#include <cstdio>
#include <iostream>
#include <limits>


#define MAX_LEN 250
#define OBS_SPACE 8
#define CHOICE_STATE 13
#define ACTION_SPACE 2


bool is_check( bool act ) { return act == 1; }

double dot( double *xs, double *ys, int len ) {
  double prod;
  for ( int i = 0; i < len; i++ ) prod += xs[ i ] * ys[ i ];

  return prod;
}


int argmax( double* xs, int len ) {
  int dec;
  double dv = -1 * std::numeric_limits<double>::infinity();

  for ( int i = 0; i < len; i++ ) {
    if ( xs[ i ] > dv ) {
      dec = i;
      dv  = xs[ i ];
    }
  }

  return dec;
}


typedef struct hist {
  bool actions[ MAX_LEN ];
  int  length;
  int  completed;
  double ep_reward;
  double ep_cost;
} hist;


typedef struct model {
  int ws_len;
  int st_len;
  double ws[ ACTION_SPACE ][ CHOICE_STATE ];
} model;


int plan( double *obs, hist *ht, model *md ) {

  double checks = 0.0;
  for ( int i = 0; i < ht->completed; i++ ) if ( is_check( ht->actions[ i ] ) ) checks += 1.0f;

  double proportion = ( ( double ) ht->completed + 1.0f ) / ( double ) ht->length;

  double st[ CHOICE_STATE ];
  st[ 0 ] = checks;
  st[ 1 ] = proportion;
  st[ 2 ] = ht->ep_reward;
  st[ 3 ] = ht->ep_cost;
  for ( int j = 0; j < OBS_SPACE; j++ ) st[ 4 + j ] = obs[ j ];
  st[ CHOICE_STATE - 1 ] = 1.0f;

  double ss[ ACTION_SPACE ];
  for ( int k = 0; k < ACTION_SPACE; k++ ) ss[ k ] = dot( st, md->ws[ k ], CHOICE_STATE );

  return argmax( ss, ACTION_SPACE );
}


int main( int argc, char *argv[] ) {

  model md;
  md.ws_len = ACTION_SPACE;
  md.st_len = CHOICE_STATE;

  double _md[ ACTION_SPACE ][ CHOICE_STATE ] = { { 0.4708550591, -0.0085735808, 1.1214000988,  1.0985257602, 0.0094695853, 0.6215058370, 0.0067630928,
                                                   0.0062859764,  0.0018550891, 0.0013285198, -0.0078833342, 0.6411701398, 0.0094695853 },
                                                 { 0.4762322598,  0.0152434686, 1.0717079730,  1.0968067869, 0.0591534762, 1.1652988746, 0.0390922789,
                                                   0.0481031272,  0.0079290925, 0.0031212565, -0.0508862352, 1.1929781536, 0.0591534762 } };

  for ( int g = 0; g < ACTION_SPACE; g++ ) {
    for ( int h = 0; h < CHOICE_STATE; h++ ) {
      md.ws[ g ][ h ] = _md[ g ][ h ];
    }
  }

  hist ht;
  klee_make_symbolic( &ht, sizeof( ht ), "history" );

  double obs[ OBS_SPACE ];
  klee_make_symbolic( obs, sizeof( obs ), "obs" );

  ///// General Environmental Constraints
  klee_assume( obs[ 0 ] == 1.0f );

  klee_assume( obs[ 3 ] == 0.0f || obs[ 3 ] == 1.0f );
  klee_assume( obs[ 4 ] == 0.0f || obs[ 4 ] == 1.0f );
  klee_assume( obs[ 5 ] == 0.0f || obs[ 5 ] == 1.0f );
  klee_assume( obs[ 3 ] == 1.0f || obs[ 4 ] == 1.0f || obs[ 5 ] == 1.0f );
  klee_assume( obs[ 3 ] != 1.0f || ( obs[ 4 ] == 0.0f && obs[ 5 ] == 0.0f ) ); // sphere ==> !box && !cylinder
  klee_assume( obs[ 4 ] != 1.0f || ( obs[ 3 ] == 0.0f && obs[ 5 ] == 0.0f ) ); // box ==> !sphere && !cylinder
  klee_assume( obs[ 5 ] != 1.0f || ( obs[ 4 ] == 0.0f && obs[ 3 ] == 0.0f ) ); // cylinder ==> !box && !sphere

  klee_assume( obs[ 6 ] == 0.0f || obs[ 6 ] == 1.0f );
  klee_assume( obs[ 6 ] != 0.0f || obs[ 7 ] == obs[ 1 ] ); // intl == 0 ==> ival == dval

  ///// Scenario Environmental Constraints
  klee_assume( 0.0f < obs[ 1 ] && obs[ 1 ] < 37.2f );
  klee_assume( obs[ 2 ] == 0.34f );
  klee_assume( obs[ 4 ] == 0.0f );
  klee_assume( obs[ 6 ] == 0.0f );

  ///// State Constraints
  klee_assume( ht.length == 120 );
  klee_assume( ht.completed == 60 );
  for ( int i = 0; i < 60; i++ ) klee_assume( ht.actions[ i ] == ( i < 20 ) );
  klee_assume( ht.ep_reward - ht.ep_cost > 20.0f );

  int dec = plan( obs, &ht, &md );

  std::cout << "Decision - " << dec << "\n";

  return 0;
}
