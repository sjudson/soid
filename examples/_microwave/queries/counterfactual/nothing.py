import soid

from ..mw import *


def query_type():
    return soid.counterfactual.sufficient


def descriptor():
    return 'An agent was always observed in action. What conditons are sufficient for it to do nothing?'


def behavior( E, S, P ):
    return ( P.decision == nothng )
