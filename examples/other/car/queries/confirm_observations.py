from soid.soidlib import *

from .car import declare, cardinalIDs

soid = Soid( 'confirm observations', verification, priority = 1 )
#soid.register( declare )


#@soid.register
def descriptor():
    return (
        f'\n\tquestion: Did the core logic decide on the action that was observed, or are we looking in the wrong place?        '
    )


#@soid.register
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

                And( Equal( E.occupied_2_1,  True ), Equal( E.oriented_2_1, cardinalIDs[ 'East' ] ), Equal( E.leftsignal_2_1, False ), Equal( E.rightsignal_2_1, True ) ),

                And( Equal( E.occupied_2_2, False ) ),
                And( Equal( E.occupied_2_3, False ) ),
                And( Equal( E.occupied_3_0, False ) ),
                And( Equal( E.occupied_3_1, False ) ),
                And( Equal( E.occupied_3_2, False ) ),
                And( Equal( E.occupied_3_3, False ) )  )


#@soid.register
def state( S ):
    return And( Equal( S.curr_direction,     cardinalIDs[ 'North' ] ),
                Equal( getattr( S, 'from' ), cardinalIDs[ 'South' ] ),
                Equal( S.to,                 cardinalIDs[ 'North' ] ),
                Equal( S.row,                7 ),
                Equal( S.col,                6 ),
                Equal( S.needs_turn,         False ),
                Equal( S.has_turned,         False ) )


#@soid.register
def behavior( D ):
    return Equal( D.move, True )
