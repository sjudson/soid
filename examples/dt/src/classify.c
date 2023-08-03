#include "tree.h"

#include <math.h>
#include <stdlib.h>
#include <string.h>

#ifdef symbolic
#include <soidlib.h>
#endif

#ifdef run
#include <stdio.h>
#include <graphviz/cgraph.h>


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


void write_header( FILE *fpo ) {
  fprintf( fpo, "#include \"tree.h\"\n\n#include <stdlib.h>\n\nvoid tree( Node *root ) {\n\n" );
  return;
}


void write_node( FILE *fpo, Node *N, int is_root ) {

  if ( is_root ) {

    fprintf( fpo, "\troot->test = %f;\n", N->test );
    fprintf( fpo, "\troot->tidx = %d;\n", N->tidx );
    fprintf( fpo, "\troot->class = %d;\n", N->class );

    if ( N->class == -1 ) {
      fprintf( fpo, "\troot->tchild = x%llx;\n", ( unsigned long long int ) N->tchild );
      fprintf( fpo, "\troot->fchild = x%llx;\n", ( unsigned long long int ) N->fchild );
    }

    fprintf( fpo, "\n" );

    return;
  }

  // use pointer address as unique identifier
  fprintf( fpo, "\tNode *x%llx = ( Node* ) malloc( sizeof( Node ) );\n", ( unsigned long long int ) N );
  fprintf( fpo, "\tx%llx->test = %f;\n", ( unsigned long long int ) N, N->test );
  fprintf( fpo, "\tx%llx->tidx = %d;\n", ( unsigned long long int ) N, N->tidx );
  fprintf( fpo, "\tx%llx->class = %d;\n", ( unsigned long long int ) N, N->class );

  if ( N->class == -1 ) {
    fprintf( fpo, "\tx%llx->tchild = x%llx;\n", ( unsigned long long int ) N, ( unsigned long long int ) N->tchild );
    fprintf( fpo, "\tx%llx->fchild = x%llx;\n", ( unsigned long long int ) N, ( unsigned long long int ) N->fchild );
  }

  fprintf( fpo, "\n" );
  return;
}


void write_footer( FILE *fpo, Node *root ) {
  fprintf( fpo, "\treturn;\n}" );
  return;
}


void make_children( Agraph_t *g, Node *N, Agnode_t *n, int is_root, FILE *fpo ) {

  int leaf;
  Agedge_t *el, *er;
  Agnode_t *nl, *nr;

  el = agfstedge( g, n );
  er = agnxtedge( g, el, n );

  nl = aghead( el );                                       // not sure why these are head and not tail
  nr = aghead( er );

  N->tchild = ( Node* ) malloc( sizeof( Node ) );
  leaf = parse_label( N->tchild, nl );

  if ( !leaf ) {
    make_children( g, N->tchild, nl, 0, fpo );
  } else {
    write_node( fpo, N->tchild, 0 );
  }

  N->fchild = ( Node* ) malloc( sizeof( Node ) );
  leaf = parse_label( N->fchild, nr );

  if ( !leaf ) {
    make_children( g, N->fchild, nr, 0, fpo );
  } else {
    write_node( fpo, N->fchild, 0 );
  }

  write_node( fpo, N, is_root );

  return;
}


void make_tree( Node *root ) {

  FILE *fpi;
  fpi = fopen( "./classifier/tree/dt.dot", "r" );

  Agraph_t *g;
  g = agread( fpi, NULL );

  Agnode_t *n;

  n = agfstnode( g );

  int leaf;
  leaf = parse_label( root, n );

  FILE *fpo;
  fpo = fopen( "./tree.c", "w" );

  write_header( fpo );

  if ( !leaf ) make_children( g, root, n, 1, fpo );

  write_footer( fpo, root );

  fclose( fpi );
  fclose( fpo );
  return;
}
#endif


int traverse( Node *N, double *fv ) {
  if ( N->class >= 0 ) return N->class;
  return ( fv[ N->tidx ] <= N->test ) ? traverse( N->tchild, fv ) : traverse( N->fchild, fv );
}


int classify( Node *root, double *data ) {
  double bmi = data[ 6 ] / ( pow( data[ 5 ], 2 ) );
  double fv[ 8 ] = { data[ 0 ], data[ 1 ], data[ 2 ], data[ 3 ], data[ 4 ], bmi, data[ 7 ], data[ 8 ] };

  return traverse( root, fv );
}


#ifdef run

int main( int argc, char **argv ) {

  Node *root = ( Node* ) malloc( sizeof( Node ) );
  make_tree( root );

  double data[ 9 ] = { 1.0, 199.0, 76.0, 43.0, 0.0, 54.0, 249.973, 1.394, 22.0 };
  int cls = classify( root, data );

  const char *clss[ 2 ] = { "FALSE", "TRUE" };
  printf( "Test Instance classified to %s\n", clss[ cls ] );

  return 0;
}

#endif
#ifdef symbolic

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

#endif
