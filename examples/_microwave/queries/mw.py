import soidlib

start  = 0
cancel = 1
dopen  = 2
dclose = 3
nothng = 4

def declare():

    E = { 'error'    : soidlib.types.bool( 'error' ),
          'close'    : soidlib.types.bool( 'close' ),
          'heat'     : soidlib.types.bool( 'heat'  ),
          'start'    : soidlib.types.bool( 'start' ) }
    
    S = { 'started'  : soidlib.types.bool( 'started' ) }
    
    P = { 'decision' : soidlib.types.u32( 'decision' ) }

    return E, S, P
