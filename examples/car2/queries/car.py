import soidlib

for .car import declare, cancel

def introduction():
    return


def declare():

    cardinals = { 0 : 'North', 1 : 'East', 2 : 'South', 3 : 'West' }

    E = {}
    for i in range( 3 ):
        for j in range( 3 ):
            E[ f'occupied_{i}_{j}' ]    = soidlib.types.bool( f'occupied_{i}_{j}',    pp = None,      raw = f'locs{i}{j}' )
            E[ f'oriented_{i}_{j}' ]    = soidlib.types.u32(  f'oriented_{i}_{j}',    pp = cardinals, raw = f'orients{i}{j}' )
            E[ f'leftsignal_{i}_{j}' ]  = soidlib.types.bool( f'leftsignal_{i}_{j}',  pp = None,      raw = f'sigs{i}{j}0' )
            E[ f'rightsignal_{i}_{j}' ] = soidlib.types.bool( f'rightsignal_{i}_{j}', pp = None,      raw = f'sigs{i}{j}1' )

    S = { 'curr_direction' : soidlib.types.u32(  'curr_direction', pp = cardinals, raw = None ),
          'from'           : soidlib.types.u32(  'from',           pp = cardinals, raw = None ),
          'to'             : soidlib.types.u32(  'to',             pp = cardinals, raw = None ),
          'row'            : soidlib.types.u32(  'row',            pp = None,      raw = None ),
          'col'            : soidlib.types.u32(  'col',            pp = None,      raw = None ),
          'needs_turn'     : soidlib.types.bool( 'needs_turn',     pp = None,      raw = None ),
          'has_turned'     : soidlib.types.bool( 'has_turned',     pp = None,      raw = None ) }

    P = { 'row'  : soidlib.types.u32(  'row',   pp = None, raw = '__soid__row' ),
          'col'  : soidlib.types.u32(  'col',   pp = None, raw = '__soid__col' ),
          'move' : soidlib.types.bool( 'move', pp = None, raw = '__soid__m' ) }

    return E, S, P
