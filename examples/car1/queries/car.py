import soidlib


def introduction():
    return "\n\nWorking adaptively, so no intro...\n"


def declare():

    cardinals = { 0 : 'North', 1 : 'East', 2 : 'South', 3 : 'West' }

    E = {}
    for i in range( 3 ):
        for j in range( 3 ):
            E[ f'occupied_{i}_{j}' ]    = soidlib.types.bool_bv( f'occupied_{i}_{j}',    pp = None,      raw = f'locs{i}{j}' )
            E[ f'oriented_{i}_{j}' ]    = soidlib.types.u32_bv(  f'oriented_{i}_{j}',    pp = cardinals, raw = f'orients{i}{j}' )
            E[ f'leftsignal_{i}_{j}' ]  = soidlib.types.bool_bv( f'leftsignal_{i}_{j}',  pp = None,      raw = f'sigs{i}{j}0' )
            E[ f'rightsignal_{i}_{j}' ] = soidlib.types.bool_bv( f'rightsignal_{i}_{j}', pp = None,      raw = f'sigs{i}{j}1' )

    S = { 'curr_direction' : soidlib.types.u32_bv(  'curr_direction', pp = cardinals, raw = None ),
          'from'           : soidlib.types.u32_bv(  'from',           pp = cardinals, raw = None ),
          'to'             : soidlib.types.u32_bv(  'to',             pp = cardinals, raw = None ),
          'row'            : soidlib.types.u32_bv(  'row',            pp = None,      raw = None ),
          'col'            : soidlib.types.u32_bv(  'col',            pp = None,      raw = None ),
          'needs_turn'     : soidlib.types.bool_bv( 'needs_turn',     pp = None,      raw = None ),
          'has_turned'     : soidlib.types.bool_bv( 'has_turned',     pp = None,      raw = None ) }

    P = { 'new_row'  : soidlib.types.u32_bv(  'new_row',   pp = None, raw = None ),
          'new_col'  : soidlib.types.u32_bv(  'new_col',   pp = None, raw = None ),
          'move'     : soidlib.types.bool_bv( 'move',      pp = None, raw = 'm' ) }

    return E, S, P
