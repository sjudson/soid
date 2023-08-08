import sys

import soid
import soid.soidlib as soidlib

from queries import verify, weight

if __name__ == '__main__':

    test = sys.argv[ 1 ]

    if test == 'verify':
        base  = verify
        query = soidlib.Soid( 'Decision Tree Query', soidlib.verification )
    else:
        base  = weight
        query = soidlib.Soid( 'Decision Tree Query', soidlib.counterfactual.single )
        query.falsified( base.falsified )

    query.register( base.declare )
    query.environmental( base.environmental )
    query.state( base.state )
    query.behavior( base.behavior )

    oracle = soid.Oracle()

    print( f'Soid Results:' )
    ( info, res, models, resources ) = soid.invoke( oracle, '/usr/src/soid/examples/dt/src/Makefile', query )
    print( f'Result: {res} Resources: {resources}' )
