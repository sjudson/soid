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

  int leaf;
  Agnode_t *n;
  Agedge_t *l, *r;

  n = agfstnode( g );

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

  double data[ 9 ] = { 1.0, 199.0, 76.0, 43.0, 0.0, 54.0, 249.973, 1.394, 22.0 };

  int cls = classify( root, data );
  const char *clss[ 2 ] = { "FALSE", "TRUE" };

  printf( "Test Instance classified to %s\n", clss[ cls ] );

  return 0;
}
