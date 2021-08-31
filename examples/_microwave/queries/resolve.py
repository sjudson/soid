import soid

from .mw import *


def query_type():
    return soid.verification


def descriptor():
    return 'When the agent observes an error, will they always try to resolve it? Resolution is understood as either a) closing the door, or b) pushing cancel.'


def environmental( E ):
    return ( E.error == 1 )


def state( S ):
    return True


def behavior( E, S, P ):
    return Or( P.decision == cancel, P.decision == dclose )
