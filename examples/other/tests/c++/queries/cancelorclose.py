from soid.soidlib import *

from .mw import declare, cancel, dclose


soid = Soid( 'always cancel or close', verification, priority = 4 )
soid.register( declare )


@soid.register
def descriptor():
    return (
        f'\n\tquestion: When the agent observes an error, will they always try to resolve it by closing the door or by canceling'
        f'\n\t          the error?                                                                                              '
        f'\n\t                                                                                                                  '
        f'\n\t          This query helps analyze the extended counterfactual                                                    '
        f'\n\t               '
        f'( ( error {symbols.land} door open ) {symbols.counterfactual} close door ) {symbols.implies} '
        f'( ( error {symbols.land} door closed ) {symbols.counterfactual} push cancel )'
    )


@soid.register
def environmental( E ):
    return Equal( E.error, True )


@soid.register
def state( S ):
    return True


@soid.register
def behavior( D ):
    return Or( Equal( D.decision, cancel ), Equal( D.decision, dclose ) )
