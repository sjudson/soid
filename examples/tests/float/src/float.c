#include "soidlib.h"

#include <stdlib.h>
#include <stdio.h>

double clamp( double x ) {
  return ( x >= 1.0 ) ? 1.0 : x;
}

int main( int argc, char *argv[] ) {

  double x;
  double y, __soid__y;

  klee_make_symbolic( &x, sizeof( x ), "x" );

  klee_assume( x > 2.0 );

  klee_make_symbolic( &__soid__y, sizeof( __soid__y ), "__soid__y" );

  y = clamp( x );

  klee_assume( y == __soid__y );

  return 0;
}
