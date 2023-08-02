#include <soidlib.h>

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <graphviz/cgraph.h>

typedef struct Node {
  double test;
  int    tidx;
  int    class;
  struct Node *tchild;
  struct Node *fchild;
} Node;


int parse_label( Node *N, Agnode_t *n ) {

  char label[ 128 ];
  strncpy( label, agget( n, "label" ), 128 );                // copy to work non-destructively

  char idx;
  char *tok, *ptok;

  tok = strtok( label, "\\n" );

  // non-leaf
  if ( strncmp( tok, "x" , 1 ) == 0 ) {
    idx = tok[ 2 ];
    N->tidx = atoi( &idx );                                  // indicies are always single digits

    tok = strtok( tok, " " );
    while( tok ) { ptok = tok; tok = strtok( NULL, " " );  } // iterate to end of test string
    N->test  = strtod( ptok, NULL );

    N->class = -1;
    return 0;
  }

  // leaf
  while ( tok ) { ptok = tok; tok = strtok( NULL, "\\n" ); } // iterate to class string
  tok = strtok( ptok, " " );
  while ( tok ) { ptok = tok; tok = strtok( NULL, " " ); }   // iterate to end of class string
  N->class = atoi( ptok );

  return 1;
}


void make_children( Agraph_t *g, Node *N, Agnode_t *n ) {

  int leaf;
  Agedge_t *el, *er;
  Agnode_t *nl, *nr;

  el = agfstedge( g, n );
  er = agnxtedge( g, el, n );

  nl = aghead( el );                                       // not sure why these are head and not tail
  nr = aghead( er );

  N->tchild = ( Node* ) malloc( sizeof( Node ) );
  leaf = parse_label( N->tchild, nl );

  if ( !leaf ) make_children( g, N->tchild, nl );

  N->fchild = ( Node* ) malloc( sizeof( Node ) );
  leaf = parse_label( N->fchild, nr );

  if ( !leaf ) make_children( g, N->fchild, nr );

  return;
}


void make_tree( Node *root ) {

  FILE *fp;
  fp = fopen( "./classifier/tree/dt.dot", "r" );

  Agraph_t *g;
  g = agread( fp , NULL );

  Agnode_t *n;
  n = agfstnode( g );

  int leaf;
  leaf = parse_label( root, n );

  if ( !leaf ) make_children( g, root, n );

  fclose( fp );
  return;
}


int traverse( Node *N, double *fv ) {
  if ( N->class >= 0 ) return N->class;
  return ( fv[ N->tidx ] <= N->test ) ? traverse( N->tchild, fv ) : traverse( N->fchild, fv );
}


int classify( Node *N, double *data ) {
  double bmi = data[ 6 ] / ( pow( data[ 5 ], 2 ) );
  double fv[ 8 ] = { data[ 0 ], data[ 1 ], data[ 2 ], data[ 3 ], data[ 4 ], bmi, data[ 7 ], data[ 8 ] };

  return traverse( N, fv );
}


int main( int argc, char **argv ) {

  Node *root = ( Node* ) malloc( sizeof( Node ) );
  make_tree( root );

  double data[ 9 ];
  int cls, __soid__cls;

  //double data[ 9 ] = { 1.0, 199.0, 76.0, 43.0, 0.0, 54.0, 249.973, 1.394, 22.0 };
  klee_make_symbolic( &data[ 0 ], sizeof( data[ 0 ] ), "data0" );
  klee_assume( data[ 0 ] == 1.0 );

  klee_make_symbolic( &data[ 1 ], sizeof( data[ 1 ] ), "data1" );
  klee_assume( data[ 1 ] == 199.0 );

  klee_make_symbolic( &data[ 2 ], sizeof( data[ 2 ] ), "data2" );
  klee_assume( data[ 2 ] == 76.0 );

  klee_make_symbolic( &data[ 3 ], sizeof( data[ 3 ] ), "data3" );
  klee_assume( data[ 3 ] == 43.0 );

  klee_make_symbolic( &data[ 4 ], sizeof( data[ 4 ] ), "data4" );
  klee_assume( data[ 4 ] == 0.0 );

  klee_make_symbolic( &data[ 5 ], sizeof( data[ 5 ] ), "data5" );
  klee_assume( data[ 5 ] == 54.0 );

  klee_make_symbolic( &data[ 6 ], sizeof( data[ 6 ] ), "data6" );
  klee_assume( data[ 6 ] == 249.973 );

  klee_make_symbolic( &data[ 7 ], sizeof( data[ 7 ] ), "data7" );
  klee_assume( data[ 7 ] == 1.394 );

  klee_make_symbolic( &data[ 8 ], sizeof( data[ 8 ] ), "data8" );
  klee_assume( data[ 8 ] == 22.0 );

  klee_make_symbolic( &__soid__cls, sizeof( __soid__cls ), "__soid__cls" );

  cls = classify( root, data );

  klee_assume( cls == __soid__cls );

  //const char *clss[ 2 ] = { "FALSE", "TRUE" };
  //printf( "Test Instance classified to %s\n", clss[ cls ] );

  return 0;
}
