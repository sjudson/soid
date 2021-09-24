from soidlib import *

from ..mw import declare, cancel

soid = Soid( 'cancel', counterfactual.single, priority = 3 )
soid.register( declare )


@soid.register
def descriptor():
    return 'An agent was observed closing a door while the microwave was in error. Is there an alternative scenario where the agent instead pushes cancel upon the erroring after start?'


@soid.register
def environmental( E ):
    obs = And( Equal( E.error, True ),
               Equal( E.close, False ),
               Equal( E.heat,  False ),
               Equal( E.start, True ) )

    qry = And( Equal( E.error, True ),
               Equal( E.start, True ) )

    return qry, obs


@soid.register
def state( S ):
    obs = Equal( S.started, True )

    qry = True

    return qry, obs


@soid.register
def behavior( P ):
    return Equal( P.decision, cancel )
