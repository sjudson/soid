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


def _bv32( decl ):

    if decl == 'bool':
        def __inner( v, val = None, pp = None ):
            if isinstance( v, str ):
                var = _cbool_to_bv32( val ) if val else _bv32arr( v )  # named variable
                setattr( var, 'soid_base', 'bool' )

                if val:                                                # named constant
                    setattr( var, 'soid_pp', v )

                if pp:
                    setattr( var, 'soid_val_pp', pp )
                return var

            elif isinstance( v, bool ):                                # anonymous constant
                var = _cbool_to_bv32( v )
                setattr( var, 'soid_base', 'bool' )
                setattr( var, 'soid_pp', str( v ) )

                if pp:
                    setattr( var, 'soid_val_pp', pp )
                return var

            else:
                pass # todo: handle
        return __inner

    if decl == 'int' or decl == 'u32':
        def __inner( v, val = None, pp = None ):
            if isinstance( v, str ):
                var = _cint_to_bv32( val ) if val else _bv32arr( v )  # named variable
                setattr( var, 'soid_base', 'u32' )

                if val:                                               # named constant
                    setattr( var, 'soid_pp', v )

                if pp:
                    setattr( var, 'soid_val_pp', pp )
                return var

            elif isinstance( v, bool ):                               # anonymous constant
                var = _cint_to_bv32( v )
                setattr( var, 'soid_base', 'u32' )
                setattr( var, 'soid_pp', str( v ) )

                if pp:
                    setattr( var, 'soid_val_pp', pp )
                return var

            else:
                pass # todo: handle
        return __inner


def _fbool( val ):
    var = z3.BoolVal( val )
    setattr( var, 'soid_pp', symbols.true if val else symbols.false )
    return var


def _type_resolve( args ):

    largs  = list( args )
    sargs  = [ str( arg ) for arg in largs ]
    
    pretty = None
    for i, arg in enumerate( args ):
        if isinstance( arg, bool ):
            sargs[ i ] = symbols.true if arg else symbols.false
            largs[ i ] = _cint_to_bv32( arg )

        elif isinstance( arg, z3.z3.ArrayRef ):
            largs[ i ] = _bv32arr_to_bv32( arg )

            if hasattr( arg, 'soid_val_pp' ):
                pretty = arg.soid_val_pp

        # todo: any other cases?

    if pretty:
        for i, sarg in enumerate( sargs ):
            if sarg in pretty.keys():
                sargs[ i ] = pretty[ sarg ]

    return tuple( largs ), tuple( sargs )


_tyu    = namedtuple( 'tyutil', [ 'bv32arr', 'int_to_bv32', 'bool_to_bv32', 'bv32arr_to_bv32' ] )
_tyutil = _tyu( bv32arr = _bv32arr, int_to_bv32 = _cint_to_bv32, bool_to_bv32 = _cbool_to_bv32, bv32arr_to_bv32 = _bv32arr_to_bv32 )

_ty     = namedtuple( 'types', [ 'bool', 'int', 'u32', 'util' ] )
types   = _ty( bool = _bv32( 'bool' ), int = _bv32( 'int' ), u32 = _bv32( 'u32' ), util = _tyutil )



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

_phi  = chr(int('1D719', 16))
_vphi = chr(int('1D711', 16))
_pi   = chr(int('1D6F1', 16))
_beta = chr(int('1D6FD', 16))

_sym    = namedtuple( 'symbols', [ 'land', 'lor', 'lnot', 'implies', 'iff', 'xor', 'domain', 'defi', 'true', 'false', 'universal', 'existential',
                                   'not_existential', 'proves', 'not_proves', 'models', 'not_models', 'counterfactual', 'phi', 'vphi', 'pi', 'beta' ] )
symbols = _sym( land = _and, lor = _or, lnot = _not, xor = _xor,
                implies = _imp, iff = _iff,
                domain = _dom,
                defi = _def,
                true = _t, false = _f,
                universal = _uni, existential = _exi, not_existential = _nex,
                proves = _prv, not_proves = _npv, models = _mod, not_models = _nmd,
                counterfactual = _ctf,
                phi = _phi, vphi = _vphi, pi = _pi, beta = _beta )



####################
##### CORE API #####
####################


##### START Z3 Wrappers (with typecasting) #####
#
# todos: add more + handle error cases

def Equal( *args ):
    args, sargs = _type_resolve( args )

    eqn = ( args[ 0 ] == args[ 1 ] )
    setattr( eqn, 'soid_pp', f'( {sargs[0]} == {sargs[1]} )' )

    return eqn


def And( *args ):
    args, sargs = _type_resolve( args )

    eqn = z3.And( *args )
    setattr( eqn, 'soid_pp', '( {} )'.format( f' {symbols.land} '.join( sargs ) ) )

    return eqn


def Or( *args ):
    args, sargs = _type_resolve( args )

    eqn = z3.Or( *args )
    setattr( eqn, 'soid_pp', '( {} )'.format( f' {symbols.lor} '.join( sargs ) ) )

    return eqn


def Not( *args ):
    args, sargs = _type_resolve( args )

    eqn = z3.Not( args[ 0 ] )
    setattr( eqn, 'soid_pp', f'{symbols.lnot}{sargs[0]}' )

    return eqn



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

            self.__Eext = None
            self.__Sext = None
            cbools, _ = _type_resolve( ( True, False ) )
            for var in self.oracle.E:
                if var.soid_base == 'bool':
                    varg, _ = _type_resolve( ( var, ) )
                    const = Or( Equal( varg[ 0 ], cbools[ 0 ] ), Equal( varg[ 0 ], cbools[ 1 ] ) )
                    self.__Eext = And( self.__Eext, const ) if self.__Eext != None else const

            for var in self.oracle.S:
                if var.soid_base == 'bool':
                    varg, _ = _type_resolve( ( var, ) )
                    const = Or( Equal( varg[ 0 ], cbools[ 0 ] ), Equal( varg[ 0 ], cbools[ 1 ] ) )
                    self.__Sext = And( self.__Sext, const ) if self.__Sext != None else const

            return

        self.__declare = __inner


    def __reg_desc( self, f ):
        def __inner( *args, **kwargs ):
            return f( *args, **kwargs )

        self.__descriptor = __inner


    def __reg_env( self, f ):
        def __inner( *args, **kwargs ):
            eqn = f( *args, **kwargs )
            if isinstance( eqn, bool ):
                eqn = _fbool( eqn )

            if self.__Eext == None:
                return eqn

            neqn = And( eqn, self.__Eext )
            setattr( neqn, 'soid_pp', eqn.soid_pp )

            return neqn
        self.__environmental = __inner


    def __reg_st( self, f ):
        def __inner( *args, **kwargs ):
            eqn = f( *args, **kwargs )
            if isinstance( eqn, bool ):
                eqn = _fbool( eqn )
                
            neqn = And( eqn, self.__Sext )
            setattr( neqn, 'soid_pp', eqn.soid_pp )

            return neqn
        self.__state = __inner


    def __reg_bhv( self, f ):
        def __inner( *args, **kwargs ):
            eqn = f( *args, **kwargs )
            if isinstance( eqn, bool ):
                eqn = _fbool( eqn )

            return eqn
        self.__behavior      = __inner
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
