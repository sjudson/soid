from collections import namedtuple

import z3
import inspect



########################
##### QUERY TYPES ######
########################



_cf = namedtuple( 'counterfactual', [ 'single', 'necessary', 'sufficient' ] )
_bh = namedtuple( 'behavior', [ 'necessary', 'sufficient' ] )

verification   = 'verification'
counterfactual = _cf( single = 'counterfactual.single', necessary = 'counterfactual.necessary', sufficient = 'counterfactual.sufficient' )
behavior       = _bh(                                   necessary = 'behavior.necessary',       sufficient = 'behaviro.sufficient' )
agent          = 'agent'



######################
##### VAR TYPES ######
######################


####
# _bv32arr
#
# convert int variable to (Array (_ BitVec 32) (_ BitVec 8))
#
def _bv32arr( x ):
    return z3.Array( x, z3.BitVecSort( 32 ), z3.BitVecSort( 8 ) )


####
# _bv32bv
#
# convert int variable to (_ BitVec 32)
#
def _bv32bv( x ):
    return z3.BitVec( x, 32 )


####
# _cint_to_bv32arr
#
# convert constant int to (Array (_ BitVec 32) (_ BitVec 8))
#
def _cint_to_bv32( x ):
    return z3.BitVecVal( 1 * x, 32 )   # implicit bool conversion


####
# _cbool_to_bv32arr
#
# convert constant bool to (Array (_ BitVec 32) (_ BitVec 8))
#
def _cbool_to_bv32( x ):
    return _cint_to_bv32( x )


####
# _bv32arr_to_bv32
#
# convert (Array (_ BitVec 32) (_ BitVec 8)) to (_ BitVec 32)
#
def _bv32arr_to_bv32( x ):
    return z3.Concat( z3.Select( x, z3.BitVecVal( 3, 32 ) ),
                      z3.Select( x, z3.BitVecVal( 2, 32 ) ),
                      z3.Select( x, z3.BitVecVal( 1, 32 ) ),
                      z3.Select( x, z3.BitVecVal( 0, 32 ) ) )


####
# _bv32
#
# parse declaration of int or bool and turn into z3 expression
#
def _bv32( decl, as_bv = False ):

    if decl == 'bool':
        def __inner( v, val = None, pp = None, raw = None ):
            rv = raw if raw else v

            if isinstance( v, str ):
                if val:
                    var = _cbool_to_bv32( val )                        # named constant
                else:
                    var = _bv32bv( rv ) if as_bv else _bv32arr( rv )   # named variable
                setattr( var, 'soid_base', 'bool' )
                setattr( var, 'soid_isbv', as_bv )

                if pp:
                    setattr( var, 'soid_val_pp', pp )
                return var

            elif isinstance( v, bool ):                                # anonymous constant
                var = _cbool_to_bv32( v )
                setattr( var, 'soid_base', 'bool' )
                setattr( var, 'soid_isbv', as_bv )
                setattr( var, 'soid_pp', str( v ) )

                if pp:
                    setattr( var, 'soid_val_pp', pp )
                return var

            else:
                pass # todo: handle
        return __inner

    if decl == 'int' or decl == 'u32':
        def __inner( v, val = None, pp = None, raw = None ):
            rv = raw if raw else v

            if isinstance( v, str ):
                if val:                                               # named constant
                    var = _cint_to_bv32( val )
                else:
                    var = _bv32bv( rv ) if as_bv else _bv32arr( rv )  # named variable
                setattr( var, 'soid_pp', str( v ) )
                setattr( var, 'soid_base', 'u32' )
                setattr( var, 'soid_isbv', as_bv )

                if pp:
                    setattr( var, 'soid_val_pp', pp )
                return var

            elif isinstance( v, bool ):                               # anonymous constant
                var = _cint_to_bv32( v )
                setattr( var, 'soid_base', 'u32' )
                setattr( var, 'soid_isbv', as_bv )
                setattr( var, 'soid_pp', str( v ) )

                if pp:
                    setattr( var, 'soid_val_pp', pp )
                return var

            else:
                pass # todo: handle
        return __inner


####
# _fbool
#
# declare constant bool
#
def _fbool( val ):
    var = z3.BoolVal( val )
    setattr( var, 'soid_isbv', False )
    setattr( var, 'soid_pp', symbols.true if val else symbols.false )
    return var


####
# _type_resolve
#
# parse formula and resolve everything into z3 types
#
def _type_resolve( args ):

    largs  = list( args )
    sargs  = [ str( arg ) for arg in largs ]

    pretty = None
    for i, arg in enumerate( args ):

        if isinstance( arg, bool ):
            sargs[ i ] = symbols.true if arg else symbols.false
            largs[ i ] = _cbool_to_bv32( arg )

        elif isinstance( arg, int ):
            sargs[ i ] = str( arg )
            largs[ i ] = _cint_to_bv32( arg )

        elif isinstance( arg, z3.z3.BoolRef ):
            if hasattr( arg, 'soid_pp' ):
                sargs[ i ] = arg.soid_pp

        elif isinstance( arg, z3.z3.ArrayRef ):
            largs[ i ] = _bv32arr_to_bv32( arg )

            if hasattr( arg, 'soid_val_pp' ):
                pretty = arg.soid_val_pp

        # todo: any other cases?

    # pretty print special variable values
    if pretty:
        for i, sarg in enumerate( sargs ):
            if sarg in pretty.keys():
                sargs[ i ] = pretty[ sarg ]

    return tuple( largs ), tuple( sargs )


_tyu    = namedtuple( 'tyutil', [ 'bv32arr', 'bv32bv', 'int_to_bv32', 'bool_to_bv32', 'bv32arr_to_bv32' ] )
_tyutil = _tyu( bv32arr = _bv32arr, bv32bv = _bv32bv, int_to_bv32 = _cint_to_bv32, bool_to_bv32 = _cbool_to_bv32, bv32arr_to_bv32 = _bv32arr_to_bv32 )

_ty     = namedtuple( 'types', [ 'bool', 'int', 'u32', 'bool_bv', 'int_bv', 'u32_bv', 'util' ] )
types   = _ty( bool = _bv32( 'bool' ), int = _bv32( 'int' ), u32 = _bv32( 'u32' ), bool_bv = _bv32( 'bool', True ), int_bv = _bv32( 'int', True ), u32_bv = _bv32( 'u32', True ), util = _tyutil )



####################
##### SYMBOLS ######
####################



_and = chr( int( '2227', 16 ) )
_or  = chr( int( '2228', 16 ) )
_not = chr( int( '00AC', 16 ) )
_imp = chr( int( '2192', 16 ) )
_iff = chr( int( '27F7', 16 ) )
_xor = chr( int( '2295', 16 ) )
_dom = chr( int( '1D53B', 16 ) )
_t   = chr( int( '22A4', 16 ) )
_f   = chr( int( '22A5', 16 ) )
_uni = chr( int( '2200', 16 ) )
_exi = chr( int( '2203', 16 ) )
_nex = chr( int( '2204', 16 ) )
_def = chr( int( '2254', 16 ) )
_prv = chr( int( '22A2', 16 ) )
_npv = chr( int( '22AC', 16 ) )
_mod = chr( int( '22A8', 16 ) )
_nmd = chr( int( '22AD', 16 ) )
_ctf = chr( int( '25A1', 16 ) ) + _imp

_phi  = chr( int( '1D719', 16 ) )
_vphi = chr( int( '1D711', 16 ) )
_pi   = chr( int( '1D6F1', 16 ) )
_beta = chr( int( '1D6FD', 16 ) )

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


####
# Equal
#
# define equality
#
def Equal( *args ):
    args, sargs = _type_resolve( args )

    eqn = ( args[ 0 ] == args[ 1 ] )
    setattr( eqn, 'soid_pp', f'( {sargs[0]} == {sargs[1]} )' )

    return eqn


####
# Equal
#
# define conjunction
#
def And( *args ):
    args, sargs = _type_resolve( args )

    eqn = z3.And( *args )
    setattr( eqn, 'soid_pp', '( {} )'.format( f' {symbols.land} '.join( sargs ) ) )

    return eqn


####
# Equal
#
# define disjunction
#
def Or( *args ):
    args, sargs = _type_resolve( args )

    eqn = z3.Or( *args )
    setattr( eqn, 'soid_pp', '( {} )'.format( f' {symbols.lor} '.join( sargs ) ) )

    return eqn


####
# Equal
#
# define negation
#
def Not( *args ):
    args, sargs = _type_resolve( args )

    eqn = z3.Not( args[ 0 ] )
    setattr( eqn, 'soid_pp', f'{symbols.lnot}{sargs[0]}' )

    return eqn



##### END WRAPPERS ######


####
# Decl
#
# class used to capture a variable set declaration
#
class Decl():

    def __init__( self ):
        self.__soid__iter__init = dir( self )

    # I did not tell you it's okay to use reflection like this
    def __iter__( self ):
        self.__soid__iter__i   = 0
        self.__soid__iter__itms = list( filter( lambda x: x not in self.__soid__iter__init + [ '_Decl__soid__iter__init', '_Decl__soid__iter__i', '_Decl__soid__iter__itms' ], dir( self ) ) )
        return self

    def __next__( self ):
        if self.__soid__iter__i  == len( self.__soid__iter__itms ):
            raise StopIteration
        
        nxt = getattr( self, self.__soid__iter__itms[ self.__soid__iter__i ] )
        self.__soid__iter__i += 1

        return nxt
    

####
# Soid
#
# class used to define a soid query
#
class Soid():


    def __init__( self, query_name, query_type, priority = float( 'inf' ), expect = True, skip = False ):

        self.query_name = query_name
        self.query_type = query_type
        self.__synth = ( query_type not in [ verification, counterfactual.single ] )

        self.priority = priority
        self.skip     = skip
        self.expect   = expect

        self.__regmap = {
            'descriptor'    : self.__reg_desc,
            'declare'       : self.__reg_decl,
            'environmental' : self.__reg_env,
            'state'         : self.__reg_st,
            'behavior'      : self.__reg_bhv,
        }


    ####
    # __oracle
    #
    # gives query access to the oracle that will be used to discharge it,
    # which is then used so that it can set some variables as appropriate
    #
    def __oracle( self, oracle ):
        self.oracle = oracle


    ####
    # __varset
    #
    # loads variables from declaration onto object
    #
    def __varset( self, vdict, decl ):
        vs  = list( vdict.keys() )
        svs = [ vdict[ v ] for v in vs ]  # vs.values() would _probably_ work here, but to be safe

        for i, v in enumerate( vs ):
            setattr( decl, v, svs[ i ] )
        return decl


    ####
    # __reg_decl
    #
    # decorator whose inner loads declared variables into z3Py and gives to oracle
    #
    def __reg_decl( self, f ):

        def __inner( *args, **kwargs ):

            E, S, P = f( *args, **kwargs )
            if E:
                self.oracle.E = self.__varset( E, Decl() )
            if S:
                self.oracle.S = self.__varset( S, Decl() )
            if P:
                self.oracle.P = self.__varset( P, Decl() )

            self.__Eext = None
            self.__Sext = None
            cbools, _ = _type_resolve( ( True, False ) )
            for var in self.oracle.E:
                if var.soid_base == 'bool':
                    varg, _ = _type_resolve( ( var, ) )
                    # since bools get turned into (Array (_ BitVec 32) (_ BitVec 8)), constrain them to either 0 or 1
                    const = Or( Equal( varg[ 0 ], cbools[ 0 ] ), Equal( varg[ 0 ], cbools[ 1 ] ) )
                    self.__Eext = And( self.__Eext, const ) if self.__Eext != None else const

            for var in self.oracle.S:
                if var.soid_base == 'bool':
                    varg, _ = _type_resolve( ( var, ) )
                    # since bools get turned into (Array (_ BitVec 32) (_ BitVec 8)), constrain them to either 0 or 1
                    const = Or( Equal( varg[ 0 ], cbools[ 0 ] ), Equal( varg[ 0 ], cbools[ 1 ] ) )
                    self.__Sext = And( self.__Sext, const ) if self.__Sext != None else const

            return

        self.__declare = __inner


    ####
    # __reg_desc
    #
    # decorator whose inner loads query description
    #
    def __reg_desc( self, f ):
        def __inner( *args, **kwargs ):
            return f( *args, **kwargs )

        self.__descriptor = __inner


    ####
    # __reg_env
    #
    # decorator whose inner loads query environmental constraints
    #
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


    ####
    # __reg_st
    #
    # decorator whose inner loads query state constraints
    #
    def __reg_st( self, f ):
        def __inner( *args, **kwargs ):
            eqn = f( *args, **kwargs )
            if isinstance( eqn, bool ):
                eqn = _fbool( eqn )

            neqn = And( eqn, self.__Sext )
            setattr( neqn, 'soid_pp', eqn.soid_pp )

            return neqn
        self.__state = __inner


    ####
    # __reg_bhv
    #
    # decorator whose inner loads query behavior constraints
    #
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


    ####
    # register
    #
    # register arbitrary function (uses name to determine type)
    #
    def register( self, f ):
        self.__regmap[ f.__name__ ]( f ) # todo: handle error case


    ####
    # description
    #
    # register description function
    #
    def description( self, f ):
        self.__reg_desc( f )


    ####
    # environmental
    #
    # register environmental constraints function
    #
    def environmental( self, f ):
        self.__reg_env( f )


    ####
    # state
    #
    # register state constraints function
    #
    def state( self, f ):
        self.__reg_st( f )


    ####
    # behavior
    #
    # register behavior constraints function
    #
    def behavior( self, f ):
        self.__reg_bhv( f )
