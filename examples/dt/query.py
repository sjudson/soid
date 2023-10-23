import sys

import soid
import soid.soidlib as soidlib

from queries import verify, weight

if __name__ == '__main__':

    test = sys.argv[ 1 ]

    if test == 'verify':
        idx   = 1
        base  = verify
        query = soidlib.Soid( 'Decision Tree Query', soidlib.would )
    else:
        idx   = 2
        base  = weight
        query = soidlib.Soid( 'Decision Tree Query', soidlib.might )
        query.register( base.falsified )

    query.register( base.declare )
    query.register( base.environmental )
    query.register( base.state )
    query.register( base.behavior )

    oracle = soid.Oracle()

    print( f'Soid Results:' )
    ( info, res, models, resources ) = soid.invoke( oracle, '/usr/src/soid/examples/dt/src/Makefile', query, idx )
    print( f'Result: {res} Resources: {resources}' )
