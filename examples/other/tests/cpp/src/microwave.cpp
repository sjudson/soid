#include "soidlib.h"

#include <cstdint>


#define pushStart 0
#define pushCancel 1
#define openDoor 2
#define closeDoor 3
#define doNothing 4


uint8_t decide( bool *started, bool start, bool close, bool heat, bool error ) {

  // always close the door if it's open and the heat is on
  if ( !close && heat ) { return closeDoor; }

  // otherwise try to solve the error by pushing cancel
  if (  error ) { return pushCancel; }

  // otherwise, if open then close the door after getting food
  if ( !close ) { return closeDoor; }

  // if no error, it's closed, and it's running, just wait
  if (  start ) { return doNothing; }

  // if it's not running, if we've already started it then open it to remove food
  if ( *started ) {
    *started = false;
    return openDoor;
  }

  // otherwise, press start
  *started = true;
  return pushStart;
}


int main( int argc, char *argv[] ) {

  bool started, start, close, heat, error;
  uint32_t decision, __soid__decision;

  klee_make_symbolic( &started, sizeof( started ), "started" );
  klee_make_symbolic( &start,   sizeof( start ),   "start"   );
  klee_make_symbolic( &close,   sizeof( close ),   "close"   );
  klee_make_symbolic( &heat,    sizeof( heat ),    "heat"    );
  klee_make_symbolic( &error,   sizeof( error ),   "error"   );

  klee_make_symbolic( &__soid__decision, sizeof( __soid__decision ), "__soid__decision" );

  decision = decide( &started, start, close, heat, error );

  klee_assume( decision == __soid__decision );

  return 0;
}
