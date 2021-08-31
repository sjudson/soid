import soid

from mw import *


@soid.query_type
def query_type():
    return soid.counterfactual.sufficient


@soid.descriptor
def descriptor():
    return 'An agent was always observed in action. What conditons are sufficient for it to do nothing?'


@soid.behavior
def behavior( E, S, P ):
    return ( P.decision == nothng )
