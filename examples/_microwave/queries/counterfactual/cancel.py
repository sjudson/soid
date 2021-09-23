import soidlib

from ..mw import declare, cancel


soid = soidlib.Soid( 'cancel', soidlib.soidlib.counterfactual.single )


def descriptor():
    return 'An agent was observed closing a door while the microwave was in error. Is there an alternative scenario where the agent instead pushes cancel upon the erroring after start?'


def environmental( E ):
    obs = soid.And( soid.Equal( E.error, True ),
                    soid.Equal( E.close, False ),
                    soid.Equal( E.heat,  False ),
                    soid.Equal( E.start, True ) )

    qry = soid.And( soid.Equal( E.error, True ),
                    soid.Equal( E.start, True ) )

    return qry, obs


def state( S ):
    obs = soid.Equal( S.started, True )

    qry = True

    return qry, obs


def behavior( P ):
    return soid.Equal( P.decision, cancel )


soid.register( descriptor )
soid.register( declare )
soid.register( environmental )
soid.register( state )
soid.register( behavior )
