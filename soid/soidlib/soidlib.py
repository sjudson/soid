from collections import namedtuple

import z3
import inspect



########################
##### QUERY TYPES ######
########################



_cf = namedtuple( 'counterfactual', [ 'single', 'necessary', 'sufficient' ] )
_bh = namedtuple( 'behavior', [ 'necessary', 'sufficient' ] )

introduction   = 'introduction'
verification   = 'verification'
counterfactual = _cf( single = 'counterfactual.single', necessary = 'counterfactual.necessary', sufficient = 'counterfactual.sufficient' )
behavior       = _bh(                                   necessary = 'behavior.necessary',       sufficient = 'behavior.sufficient' )
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
# _bv8arr
#
# convert int variable to (Array (_ BitVec 32) (_ BitVec 1))
#
def _bv8arr( x ):
    return z3.Array( x, z3.BitVecSort( 32 ), z3.BitVecSort( 1 ) )


####
# _bv32bv
#
# convert int variable to (_ BitVec 32)
#
def _bv32bv( x ):
    return z3.BitVec( x, 32 )


####
# _bv8bv
#
# convert bool variable to (_ BitVec 8)
#
def _bv8bv( x ):
    return z3.BitVec( x, 8 )


####
# _cint_to_bv32arr
#
# convert constant int to (Array (_ BitVec 32) (_ BitVec 8))
#
def _cint_to_bv32( x ):
    return z3.BitVecVal( 1 * x, 32 )


####
# _cbool_to_bv8arr
#
# convert constant bool to (Array (_ BitVec 32) (_ BitVec 8))
#
def _cbool_to_bv8( x ):
    return z3.BitVecVal( 1 * x, 8 )


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
# _bv8arr_to_bv8
#
# convert (Array (_ BitVec 32) (_ BitVec 1)) to (_ BitVec 8)
#
def _bv8arr_to_bv8( x ):
    return z3.Select( x, z3.BitVecVal( 0, 32 ) )


####
# _bv32
#
# parse declaration of int and turn into z3 expression
#
def _bv32( decl, as_bv = False, is_bool = False ):
    def __inner( v, val = None, pp = None, raw = None ):
        rv = raw if raw else v

        if isinstance( v, str ):
            if val:                                               # named constant
                var = _cint_to_bv32( val )
            else:
                var = _bv32bv( rv ) if as_bv else _bv32arr( rv )  # named variable
            setattr( var, 'soid_pp', str( v ) )
            setattr( var, 'soid_base', 'u32' )
            setattr( var, 'soid_isbool', is_bool )
            setattr( var, 'soid_isbv', as_bv )
            setattr( var, 'soid_isflt', False )
            setattr( var, 'soid_isdbl', False )

            if pp:
                setattr( var, 'soid_val_pp', pp )
            return var

        elif isinstance( v, bool ):
            var = _cint_to_bv32( v )                              # anonymous constant
            setattr( var, 'soid_pp', str( v ) )
            setattr( var, 'soid_base', 'u32' )
            setattr( var, 'soid_isbool', is_bool )
            setattr( var, 'soid_isbv', as_bv )
            setattr( var, 'soid_isflt', False )
            setattr( var, 'soid_isdbl', False )

            if pp:
                setattr( var, 'soid_val_pp', pp )
            return var

        else:
            pass # todo: handle
    return __inner


####
# _bv8
#
# parse declaration of bool and turn into z3 expression
#
def _bv8( decl, as_bv = False ):
    def __inner( v, val = None, pp = None, raw = None ):
        rv = raw if raw else v

        if isinstance( v, str ):
            if val:
                var = _cbool_to_bv8( val )                         # named constant
            else:
                var = _bv8bv( rv ) if as_bv else _bv8arr( rv )     # named variable
            setattr( var, 'soid_pp', str( v ) )
            setattr( var, 'soid_base', 'bool' )
            setattr( var, 'soid_isbv', as_bv )
            setattr( var, 'soid_isbool', True )
            setattr( var, 'soid_isflt', False )
            setattr( var, 'soid_isdbl', False )

            if pp:
                setattr( var, 'soid_val_pp', pp )
            return var

        elif isinstance( v, bool ):
            var = _cbool_to_bv8( v )                               # anonymous constant
            setattr( var, 'soid_pp', str( v ) )
            setattr( var, 'soid_base', 'bool' )
            setattr( var, 'soid_isbv', as_bv )
            setattr( var, 'soid_isbool', True )
            setattr( var, 'soid_isflt', False )
            setattr( var, 'soid_isdbl', False )

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
    setattr( var, 'soid_isbool', True )
    setattr( var, 'soid_isflt', False )
    setattr( var, 'soid_isdbl', False )
    setattr( var, 'soid_pp', symbols.true if val else symbols.false )
    return var


####
# _cfloat
#
# declare constant float
#
def _cfloat( x ):
    return z3.FPVal( x, z3.Float32() )


####
# _float
#
# declare float variable
#
def _float( x ):
    return z3.FP( x, z3.Float32() )


####
# _cdouble
#
# declare constant double
#
def _cdouble( x ):
    return z3.FPVal( x )


####
# _double
#
# declare double variable
#
def _double( x ):
    return z3.FP( x, z3.Float64() )


####
# _fp
#
# parse declaration of float or double and turn into z3 expression
#
def _fp( decl ):

    if decl == 'float':
        def __inner( v, val = None, pp = None, raw = None ):
            rv = raw if raw else v

            if isinstance( v, str ):
                if val:
                    var = _cfloat( val )                              # named constant
                else:
                    var = _float( rv )                                # named variable
            elif isinstance( v, float ):
                    var = _cfloat( v )                                # anonymous constant

            else:
                pass # todo: handle

            setattr( var, 'soid_pp', str( v ) )
            setattr( var, 'soid_base', 'float' )
            setattr( var, 'soid_isbv', False )
            setattr( var, 'soid_isflt', True )
            setattr( var, 'soid_isdbl', False )

            if pp:
                setattr( var, 'soid_val_pp', pp )
            return var

        return __inner

    if decl == 'double':
        def __inner( v, val = None, pp = None, raw = None ):
            rv = raw if raw else v

            if isinstance( v, str ):
                if val:
                    var = _cdouble( val )                             # named constant
                else:
                    var = _double( rv )                               # named variable
            elif isinstance( v, double ):
                    var = _cdouble( v )                               # anonymous constant

            else:
                pass # todo: handle

            setattr( var, 'soid_pp', str( v ) )
            setattr( var, 'soid_base', 'double' )
            setattr( var, 'soid_isbv', False )
            setattr( var, 'soid_isflt', False )
            setattr( var, 'soid_isdbl', True )

            if pp:
                setattr( var, 'soid_val_pp', pp )
            return var

        return __inner


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
            oarg = largs[ 1 - i ]
            largs[ i ] = _cint_to_bv32( arg ) if hasattr( oarg, 'soid_base' ) and not oarg.soid_base == 'bool' else _cbool_to_bv8( arg )

        elif isinstance( arg, int ):
            sargs[ i ] = str( arg )
            largs[ i ] = _cint_to_bv32( arg )

        elif isinstance( arg, float ):
            sargs[ i ] = f'{arg:.8f}'
            oarg = largs[ 1 - i ]
            largs[ i ] = _cdouble( arg ) if oarg.soid_isdbl else _cfloat( arg )

        elif isinstance( arg, z3.z3.BoolRef ):
            if hasattr( arg, 'soid_pp' ):
                sargs[ i ] = arg.soid_pp

        elif isinstance( arg, z3.z3.BitVecRef ):

            if hasattr( arg, 'soid_pp' ):
                sargs[ i ] = arg.soid_pp

            if hasattr( arg, 'soid_val_pp' ):
                pretty = arg.soid_val_pp

        elif isinstance( arg, z3.z3.ArrayRef ):
            largs[ i ] = _bv32arr_to_bv32( arg )

            if hasattr( arg, 'soid_val_pp' ):
                pretty = arg.soid_val_pp

        elif isinstance( arg, z3.z3.FPRef ):

            if hasattr( arg, 'soid_pp' ):
                sargs[ i ] = arg.soid_pp

            if hasattr( arg, 'soid_val_pp' ):
                pretty = arg.soid_val_pp

        # todo: any other cases?

    # pretty print special variable values
    if pretty:
        for i, sarg in enumerate( sargs ):
            if sarg in pretty.keys():
                sargs[ i ] = pretty[ sarg ]

    return tuple( largs ), tuple( sargs )


_tyu    = namedtuple( 'tyutil', [ 'bv32arr', 'bv8arr', 'bv32bv', 'bv8bv', 'int_to_bv32', 'bool_to_bv8', 'bv32arr_to_bv32', 'bv8arr_to_bv8', 'float', 'double' ] )
_tyutil = _tyu( bv32arr = _bv32arr,
                bv8arr = _bv8arr,

                bv32bv = _bv32bv,
                bv8bv = _bv8bv,

                int_to_bv32 = _cint_to_bv32,
                bool_to_bv8 = _cbool_to_bv8,

                bv32arr_to_bv32 = _bv32arr_to_bv32,
                bv8arr_to_bv8 = _bv8arr_to_bv8,

                float = _float,
                double = _double )

_ty     = namedtuple( 'types', [ 'bool', 'int', 'u32', 'bool_as_int', 'bool_as_u32', 'bool_bv', 'int_bv', 'u32_bv', 'bool_as_int_bv', 'bool_as_u32_bv', 'float', 'double', 'util' ] )
types   = _ty( bool = _bv8( 'bool' ),
               int = _bv32( 'int' ),
               u32 = _bv32( 'u32' ),
               bool_as_int = _bv32( 'int', False, True ),
               bool_as_u32 = _bv32( 'u32', False, True ),

               bool_bv = _bv8( 'bool', True ),
               int_bv = _bv32( 'int', True ),
               u32_bv = _bv32( 'u32', True ),
               bool_as_int_bv = _bv32( 'int', True, True ),
               bool_as_u32_bv = _bv32( 'u32', True, True ),

               float = _fp( 'float'),
               double = _fp( 'double' ),
               util = _tyutil )



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

_phi  = chr( int( '1D711', 16 ) )
_psi  = chr( int( '1D713', 16 ) )
_pi   = chr( int( '1D6F1', 16 ) )
_beta = chr( int( '1D6FD', 16 ) )

_sym    = namedtuple( 'symbols', [ 'land', 'lor', 'lnot', 'implies', 'iff', 'xor', 'domain', 'defi', 'true', 'false', 'universal', 'existential',
                                   'not_existential', 'proves', 'not_proves', 'models', 'not_models', 'counterfactual', 'phi', 'psi', 'pi', 'beta' ] )
symbols = _sym( land = _and, lor = _or, lnot = _not, xor = _xor,
                implies = _imp, iff = _iff,
                domain = _dom,
                defi = _def,
                true = _t, false = _f,
                universal = _uni, existential = _exi, not_existential = _nex,
                proves = _prv, not_proves = _npv, models = _mod, not_models = _nmd,
                counterfactual = _ctf,
                phi = _phi, psi = _psi, pi = _pi, beta = _beta )



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
# FP_GT
#
# define GT for floats
#
def FP_GT( *args ):
    args, sargs = _type_resolve( args )

    eqn = ( z3.fpGT( args[ 0 ], args[ 1 ] ) )
    setattr( eqn, 'soid_pp', f'( {sargs[0]} > {sargs[1]} )' )

    return eqn


####
# FP_GTE
#
# define GTE for floats
#
def FP_GTE( *args ):
    args, sargs = _type_resolve( args )

    eqn = ( z3.fpGEQ( args[ 0 ], args[ 1 ] ) )
    setattr( eqn, 'soid_pp', f'( {sargs[0]} >= {sargs[1]} )' )

    return eqn


####
# FP_LT
#
# define LT for floats
#
def FP_LT( *args ):
    args, sargs = _type_resolve( args )

    eqn = ( z3.fpLT( args[ 0 ], args[ 1 ] ) )
    setattr( eqn, 'soid_pp', f'( {sargs[0]} < {sargs[1]} )' )

    return eqn


####
# FP_LTE
#
# define LTE for floats
#
def FP_LTE( *args ):
    args, sargs = _type_resolve( args )

    eqn = ( z3.fpLEQ( args[ 0 ], args[ 1 ] ) )
    setattr( eqn, 'soid_pp', f'( {sargs[0]} <= {sargs[1]} )' )

    return eqn


####
# GT
#
# define GT for ints
#
def GT( *args ):
    args, sargs = _type_resolve( args )

    eqn = ( args[ 0 ] > args[ 1 ] )
    setattr( eqn, 'soid_pp', f'( {sargs[0]} > {sargs[1]} )' )

    return eqn


####
# GTE
#
# define GTE for ints
#
def GTE( *args ):
    args, sargs = _type_resolve( args )

    eqn = ( args[ 0 ] >= args[ 1 ] )
    setattr( eqn, 'soid_pp', f'( {sargs[0]} >= {sargs[1]} )' )

    return eqn


####
# LT
#
# define LT for ints
#
def LT( *args ):
    args, sargs = _type_resolve( args )

    eqn = ( args[ 0 ] < args[ 1 ] )
    setattr( eqn, 'soid_pp', f'( {sargs[0]} < {sargs[1]} )' )

    return eqn


####
# LTE
#
# define LTE for ints
#
def LTE( *args ):
    args, sargs = _type_resolve( args )

    eqn = ( args[ 0 ] <= args[ 1 ] )
    setattr( eqn, 'soid_pp', f'( {sargs[0]} <= {sargs[1]} )' )

    return eqn



####
# And
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

    def __getitem__( self, item ):
        return getattr( self, item )


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
            'falsified'     : self.__reg_f,
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

            E, S, D = f( *args, **kwargs )
            if E:
                self.oracle.E = self.__varset( E, Decl() )
            if S:
                self.oracle.S = self.__varset( S, Decl() )
            if D:
                self.oracle.D = self.__varset( D, Decl() )

            # since bools get turned into arrays or bitvectors, constrain them to either 0 or 1
            def extend( vs ):
                exts = None
                for v in vs:
                    if hasattr( v, 'soid_isbool' ) and v.soid_isbool:
                        varg,  _ = _type_resolve( ( v, ))
                        tbool, _ = _type_resolve( ( True, v ) )
                        fbool, _ = _type_resolve( ( False, v ) )

                        const = Or( Equal( varg[ 0 ], tbool[ 0 ] ), Equal( varg[ 0 ], fbool[ 0 ] ) )
                        exts = And( exts, const ) if exts != None else const

                return exts

            Es = list( self.oracle.E ) if self.oracle.E else []
            self.__Eext = extend( Es )

            Ss = list( self.oracle.S ) if self.oracle.S else []
            self.__Sext = extend( Ss )

            Ds = list( self.oracle.D ) if self.oracle.D else []
            self.__Dext = extend( Ds )

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
    # we also tag on the extended type constraints for V (forcing bools to be bools, etc.)
    #
    def __reg_env( self, f ):
        def __inner( *args, **kwargs ):
            eqn = f( *args, **kwargs )
            if isinstance( eqn, bool ):
                eqn = _fbool( eqn )

            if self.__Eext == None and self.__Dext == None:
                return eqn

            neqn = eqn

            if self.__Eext != None:
                neqn = And( neqn, self.__Eext )
            if self.__Dext != None:
                neqn = And( neqn, self.__Dext )

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

            if self.__Sext == None:
                return eqn

            neqn = And( eqn, self.__Sext )
            setattr( neqn, 'soid_pp', eqn.soid_pp )

            return neqn
        self.__state = __inner


    ####
    # __reg_f
    #
    # decorator whose inner loads query falsified constraints
    #
    def __reg_f( self, f ):
        def __inner( *args, **kwargs ):
            eqn = f( *args, **kwargs )
            if isinstance( eqn, bool ):
                eqn = _fbool( eqn )

            return eqn
        self.__falsified = __inner


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
    # declare
    #
    # register declare function
    #
    def declare( self, f ):
        self.__reg_decl( f )


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
    # falsified
    #
    # register falsified constraints function
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
