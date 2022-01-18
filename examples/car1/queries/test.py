from soidlib import *

from .car import declare

soid = Soid( 'test', verification, priority = 1 )
soid.register( declare )


@soid.register
def descriptor():
    return (
        f'\n\tquestion: Working adaptively, so no description...                                                                '
    )


@soid.register
def environmental( E ):
    return True


@soid.register
def state( S ):
    return True


@soid.register
def behavior( E, S, P ):
    return True
