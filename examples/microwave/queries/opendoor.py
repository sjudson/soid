from soidlib import *

from .mw import declare, dopen


soid = Soid( 'open door', verification, priority = 3 )
soid.register( declare )


@soid.register
def descriptor():
    return (
        f'\n\tquestion: When the agent observes an error, will they never open the door?                                         '
    )


@soid.register
def environmental( E ):
    return Equal( E.error, True )


@soid.register
def state( S ):
    return True


@soid.register
def behavior( E, S, P ):
    return Not( Equal( P.decision, dopen ) )
