from soidlib import *

from ..mw import declare, nothng


soid = Soid( 'nothing', counterfactual.sufficient, skip = True )
soid.register( declare )


@soid.register
def descriptor():
    return 'An agent was always observed in action. What conditons are sufficient for it to do nothing?'


@soid.register
def behavior( P ):
    return Equal( P.decision, nothng )
