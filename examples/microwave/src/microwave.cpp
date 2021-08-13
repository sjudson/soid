#include "klee.h"
#include <assert.h>

#include <iostream>
#include <iomanip>
#include <string>
#include <cstdio>

#define pushStart 0
#define pushCancel 1
#define openDoor 2
#define closeDoor 3
#define doNothing 4

uint8_t decide( bool *started, bool start, bool close, bool heat, bool error ) {

  // always close the door if it's open, either to fix error or after getting food
  if ( !close ) { return closeDoor; }

  // otherwise, on error push the cancel button
  if (  error ) { return pushCancel; }

  // if no error, it's closed, and it's running, just wait
  if (  start ) { return doNothing; }

  // if it's not running, if we've already started it then open it to remove food
  if ( *started ) {
    *started = 0;
    return openDoor;
  }

  // otherwise, press start
  *started = 1;
  return pushStart;
}

int main( int argc, char *argv[] ) {

  bool started, start, close, heat, error;
  uint32_t dec;
  klee_make_symbolic( &started, sizeof( started ), "started" );
  klee_make_symbolic( &start, sizeof( start ), "start" );
  klee_make_symbolic( &close, sizeof( close ), "close" );
  klee_make_symbolic( &heat, sizeof( heat ), "heat" );
  klee_make_symbolic( &error, sizeof( error ), "error" );

  dec = decide( &started, start, close, heat, error );

  std::cout << "Decision - " << dec << "\n";

  return 0;
}
