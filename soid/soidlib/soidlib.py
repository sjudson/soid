from collections import namedtuple

import z3
import inspect



########################
##### QUERY TYPES ######
########################



_cf = namedtuple( 'counterfactual', [ 'single', 'necessary', 'sufficient' ] )
_bh = namedtuple( 'behavior', [ 'necessary', 'sufficient' ] )

verification   = 0
counterfactual = _cf( single = 1, necessary = 2, sufficient = 3 )
behavior       = _bh(             necessary = 4, sufficient = 5 )
agent          = 6



######################
##### VAR TYPES ######
######################



def bv32arr( x ):
    return z3.Array( x, z3.BitVecSort( 32 ), z3.BitVecSort( 8 ) )


def cint_to_bv32( x ):
    return z3.BitVecVal( 1 * x, 32 )   # implicit bool conversion


def cbool_to_bv32( x ):
    return cint_to_bv32( x )


def bv32arr_to_bv32( x ):
    return z3.Concat( z3.Select( x, z3.BitVecVal( 3, 32 ) ),
                      z3.Select( x, z3.BitVecVal( 2, 32 ) ),
                      z3.Select( x, z3.BitVecVal( 1, 32 ) ),
                      z3.Select( x, z3.BitVecVal( 0, 32 ) ) )


def _bv32( v ):
    if isinstance( v, str ):                             # if given a name then create a new array-based variable
        return bv32arr( v )
    elif isinstance( v, bool ) or isinstance( v, int ):  # otherwise treat as a constant
        return cint_to_bv32( v )
    else:
        pass # todo: handle


_tyu   = namedtuple( 'tyutil', [ 'bv32arr', 'int_to_bv32', 'bool_to_bv32', 'bv32arr_to_bv32' ] )
tyutil = _tyu( bv32arr = bv32arr, int_to_bv32 = cint_to_bv32, bool_to_bv32 = cbool_to_bv32, bv32arr_to_bv32 = bv32arr_to_bv32 )

_ty    = namedtuple( 'types', [ 'bool', 'int', 'u32', 'util' ] )
types  = _ty( bool = _bv32, int = _bv32, u32 = _bv32, util = tyutil )



####################
##### CORE API #####
####################



class Soid():

    def __init__( self, qn, qt ):

        self.__name  = qn
        self.__type  = qt
        self.__synth = ( qt not in [ verification, counterfactual.single ] )

        self.__regmap = {
            'descriptor'    : self.__reg_desc,
            'declare'       : self.__reg_decl,
            'environmental' : self.__reg_env,
            'state'         : self.__reg_st,
            'behavior'      : self.__reg_bhv,
        }


    def __oracle( self, oracle ):
        self.oracle = oracle


    def __varset( self, vdict ):
        vs  = list( vdict.keys() )
        svs = [ vdict[ v ] for v in vs ]  # vs.values() would _probably_ work here, but to be safe

        ety = namedtuple( 'E', vs )
        return ety( *svs )


    def __reg_decl( self, f ):
        def __inner( *args, **kwargs ):
            E, S, P = f( *args, **kwargs )
            if E:
                self.oracle.E = self.__varset( E )
            if S:
                self.oracle.S = self.__varset( S )
            if P:
                self.oracle.P = self.__varset( P )
            return

        self.__declare = __inner


    def __wrap( self, f ):
        def __inner( *args, **kwargs ):
            return f( *args, **kwargs )
        return __inner


    def __reg_desc( self, f ):
        self.__descriptor = self.__wrap( f )


    def __reg_env( self, f ):
        self.__environmental = self.__wrap( f )


    def __reg_st( self, f ):
        self.__state = self.__wrap( f )


    def __reg_bhv( self, f ):
        self.__behavior      = self.__wrap( f )
        self.__behavior_info = inspect.getfullargspec( f )


    def __type_resolve( self, args ):

        largs = list( args )
        for i, arg in enumerate( args ):
            if isinstance( arg, bool ) or isinstance( arg, bool ):
                largs[ i ] = cint_to_bv32( arg )

            if isinstance( arg, z3.z3.ArrayRef ):
                largs[ i ] = bv32arr_to_bv32( arg )

            # todo: any other cases?

        return tuple( largs )



    ########################
    ##### USER METHODS #####
    ########################

    # todo: handle various error cases

    def register( self, f ):
        self.__regmap[ f.__name__ ]( f )


    def Equal( self, *args ):
        args = self.__type_resolve( args )
        return ( args[ 0 ] == args[ 1 ] )


    def And( self, *args ):
        args = self.__type_resolve( args )
        return z3.And( *args )


    def Or( self, *args ):
        args = self.__type_resolve( args )
        return z3.Or( *args )

    # todo: add more
