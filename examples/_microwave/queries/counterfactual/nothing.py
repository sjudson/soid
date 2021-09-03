import soidlib

from ..mw import declare, nothng


soid = soidlib.Soid( 'nothing', soidlib.counterfactual.sufficient )


def descriptor():
    return 'An agent was always observed in action. What conditons are sufficient for it to do nothing?'


def behavior( P ):
    return soid.Equal( P.decision, nothng )


soid.register( descriptor )
soid.register( declare )
soid.register( behavior )
