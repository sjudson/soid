from soidlib import *

from ..mw import declare, start


soid = Soid( 'nothing', counterfactual.necessary, skip = True )
soid.register( declare )


@soid.register
def descriptor():
    return 'An agent was never observed actually pressing the start button. What conditons are necessary for it to do so?'


@soid.register
def behavior( P ):
    return Equal( P.decision, start )

