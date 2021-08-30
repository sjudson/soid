import soid


start  = 0
cancel = 1
dopen  = 2
dclose = 3
nothng = 4


@soid.environmental
def environmental( E ):
    return ( E.error == 1 )


@soid.state
def state( S ):
    return True


@soid.behavior
def behavior( E, S, P )
    return Or( P.decision == cancel, P.decision == dclose )


@soid.constrain
def constrain():

    E = soid.E( { 'error' : 'bool' } )
    S = None
    P = soid.P( { 'decision' : 'bool' } )
