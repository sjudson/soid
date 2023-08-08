import soid.soidlib as soidlib

cardinalPPs = { '0' : 'North', '1' : 'East', '2' : 'South', '3' : 'West' }
cardinalIDs = { 'North' : 0, 'East' : 1, 'South' : 2, 'West' : 3 }


def introduction():
    return (
        f'\n\tcontext: A autononous vehicle has caused a broadside crash (or t-bone) by entering an intersection when it did not'
        f'\n\t         possess the right of way. We are being asked to investigate the likely cause of the crash, and to do so  '
        f'\n\t         will be asking questions of the core decision logic, which decides on high level vehicle operation -- to '
        f'\n\t         go, and if so where -- based on a reinforcement learned (so machine learned) model that we are unable to '
        f'\n\t         directly inspect. The model receives as inputs the locations, orientations, and signals of all other cars'
        f'\n\t         in the intersection. The two critical moments are diagrammed as `before-the-crash`:                      '
        f'\n\t                                                                                                                  '
        f'\n\t                    ***  |  ***                                                                                   '
        f'\n\t                    ***  |  ***                                                                                   '
        f'\n\t                   ------|------                                                                                  '
        f'\n\t         ***  *** | ***  |  *** | ***  ***                                                                        '
        f'\n\t         ----------------|----------------                                                                        '
        f'\n\t         ***  *** | c>r  |  *** | ***  ***                                                                        '
        f'\n\t                   ------|------                                                                                  '
        f'\n\t                    ***  |  e^s                                                                                   '
        f'\n\t                    ***  |  ***                                                                                   '
        f'\n\t                                                                                                                  '
        f'\n\t         and at the crash:                                                                                        '
        f'\n\t                                                                                                                  '
        f'\n\t                    ***  |  ***                                                                                   '
        f'\n\t                    ***  |  ***                                                                                   '
        f'\n\t                   ------|------                                                                                  '
        f'\n\t         ***  *** | ***  |  *** | ***  ***                                                                        '
        f'\n\t         ----------------|----------------                                                                        '
        f'\n\t         ***  *** | ***  |  cXe | ***  ***                                                                        '
        f'\n\t                   ------|------                                                                                  '
        f'\n\t                    ***  |  ***                                                                                   '
        f'\n\t                    ***  |  ***                                                                                   '
        f'\n\t                                                                                                                  '
    )


def declare():

    E = {}
    for i in range( 4 ):
        for j in range( 4 ):
            E[ f'occupied_{i}_{j}' ]    = soidlib.types.bool_as_int_bv( f'occupied_{i}_{j}',    pp = None,        raw = f'locs{i}{j}' )
            E[ f'oriented_{i}_{j}' ]    = soidlib.types.u32_bv(  f'oriented_{i}_{j}',           pp = cardinalPPs, raw = f'orients{i}{j}' )
            E[ f'leftsignal_{i}_{j}' ]  = soidlib.types.bool_as_int_bv( f'leftsignal_{i}_{j}',  pp = None,        raw = f'sigs{i}{j}0' )
            E[ f'rightsignal_{i}_{j}' ] = soidlib.types.bool_as_int_bv( f'rightsignal_{i}_{j}', pp = None,        raw = f'sigs{i}{j}1' )

    S = { 'curr_direction' : soidlib.types.u32_bv(  'curr_direction',    pp = cardinalPPs, raw = None ),
          'from'           : soidlib.types.u32_bv(  'from',              pp = cardinalPPs, raw = None ),
          'to'             : soidlib.types.u32_bv(  'to',                pp = cardinalPPs, raw = None ),
          'row'            : soidlib.types.u32_bv(  'row',               pp = None,        raw = None ),
          'col'            : soidlib.types.u32_bv(  'col',               pp = None,        raw = None ),
          'needs_turn'     : soidlib.types.bool_as_int_bv( 'needs_turn', pp = None,        raw = None ),
          'has_turned'     : soidlib.types.bool_as_int_bv( 'has_turned', pp = None,        raw = None ) }

    D = { 'new_row'  : soidlib.types.u32_bv(  'new_row',     pp = None, raw = None ),
          'new_col'  : soidlib.types.u32_bv(  'new_col',     pp = None, raw = None ),
          'move'     : soidlib.types.bool_as_int_bv( 'move', pp = None, raw = 'm' ) }

    return E, S, D
