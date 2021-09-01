from collections import namedtuple

import z3


_cf = namedtuple( 'counterfactual', [ 'single', 'necessary', 'sufficient' ] )
_bh = namedtuple( 'behavior', [ 'necessary', 'sufficient' ] )

verification   = 0
counterfactual = _cf( single = 1, necessary = 2, sufficient = 3 )
behavior       = _bh(             necessary = 4, sufficient = 5 )
agent          = 6


def And( a, b ):
    return z3.And( a, b ) if not synthesis else None


def Or( a, b ):
    return z3.Or( a, b ) if not synthesis else None
