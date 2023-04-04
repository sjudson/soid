from soidlib import *

from .car import declare, cardinalIDs

soid = Soid( 'away', verification, priority = 5 )
soid.register( declare )


@soid.register
def descriptor():
    return (
        f'\n\tquestion: Lastly we consider if the two cars arrive contemporaneously, without a clear right of way for either.   '
        f'\n\t                                                                                                                  '
        f'\n\t                    ***  |  ***                                                                                   '
        f'\n\t                    ***  |  ***                                                                                   '
        f'\n\t                   ------|------                                                                                  '
        f'\n\t         ***  *** | ***  |  *** | ***  ***                                                                        '
        f'\n\t         ----------------|----------------                                                                        '
        f'\n\t         ***  c>? | ***  |  *** | ***  ***                                                                        '
        f'\n\t                   ------|------                                                                                  '
        f'\n\t                    ***  |  e^s                                                                                   '
        f'\n\t                    ***  |  ***                                                                                   '
        f'\n\t                                                                                                                  '

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

                And( Equal( E.occupied_2_0,  True ), Equal( E.oriented_2_0, cardinalIDs[ 'East' ] ) ),

                And( Equal( E.occupied_2_1, False ) ),
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
def falsified( E, S ):
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
                And( Equal( E.occupied_3_3, False ) ),
                And( Equal( S.curr_direction,     cardinalIDs[ 'North' ] ),
                     Equal( getattr( S, 'from' ), cardinalIDs[ 'South' ] ),
                     Equal( S.to,                 cardinalIDs[ 'North' ] ),
                     Equal( S.row,                7 ),
                     Equal( S.col,                6 ),
                     Equal( S.needs_turn,         False ),
                     Equal( S.has_turned,         False ) ) )


@soid.register
def behavior( D ):
    return Equal( D.move, True )
