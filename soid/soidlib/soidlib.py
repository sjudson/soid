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



def _bv32arr( x ):
    return z3.Array( x, z3.BitVecSort( 32 ), z3.BitVecSort( 8 ) )


def _cint_to_bv32( x ):
    return z3.BitVecVal( 1 * x, 32 )   # implicit bool conversion


def _cbool_to_bv32( x ):
    return _cint_to_bv32( x )


def _bv32arr_to_bv32( x ):
    return z3.Concat( z3.Select( x, z3.BitVecVal( 3, 32 ) ),
                      z3.Select( x, z3.BitVecVal( 2, 32 ) ),
                      z3.Select( x, z3.BitVecVal( 1, 32 ) ),
                      z3.Select( x, z3.BitVecVal( 0, 32 ) ) )


def _bv32( v ):
    if isinstance( v, str ):                             # if given a name then create a new array-based variable
        return _bv32arr( v )
    elif isinstance( v, bool ) or isinstance( v, int ):  # otherwise treat as a constant
        return _cint_to_bv32( v )
    else:
        pass # todo: handle


def _type_resolve( args ):

    largs = list( args )
    for i, arg in enumerate( args ):
        if isinstance( arg, bool ) or isinstance( arg, bool ):
            largs[ i ] = _cint_to_bv32( arg )

        if isinstance( arg, z3.z3.ArrayRef ):
            largs[ i ] = _bv32arr_to_bv32( arg )

        # todo: any other cases?
    return tuple( largs )


_tyu    = namedtuple( 'tyutil', [ 'bv32arr', 'int_to_bv32', 'bool_to_bv32', 'bv32arr_to_bv32' ] )
_tyutil = _tyu( bv32arr = _bv32arr, int_to_bv32 = _cint_to_bv32, bool_to_bv32 = _cbool_to_bv32, bv32arr_to_bv32 = _bv32arr_to_bv32 )

_ty     = namedtuple( 'types', [ 'bool', 'int', 'u32', 'util' ] )
types   = _ty( bool = _bv32, int = _bv32, u32 = _bv32, util = _tyutil )



####################
##### SYMBOLS ######
####################



_and = chr(int('2227', 16))
_or  = chr(int('2228', 16))
_not = chr(int('00AC', 16))
_imp = chr(int('2192', 16))
_iff = chr(int('27F7', 16))
_xor = chr(int('2295', 16))
_dom = chr(int('1D53B', 16))
_t   = chr(int('22A4', 16))
_f   = chr(int('22A5', 16))
_uni = chr(int('2200', 16))
_exi = chr(int('2203', 16))
_nex = chr(int('2204', 16))
_def = chr(int('2254', 16))
_prv = chr(int('22A2', 16))
_npv = chr(int('22AC', 16))
_mod = chr(int('22A8', 16))
_nmd = chr(int('22AD', 16))
_ctf = chr(int('25A1', 16)) + _imp

_sym    = namedtuple( 'symbols', [ 'land', 'lor', 'lnot', 'implies', 'iff', 'xor', 'domain', 'defi', 'true', 'false', 'universal',
                                   'existential', 'not_existential', 'proves', 'not_proves', 'models', 'not_models', 'counterfactual' ] )
symbols = _sym( land = _and, lor = _or, lnot = _not, xor = _xor,
                implies = _imp, iff = _iff,
                domain = _dom,
                defi = _def,
                true = _t, false = _f,
                universal = _uni, existential = _exi, not_existential = _nex,
                proves = _prv, not_proves = _npv, models = _mod, not_models = _nmd,
                counterfactual = _ctf )



####################
##### CORE API #####
####################


##### START Z3 Wrappers (with typecasting) #####
#
# todos: add more + handle error cases

def Equal( *args ):
    args = _type_resolve( args )
    return ( args[ 0 ] == args[ 1 ] )


def And( *args ):
    args = _type_resolve( args )
    return z3.And( *args )


def Or( *args ):
    args = _type_resolve( args )
    return z3.Or( *args )

##### END WRAPPERS ######


class Soid():

    def __init__( self, query_name, query_type, priority = float( 'inf' ), skip = False ):

        self.query_name = query_name
        self.query_type = query_type
        self.__synth = ( query_type not in [ verification, counterfactual.single ] )

        self.priority = priority
        self.skip     = skip

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


    ########################
    ##### USER METHODS #####
    ########################

    def register( self, f ):
        self.__regmap[ f.__name__ ]( f )

    def description( self, f ):
        self.__reg_desc( f )

    def environmental( self, f ):
        self.__reg_env( f )

    def state( self, f ):
        self.__reg_st( f )

    def behavior( self, f ):
        self.__reg_bhv( f )
