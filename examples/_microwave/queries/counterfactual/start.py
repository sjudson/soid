import soidlib

from ..mw import declare, start


soid = soidlib.Soid( 'nothing', soidlib.counterfactual.necessary )


def descriptor():
    return 'An agent was never observed actually pressing the start button. What conditons are necessary for it to do so?'


def behavior( P ):
    return soid.Equal( P.decision, start )


soid.register( descriptor )
soid.register( declare )
soid.register( behavior )
