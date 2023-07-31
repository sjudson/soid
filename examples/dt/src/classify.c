#include <stdio.h>
#include <stdlib.h>
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
    N->test = strtod( ptok, NULL );

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

  root = ( Node* ) malloc( sizeof( Node ) );
  leaf = parse_label( root, n );

  if ( !leaf ) make_children( g, root, n );

  fclose( fp );
  return;
}


int main( int argc, char **argv ) {

  Node *root;
  make_tree( root );

  return 0;
}
