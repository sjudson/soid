from soid.soidlib import *

from .mw import declare, nothng


soid = Soid( 'nothing', verification, priority = 2 )
soid.register( declare )


@soid.register
def descriptor():
    return (
        f'\n\tquestion: When the agent observes an error, will they always do something (i.e., never do nothing)?               '
    )


@soid.register
def environmental( E ):
    return Equal( E.error, True )


@soid.register
def state( S ):
    return True


@soid.register
def behavior( D ):
    return Not( Equal( D.decision, nothng ) )
