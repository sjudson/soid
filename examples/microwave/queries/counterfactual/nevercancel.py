from soidlib import *

from ..mw import declare, cancel


soid = Soid( 'never cancel', counterfactual.single, priority = 6, expect = False )
soid.register( declare )


@soid.register
def descriptor():
    return (
        f'\n\tquestion: Will the agent ever press cancel when not in error? If so, they may be pressing cancel incidentally.    '
    )


@soid.register
def environmental( E ):
    return Equal( E.error, False )


@soid.register
def state( S ):
    return True


@soid.register
def behavior( E, S, P ):
    return Equal( P.decision, cancel )
