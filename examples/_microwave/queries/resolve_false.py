import soidlib

from .mw import declare, cancel, dclose


soid = soidlib.Soid( 'resolve.1', soidlib.verification )


def descriptor():
    return 'When the agent observes an error, will they always try to resolve it? Resolution is understood as pushing cancel.'


def environmental( E ):
    return soid.Equal( E.error, True )


def state( S ):
    return True


def behavior( E, S, P ):
    return soid.Equal( P.decision, cancel )


soid.register( descriptor )
soid.register( declare )
soid.register( environmental )
soid.register( state )
soid.register( behavior )
