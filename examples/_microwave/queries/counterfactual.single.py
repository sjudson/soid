import soid

from mw import *


@soid.query_type
def query_type():
    return soid.counterfactual.single


@soid.descriptor
def descriptor():
    return 'An agent was observed closing a door while the microwave was in error. Is there an alternative scenario where the agent instead pushes cancel upon the erroring after start?'


@soid.environmental
def environmental( E ):
    obs = And( E.error == 1, And( E.close == 0, And( E.heat == 0, E.start == 1 ) ) )
    qry = And( E.error == 1, E.start == 1)
    return qry, obs


@soid.state
def state( S ):
    obs = ( S.started == 1 )
    qry = True
    return qry, obs


@soid.behavior
def behavior( E, S, P ):
    return ( P.decision == cancel )
