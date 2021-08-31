import soid

from mw import *


@soid.query_type
def query_type():
    return soid.verification


@soid.descriptor
def descriptor():
    return 'When the agent observes an error, will they always try to resolve it? Resolution is understood as either a) closing the door, or b) pushing cancel.'


@soid.environmental
def environmental( E ):
    return ( E.error == 1 )


@soid.state
def state( S ):
    return True


@soid.behavior
def behavior( E, S, P )
    return Or( P.decision == cancel, P.decision == dclose )
