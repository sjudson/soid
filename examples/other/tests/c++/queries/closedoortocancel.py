from soid.soidlib import *

from .mw import declare, cancel


soid = Soid( 'close door to cancel', verification, priority = 5 )
soid.register( declare )


@soid.register
def descriptor():
    return (
        f'\n\tquestion: When the agent observes an error with the door closed, will they always try to resolve it by canceling  '
        f'\n\t          the error?                                                                                              '
        f'\n\t                                                                                                                  '
        f'\n\t          This query helps analyze the extended counterfactual                                                    '
        f'\n\t               '
        f'( ( error {symbols.land} door open ) {symbols.counterfactual} close door ) {symbols.implies} '
        f'( ( error {symbols.land} door closed ) {symbols.counterfactual} push cancel )'
    )


@soid.register
def environmental( E ):
    return And( Equal( E.error, True ), Equal( E.close, True ) )


@soid.register
def state( S ):
    return True


@soid.register
def behavior( D ):
    return Equal( D.decision, cancel )
