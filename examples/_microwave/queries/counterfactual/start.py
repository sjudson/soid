import soidlib

from ..mw import *


def query_type():
    return soidlib.counterfactual.necessary


def descriptor():
    return 'An agent was never observed actually pressing the start button. What conditons are necessary for it to do so?'


def behavior( E, S, P ):
    return ( P.decision == start )
