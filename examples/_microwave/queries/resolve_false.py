from soidlib import *

from .mw import declare, cancel, dclose


soid = Soid( 'resolve.1', verification, priority = 1 )
soid.register( declare )


@soid.register
def descriptor():
    return 'When the agent observes an error, will they always try to resolve it? Resolution is understood as pushing cancel.'


@soid.register
def environmental( E ):
    return Equal( E.error, True )


@soid.register
def state( S ):
    return True


@soid.register
def behavior( E, S, P ):
    return Equal( P.decision, cancel )
