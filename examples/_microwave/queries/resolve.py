import soidlib

from .mw import declare, cancel, dclose


soid = soidlib.Soid( 'Resolve', soidlib.verification )


def descriptor():
    return 'When the agent observes an error, will they always try to resolve it? Resolution is understood as either a) closing the door, or b) pushing cancel.'


def environmental( E ):
    return soid.Equal( E.error, True )


def state( S ):
    return True


def behavior( E, S, P ):
    return soid.Or( soid.Equal( P.decision, cancel ),
                    soid.Equal( P.decision, dclose ) )


soid.register( descriptor )
soid.register( declare )
soid.register( environmental )
soid.register( state )
soid.register( behavior )
