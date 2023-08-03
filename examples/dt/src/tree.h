#pragma once

typedef struct Node {
  double test;
  int    tidx;
  int    class;
  struct Node *tchild;
  struct Node *fchild;
} Node;

void tree( Node* root );
