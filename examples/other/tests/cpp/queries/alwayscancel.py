from soid.soidlib import *

from .mw import declare, cancel


soid = Soid( 'always cancel', would, priority = 1 )
#soid.register( declare )


#@soid.register
def descriptor():
    return (
        f'\n\tquestion: When the agent observes an error, will they always try to resolve it by canceling the error?            '
        f'\n\t                                                                                                                  '
        f'\n\t          This query is a direct formulation of our core counterfactual ( error {symbols.counterfactual} cancel ).'
    )


#@soid.register
def environmental( E ):
    return Equal( E.error, True )


#@soid.register
def state( S ):
    return True


#@soid.register
def behavior( D ):
    return Equal( D.decision, cancel )