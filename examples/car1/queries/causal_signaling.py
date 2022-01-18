from soidlib import *

from .car import declare, cardinalIDs

soid = Soid( 'causal signaling', counterfactual.single, priority = 2 )
soid.register( declare )


@soid.register
def descriptor():
    return (
        f'\n\tquestion: If we do not specify how the other car signaled, can we generate a counterfactual where the ego car does'
        f'\n\t          not enter the intersection?                                                                             ' 
    )


@soid.register
def environmental( E ):
    return And( And( Equal( E.occupied_0_0, False ) ),
                And( Equal( E.occupied_0_1, False ) ),
                And( Equal( E.occupied_0_2, False ) ),
                And( Equal( E.occupied_0_3, False ) ),
                And( Equal( E.occupied_1_0, False ) ),
                And( Equal( E.occupied_1_1, False ) ),
                And( Equal( E.occupied_1_2, False ) ),
                And( Equal( E.occupied_1_3, False ) ),
                And( Equal( E.occupied_2_0, False ) ),

                And( Equal( E.occupied_2_1,  True ), Equal( E.oriented_2_1, cardinalIDs[ 'East' ] ) ),
                
                And( Equal( E.occupied_2_2, False ) ),
                And( Equal( E.occupied_2_3, False ) ),
                And( Equal( E.occupied_3_0, False ) ),
                And( Equal( E.occupied_3_1, False ) ),
                And( Equal( E.occupied_3_2, False ) ),
                And( Equal( E.occupied_3_3, False ) )  )


@soid.register
def state( S ):
    return And( Equal( S.curr_direction,     cardinalIDs[ 'North' ] ),
                Equal( getattr( S, 'from' ), cardinalIDs[ 'South' ] ),
                Equal( S.to,                 cardinalIDs[ 'North' ] ),
                Equal( S.row,                7 ),
                Equal( S.col,                6 ),
                Equal( S.needs_turn,         False ),
                Equal( S.has_turned,         False ) )

@soid.register
def behavior( E, S, P ):
    return Equal( P.move, False )
