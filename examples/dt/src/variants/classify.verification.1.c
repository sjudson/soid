#include "../tree.h"

#include <math.h>
#include <stdlib.h>
#include <string.h>

#include <soidlib.h>


int traverse( Node *N, double *fv ) {
  if ( N->class >= 0 ) return N->class;
  return ( fv[ N->tidx ] <= N->test ) ? traverse( N->tchild, fv ) : traverse( N->fchild, fv );
}


int classify( Node *root, double *data ) {
  double bmi = data[ 6 ] / ( pow( data[ 5 ], 2 ) );
  double fv[ 8 ] = { data[ 0 ], data[ 1 ], data[ 2 ], data[ 3 ], data[ 4 ], bmi, data[ 7 ], data[ 8 ] };

  return traverse( root, fv );
}


int main ( int argc, char **argv ) {

  double data[ 9 ];
  int cls, __soid__cls;

  Node *root = ( Node* ) malloc( sizeof( Node ) );;
  tree( root );

  double data0;
  klee_make_symbolic( &data0, sizeof( double ), "data0" );
  klee_assume( data0 == 1.0 );
  memcpy( data + 0, &data0, sizeof( double ) );

  double data1;
  klee_make_symbolic( &data1, sizeof( double ), "data1" );
  klee_assume( data1 == 199.0 );
  memcpy( data + 1, &data1, sizeof( double ) );

  double data2;
  klee_make_symbolic( &data2, sizeof( double ), "data2" );
  klee_assume( data2 == 76.0 );
  memcpy( data + 2, &data2, sizeof( double ) );

  double data3;
  klee_make_symbolic( &data3, sizeof( double ), "data3" );
  klee_assume( data3 == 43.0 );
  memcpy( data + 3, &data0, sizeof( double ) );

  double data4;
  klee_make_symbolic( &data4, sizeof( double ), "data4" );
  klee_assume( data4 == 0.0 );
  memcpy( data + 4, &data4, sizeof( double ) );

  double data5;
  klee_make_symbolic( &data5, sizeof( double ), "data5" );
  klee_assume( data5 == 54.0 );
  memcpy( data + 5, &data5, sizeof( double ) );

  double data6;
  klee_make_symbolic( &data6, sizeof( double ), "data6" );
  klee_assume( data6 == 249.973 );
  memcpy( data + 6, &data6, sizeof( double ) );

  double data7;
  klee_make_symbolic( &data7, sizeof( double ), "data7" );
  klee_assume( data7 == 1.394 );
  memcpy( data + 7, &data7, sizeof( double ) );

  double data8;
  klee_make_symbolic( &data8, sizeof( double ), "data8" );
  klee_assume( data8 == 22.0 );
  memcpy( data + 8, &data8, sizeof( double ) );

  klee_make_symbolic( &__soid__cls, sizeof( __soid__cls ), "__soid__cls" );

  cls = classify( root, data );

  klee_assume( cls == __soid__cls );

  return 0;
}
