from soidlib import *

from .mw import declare, nothng


soid = Soid( 'nothing', verification, priority = 2 )
soid.register( declare )


@soid.register
def descriptor():
    return (
        f'\n\tquestion: When the agent observes an error, will they never just do nothing?                                      '
    )


@soid.register
def environmental( E ):
    return Equal( E.error, True )


@soid.register
def state( S ):
    return True


@soid.register
def behavior( E, S, P ):
    return Not( Equal( P.decision, nothng ) )