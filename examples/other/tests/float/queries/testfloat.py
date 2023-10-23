from soid.soidlib import *


def introduction():
    return f'\n\ta small test of float encodings, should fail...'


soid = Soid( 'float test', might, priority = 1 )


#@soid.register
def declare():
    E = {}
    S = { 'x' : types.double( 'x' ) }
    D = { 'y' : types.double( 'y' ) }

    return E, S, D


#@soid.register
def descriptor():
    return f'\n\ttesting...'


#@soid.register
def environmental( E ):
    return True


#@soid.register
def state( S ):
    return FP_GTE( S.x, 2.0 )


#@soid.register
def behavior( D ):
    return FP_LT( D.y, 1.0 )
