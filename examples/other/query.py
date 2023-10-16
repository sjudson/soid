import sys

import soid
import soid.soidlib as soidlib

from tests.float.queries import testfloat
from tests.cpp.queries import alwayscancel, nothing, opendoor, cancelorclose, closedoortocancel
from tests.cpp.queries.counterfactual import nevercancel
from car.queries import confirm_observations, causal_signaling, roles_swapped, in_front, away


if __name__ == '__main__':

    test = sys.argv[ 1 ]

    paths = [ '/usr/src/soid/examples/other/tests/float/src/Makefile', '/usr/src/soid/examples/other/tests/cpp/src/Makefile', '/usr/src/soid/examples/other/car/defensive/Makefile' ]

    if test == 'test.float.basic':
        idx   = 1
        base  = testfloat
        path  = paths[ 0 ]
        query = soidlib.Soid( 'Float Test Query', soidlib.counterfactual.single )
    elif test == 'test.mw.cancel':
        idx   = 1
        base  = alwayscancel
        path  = paths[ 1 ]
        query = soidlib.Soid( 'Microwave Query', soidlib.verification )
    elif test == 'test.mw.nothing':
        idx   = 2
        base  = nothing
        path  = paths[ 1 ]
        query = soidlib.Soid( 'Microwave Query', soidlib.verification )
    elif test == 'test.mw.open':
        idx   = 3
        base  = opendoor
        path  = paths[ 1 ]
        query = soidlib.Soid( 'Microwave Query', soidlib.verification )
    elif test == 'test.mw.options':
        idx   = 4
        base  = cancelorclose
        path  = paths[ 1 ]
        query = soidlib.Soid( 'Microwave Query', soidlib.verification )
    elif test == 'test.mw.close':
        idx   = 5
        base  = closedoortocancel
        path  = paths[ 1 ]
        query = soidlib.Soid( 'Microwave Query', soidlib.verification )
    elif test == 'test.mw.never':
        idx   = 6
        base  = nevercancel
        path  = paths[ 1 ]
        query = soidlib.Soid( 'Microwave Query', soidlib.counterfactual.single )
    elif test == 'test.car.confirm':
        idx   = 1
        base  = confirm_observations
        path  = paths[ 2 ]
        query = soidlib.Soid( 'Car Query', soidlib.verification )
    elif test == 'test.car.causal':
        idx   = 2
        base  = causal_signaling
        path  = paths[ 2 ]
        query = soidlib.Soid( 'Car Query', soidlib.counterfactual.single )
        query.register( base.falsified )
    elif test == 'test.car.swapped':
        idx   = 3
        base  = roles_swapped
        path  = paths[ 2 ]
        query = soidlib.Soid( 'Car Query', soidlib.counterfactual.single )
        query.register( base.falsified )
    elif test == 'test.car.front':
        idx   = 4
        base  = in_front
        path  = paths[ 2 ]
        query = soidlib.Soid( 'Car Query', soidlib.counterfactual.single )
        query.register( base.falsified )
    elif test == 'test.car.away':
        idx   = 5
        base  = away
        path  = paths[ 2 ]
        query = soidlib.Soid( 'Car Query', soidlib.counterfactual.single )
        query.register( base.falsified )

    query.register( base.declare )
    query.register( base.environmental )
    query.register( base.state )
    query.register( base.behavior )

    oracle = soid.Oracle()

    print( f'Soid Results:' )
    ( info, res, models, resources ) = soid.invoke( oracle, path, query, idx )
    print( f'Result: {res} Resources: {resources}' )
