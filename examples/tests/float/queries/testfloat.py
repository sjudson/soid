from soidlib import *


def introduction():
    return f'\n\ta small test of float encodings, should fail...'


soid = Soid( 'float test', counterfactual.single, priority = 1 )


@soid.register
def declare():
    E = {}
    S = { 'x' : types.double( 'x' ) }
    P = { 'y' : types.double( 'y' ) }

    return E, S, P


@soid.register
def descriptor():
    return f'\n\ttesting...'


@soid.register
def environmental( E ):
    return True


@soid.register
def state( S ):
    return FP_GTE( S.x, 2.0 )


@soid.register
def behavior( P ):
    return FP_LT( P.y, 1.0 )
