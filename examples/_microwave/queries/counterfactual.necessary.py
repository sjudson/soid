import soid

from mw import *


@soid.query_type
def query_type():
    return soid.counterfactual.necessary


@soid.descriptor
def descriptor():
    return 'An agent was never observed actually pressing the start button. What conditons are necessary for it to do so?'


@soid.behavior
def behavior( E, S, P ):
    return ( P.decision == start )
