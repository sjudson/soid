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


void parse_label( Node *n, char *label ) {

  printf("%s\n", label);

  char *tok, *ptok;

  tok = strtok( label, "\n" );

  // non-leaf
  if ( strncmp( tok, "x" , 1 ) == 0 ) {
    tok = strtok( tok, " " );
    n->tidx = atoi( tok[ 2 ] );                              // indicies are always single digits

    while( tok ) { ptok = tok; tok = strtok( NULL, " " ); }  // iterate to end of test string
    n->test = strtod( ptok );

    return;
  }

  // leaf
  while ( tok ) { ptok = tok; tok = strtok( NULL, "\n" ); } // iterate to class string
  tok = strtok( ptok, " " );
  while( tok ) { ptok = tok; tok = strtok( NULL, " " ); }   // iterate to end of class string
  n->class = atoi( ptok );

  return;
}


void make_tree( Node *root ) {

  FILE *fp;
  fp = fopen( "./classifier/tree/dt.dot", "r" );

  Agraph_t *g;
  g = agread( fp , NULL );

  Agnode_t *n;
  Agedge_t *e;

  n = agfstnode( g );

  root = ( Node* ) malloc( sizeof( Node ) );
  parse_label( root, agget( n, "label" ) );

  for ( n = agfstnode( g ); n; n = agnxtnode( g, n ) ) {
    for ( e = agfstout( g, n ); e; e = agnxtout( g, e ) ) {
      /* do something with e */
    }
  }

  fclose( fp );
  return;
}


int main( int argc, char **argv ) {

  Node *root;
  make_tree( root );

  return 0;
}
