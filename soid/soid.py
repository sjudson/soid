#!/usr/bin/env python

from colorama import Fore, Style
from collections import namedtuple

import soidlib

import os
import os.path
import re
import sys
import argparse
import subprocess
import importlib
import types
import functools

import z3
import pycvc5


###
# Oracle
#
# the core class that formulates and discharges queries
#
class Oracle():

    def __init__( self ):

        self.runners = {
            soidlib.verification              : self.verif,
            soidlib.counterfactual.single     : self.scf,
            soidlib.counterfactual.necessary  : self.nycf,
            soidlib.counterfactual.sufficient : self.stcf,
            #soidlib.behavior.necessary        : self.nbv,
            #soidlib.behavior.sufficient       : self.sbv,
            #soidlib.agent                     : self.agent
        }

        self.ct  = 0
        self.introduction = ''

        self.reset()
        return


    ####
    # ld_env
    #
    # loads environmental constraints registered through soidlib
    #
    def ld_env( self, query ):

        ret = None
        if hasattr( query, '_Soid__environmental' ):
            ret = query._Soid__environmental( self.E )

        def __inner( obs = False ):
            if type( ret ) == tuple and len( ret ) == 2:
                return ret[ 0 ] if not obs else ret[ 1 ]
            elif type( ret ) == tuple:
                pass # todo: handle
            else:
                return ret

        self.phi     = lambda: __inner()
        self.obs_phi = lambda: __inner( True )
        return


    ####
    # ld_st
    #
    # loads state constraints registered through soidlib
    #
    def ld_st( self, query ):

        ret = None
        if hasattr( query, '_Soid__state' ):
            ret = query._Soid__state( self.S )

        def __inner( obs = False ):
            if type( ret ) == tuple and len( ret ) == 2:
                return ret[ 0 ] if not obs else ret[ 1 ]
            elif type( ret ) == tuple:
                pass # todo: handle
            else:
                return ret

        self.psi     = lambda: __inner()
        self.obs_psi = lambda: __inner( True )
        return


    ####
    # ld_bhv
    #
    # loads behavioral constraints registered through soidlib
    #
    def ld_bhv( self, query ):

        ret = None
        if hasattr( query, '_Soid__behavior' ):
            info = query._Soid__behavior_info

            if info.args == [ 'P' ]:
                ret = query._Soid__behavior( self.P )
            elif info.args == [ 'E', 'P' ]:
                ret = query._Soid__behavior( self.E, self.P )
            elif info.args == [ 'S', 'P' ]:
                ret = query._Soid__behavior( self.S, self.P )
            elif info.args == [ 'E', 'S', 'P' ]:
                ret = query._Soid__behavior( self.E, self.S, self.P )
            else:
                pass # todo: handle

        def __inner():
            return ret
        self.beta = __inner
        return


    ####
    # ld_agnt
    #
    # invokes KLEE to load agent constraints
    #
    def ld_agnt( self, makefile, variants, idx ):
        mdir, _ = os.path.split( makefile )

        print( '##################\n## INVOKING KLEE #\n##################\n\n' )

        # todo: tie in symbolize
        cmd = [ 'make', 'symbolic' ]

        if variants:
            nm   = self.type + '.' + f'{idx}'
            cmd += [ f'SOID_QUERY={nm}' ]

        ret = subprocess.run( cmd, cwd = mdir )
        klee_last = mdir + '/klee-last'

        i  = 1
        fs = []
        while True:
            fn = klee_last + '/test' + str( i ).zfill( 6 ) + '.smt2'
            if not os.path.isfile( fn ):
                break

            fs.append( fn )
            i += 1

        paths = []
        for f in fs:
            path_components = z3.parse_smt2_file( f )
            if len( path_components ) == 1:
                paths.append( path_components[ 0 ] )
                break

            paths.append( z3.And( *path_components ) )

        print( '\n\n##################\n## CLEANING KLEE #\n##################\n\n' )

        ret = subprocess.run( [ 'make', 'clean' ], cwd = mdir )

        print( '\n\n##################\n## FINISHED KLEE #\n##################' )

        self.paths = paths
        self.build_pi()

        return


    ####
    # build_pi
    #
    # combines paths from KLEE to generate agent constraints
    #
    def build_pi( self ):

        def create( p ):
            if p.soid_isbv:
                v = soidlib.types.util.bv32bv( '__soid__' + str( p ) )
                setattr( v, 'soid_isbv', True )
                return v

            v = soidlib.types.util.bv32arr( '__soid__' + str( p ) )
            setattr( v, 'soid_isbv', False )
            return v

        symbls = [ create( p ) for p in self.P ]

        def cast( i, p ):
            if p.soid_isbv:
                return ( p == symbls[ i ] )
            return soidlib.types.util.bv32arr_to_bv32( p ) == soidlib.types.util.bv32arr_to_bv32( symbls[ i ] )

        amends = [ cast( i, p ) for i, p in enumerate( self.P ) ]

        varset = set()
        for path in self.paths:
            for v in z3.z3util.get_vars( path ):
                varset.add( v )
        varlist = list( varset )

        def bind( v ):
            if not v.soid_isbv:
                return True

            for vl in varlist:
                if str( v ) == re.sub( r'_ackermann![0-9]+', '', str( vl ) ):
                    return ( v == vl )

            return True

        amends += [ bind( e ) for e in self.E ] + [ bind( s ) for s in self.S ] + [ bind( p ) for p in self.P ] + [ bind( s ) for s in symbls ]
        amended = [ z3.And( [ path ] + amends ) for path in self.paths ]

        def __inner():
            return z3.Or( *amended )
        self.pi = __inner
        return


    ####
    # load
    #
    # loads agent constraints and query constraints, and sets metadata
    #
    def load( self, query ):

        self.ct += 1
        self.reset()

        # register as oracle for query
        query._Soid__oracle( self )

        # extract mangled
        self.name   = query.query_name
        self.type   = query.query_type
        self.synth  = ( self.type not in [ soidlib.verification, soidlib.counterfactual.single ] )
        self.solver = z3.Solver() if not self.synth else pycvc5.Solver()

        query._Soid__declare()
        self.description = query._Soid__descriptor()

        self.expect = query.expect

        self.ld_env( query )
        self.ld_st( query )
        self.ld_bhv( query )

        self.info = {
            'name':        self.name,
            'type':        self.type,
            'description': self.description,
            'expect':      self.expect,
            'count':       self.ct,

            'E':           self.E,
            'S':           self.S,
            'P':           self.P,

            'phi':         self.phi,
            'psi':         self.psi,
            'obs_phi':     self.obs_phi,
            'obs_psi':     self.obs_psi,
            'pi':          self.pi,
            'beta':        self.beta,
        }

        return


    ####
    # reset
    #
    # clears the oracle in-between invocations
    #
    def reset( self ):

        self.synth  = None
        self.solver = None

        self.E = None    # environmental vars
        self.S = None    # state vars
        self.P = None    # program vars

        self.phi  = None # environmental
        self.psi  = None # state
        self.pi   = None
        self.beta = None # behavior

        # observed, optional for pretty printing counterfactuals
        self.obs_phi  = None # environmental
        self.obs_psi = None # state

        self.description = None

        self.info = None

        return


    ####
    # recurse
    #
    # walks DFS through formula tree in z3Py
    #
    def recurse( self, expr, I ):
        cs = []
        for child in expr.children():
            c, I = self.z3_to_cvc5( child, I )
            cs.append( c )

        return cs, I


    ####
    # z3_to_cvc5
    #
    # converts an expression from z3Py to CVC5 python API, continues recursion
    #
    def z3_to_cvc5( self, expr, I = {} ):

        if expr == None:
            return None, I

        s = str( expr )
        if s in I:
            return I[ s ], I

        if z3.is_and( expr ):
            cs, I = self.recurse( expr, I )
            return self.solver.mkTerm( pycvc5.kinds.And, *cs ), I

        if z3.is_or( expr ):
            cs, I = self.recurse( expr, I )
            return self.solver.mkTerm( pycvc5.kinds.Or, *cs ), I

        if z3.is_implies( expr ):
            cs, I = self.recurse( expr, I )
            return self.solver.mkTerm( pycvc5.kinds.Implies, *cs ), I

        if z3.is_not( expr ):
            cs, I = self.recurse( expr, I )
            return self.solver.mkTerm( pycvc5.kinds.Not, *cs ), I

        if z3.is_eq( expr ):
            cs, I = self.recurse( expr, I )
            return self.solver.mkTerm( pycvc5.kinds.Equal, *cs ), I

        if z3.is_quantifier( expr ) and expr.is_exists():
            cs, I = self.recurse( expr, I )
            return self.solver.mkTerm( pycvc5.kinds.Exists, *cs ), I

        if z3.is_quantifier( expr ) and expr.is_forall():
            cs, I = self.recurse( expr, I )
            return self.solver.mkTerm( pycvc5.kinds.Forall, *cs ), I

        if z3.is_add( expr ):
            cs, I = self.recurse( expr, I )

            c = expr.children()[ 0 ]
            if z3.is_bv( c ) or z3.is_bv_value( c ):
                return self.solver.mkTerm( pycvc5.kinds.BVAdd, *cs ), I
            elif z3.is_fp( c ) or z3.is_fp_value( c ) or z3.is_fprm( c ) or z3.is_fprm_value( c ):
                return self.solver.mkTerm( pycvc5.kinds.FPAdd, *cs ), I
            else:
                return self.solver.mkTerm( pycvc5.kinds.Plus, *cs ), I

        if z3.is_mul( expr ):
            cs, I = self.recurse( expr, I )

            c = expr.children()[ 0 ]
            if z3.is_bv( c ) or z3.is_bv_value( c ):
                return self.solver.mkTerm( pycvc5.kinds.BVMult, *cs ), I
            elif z3.is_fp( c ) or z3.is_fp_value( c ) or z3.is_fprm( c ) or z3.is_fprm_value( c ):
                return self.solver.mkTerm( pycvc5.kinds.FPMult, *cs ), I
            else:
                return self.solver.mkTerm( pycvc5.kinds.Mult, *cs ), I

        if z3.is_sub( expr ):
            cs, I = self.recurse( expr, I )

            c = expr.children()[ 0 ]
            if z3.is_bv( c ) or z3.is_bv_value( c ):
                return self.solver.mkTerm( pycvc5.kinds.BVSub, *cs ), I
            elif z3.is_fp( c ) or z3.is_fp_value( c ) or z3.is_fprm( c ) or z3.is_fprm_value( c ):
                return self.solver.mkTerm( pycvc5.kinds.FPSub, *cs ), I
            else:
                return self.solver.mkTerm( pycvc5.kinds.Minus, *cs ), I

        if z3.is_div( expr ):
            pass

        if z3.is_idiv( expr ):
            pass

        if z3.is_mod( expr ):
            pass

        # signed le
        if hasattr( expr, 'decl' ) and str( expr.decl() ) == '<=':
            cs, I = self.recurse( expr, I )

            c = expr.children()[ 0 ]
            if z3.is_bv( c ) or z3.is_bv_value( c ):
                return self.solver.mkTerm( pycvc5.kinds.BVSle, *cs ), I
            elif z3.is_fp( c ) or z3.is_fp_value( c ) or z3.is_fprm( c ) or z3.is_fprm_value( c ):
                return self.solver.mkTerm( pycvc5.kinds.FPSle, *cs ), I
            else:
                return self.solver.mkTerm( pycvc5.kinds.LEQ, *cs ), I

        # unsigned le
        if hasattr( expr, 'decl' ) and str( expr.decl() ) == 'ULE':
            cs, I = self.recurse( expr, I )

            c = expr.children()[ 0 ]
            if z3.is_bv( c ) or z3.is_bv_value( c ):
                return self.solver.mkTerm( pycvc5.kinds.BVUle, *cs ), I
            elif z3.is_fp( c ) or z3.is_fp_value( c ) or z3.is_fprm( c ) or z3.is_fprm_value( c ):
                return self.solver.mkTerm( pycvc5.kinds.FPUle, *cs ), I
            else:
                return self.solver.mkTerm( pycvc5.kinds.LEQ, *cs ), I

        # signed lt
        if hasattr( expr, 'decl' ) and str( expr.decl() ) == '<':
            cs, I = self.recurse( expr, I )

            c = expr.children()[ 0 ]
            if z3.is_bv( c ) or z3.is_bv_value( c ):
                return self.solver.mkTerm( pycvc5.kinds.BVSlt, *cs ), I
            elif z3.is_fp( c ) or z3.is_fp_value( c ) or z3.is_fprm( c ) or z3.is_fprm_value( c ):
                return self.solver.mkTerm( pycvc5.kinds.FPSlt, *cs ), I
            else:
                return self.solver.mkTerm( pycvc5.kinds.LT, *cs ), I

        # unsigned lt
        if hasattr( expr, 'decl' ) and str( expr.decl() ) == 'ULT':
            cs, I = self.recurse( expr, I )

            c = expr.children()[ 0 ]
            if z3.is_bv( c ) or z3.is_bv_value( c ):
                return self.solver.mkTerm( pycvc5.kinds.BVUlt, *cs ), I
            elif z3.is_fp( c ) or z3.is_fp_value( c ) or z3.is_fprm( c ) or z3.is_fprm_value( c ):
                return self.solver.mkTerm( pycvc5.kinds.FPUlt, *cs ), I
            else:
                return self.solver.mkTerm( pycvc5.kinds.LT, *cs ), I

        # signed ge
        if hasattr( expr, 'decl' ) and str( expr.decl() ) == '>=':
            cs, I = self.recurse( expr, I )

            c = expr.children()[ 0 ]
            if z3.is_bv( c ) or z3.is_bv_value( c ):
                return self.solver.mkTerm( pycvc5.kinds.BVSge, *cs ), I
            elif z3.is_fp( c ) or z3.is_fp_value( c ) or z3.is_fprm( c ) or z3.is_fprm_value( c ):
                return self.solver.mkTerm( pycvc5.kinds.FPSge, *cs ), I
            else:
                return self.solver.mkTerm( pycvc5.kinds.GEQ, *cs ), I

        # unsigned ge
        if hasattr( expr, 'decl' ) and str( expr.decl() ) == 'UGE':
            cs, I = self.recurse( expr, I )

            c = expr.children()[ 0 ]
            if z3.is_bv( c ) or z3.is_bv_value( c ):
                return self.solver.mkTerm( pycvc5.kinds.BVUge, *cs ), I
            elif z3.is_fp( c ) or z3.is_fp_value( c ) or z3.is_fprm( c ) or z3.is_fprm_value( c ):
                return self.solver.mkTerm( pycvc5.kinds.FPUge, *cs ), I
            else:
                return self.solver.mkTerm( pycvc5.kinds.GEQ, *cs ), I

        # signed gt
        if hasattr( expr, 'decl' ) and str( expr.decl() ) == '>':
            cs, I = self.recurse( expr, I )

            c = expr.children()[ 0 ]
            if z3.is_bv( c ) or z3.is_bv_value( c ):
                return self.solver.mkTerm( pycvc5.kinds.BVSgt, *cs ), I
            elif z3.is_fp( c ) or z3.is_fp_value( c ) or z3.is_fprm( c ) or z3.is_fprm_value( c ):
                return self.solver.mkTerm( pycvc5.kinds.FPSgt, *cs ), I
            else:
                return self.solver.mkTerm( pycvc5.kinds.GT, *cs ), I

        # unsigned gt
        if hasattr( expr, 'decl' ) and str( expr.decl() ) == 'UGT':
            cs, I = self.recurse( expr, I )

            c = expr.children()[ 0 ]
            if z3.is_bv( c ) or z3.is_bv_value( c ):
                return self.solver.mkTerm( pycvc5.kinds.BVUgt, *cs ), I
            elif z3.is_fp( c ) or z3.is_fp_value( c ) or z3.is_fprm( c ) or z3.is_fprm_value( c ):
                return self.solver.mkTerm( pycvc5.kinds.FPUgt, *cs ), I
            else:
                return self.solver.mkTerm( pycvc5.kinds.GT, *cs ), I

        # bitvector ops
        if hasattr( expr, 'decl' ) and str( expr.decl() ) == 'Extract':
            c, I = self.z3_to_cvc5( expr.children()[ 0 ], I )
            ex = self.solver.mkOp( pycvc5.kinds.BVExtract, expr.params()[ 0 ], expr.params()[ 1 ] )
            return self.solver.mkTerm( ex, c ), I

        # bitvector ops
        if hasattr( expr, 'decl' ) and str( expr.decl() ) == 'ZeroExt':
            c, I = self.z3_to_cvc5( expr.children()[ 0 ], I )
            ex = self.solver.mkOp( pycvc5.kinds.BVZeroExtend, expr.params()[ 0 ] )
            return self.solver.mkTerm( ex, c ), I

        # bitvector ops
        if hasattr( expr, 'decl' ) and str( expr.decl() ) == 'Concat':
            cs, I = self.recurse( expr, I )
            return self.solver.mkTerm( pycvc5.kinds.BVConcat, *cs ), I

        if z3.is_select( expr ):
            cs, I = self.recurse( expr, I )
            return self.solver.mkTerm( pycvc5.kinds.Select, *cs ), I

        if z3.is_store( expr ):
            cs, I = self.recurse( expr, I )
            return self.solver.mkTerm( pycvc5.kinds.Store, *cs ), I

        if z3.is_seq( expr ):
            pass

        # CONSTS

        if z3.is_true( expr ):
            return self.solver.mkTrue(), I

        if z3.is_false( expr ):
            return self.solver.mkFalse(), I

        if z3.is_int_value( expr ):
            return self.solver.mkInteger( expr.as_long() ), I

        if z3.is_rational_value( expr ):
            return self.solver.mkReal( expr.as_double() ), I

        if z3.is_algebraic_value( expr ):
            return self.solver.mkReal( expr.as_double() ), I

        if z3.is_bv_value( expr ):
            return self.solver.mkBitVector( expr.size(), expr.as_long() ), I

        if z3.is_finite_domain_value( expr ):
            pass

        if z3.is_fprm_value( expr ):
            pass

        if z3.is_fp_value( expr ):
            pass

        if z3.is_string_value( expr ):
            pass

        if z3.is_const_array( expr ) or z3.is_K( expr ):
            pass

        # VARS

        if z3.is_bool( expr ):
            v = self.solver.mkVar( self.solver.getBooleanSort(), str( expr ) )
            I[ s ] = v
            return v, I

        if z3.is_int( expr ):
            v = self.solver.mkVar( self.solver.getIntegerSort(), str( expr ) )
            I[ s ] = v
            return v, I

        if z3.is_real( expr ):
            v = self.solver.mkVar( self.solver.getRealSort(), str( expr ) )
            I[ s ] = v
            return v, I

        if z3.is_array( expr ):
            d, I = self.z3_to_cvc5( expr.domain(), I )
            r, I = self.z3_to_cvc5( expr.range(), I )
            v = self.solver.mkVar( self.solver.mkArraySort( d, r ), str( expr ) )
            I[ s ] = v
            return v, I

        if z3.is_map( expr ):
            pass

        if z3.is_bv( expr ):
            v = self.solver.mkVar( self.solver.mkBitVectorSort( expr.size() ), str( expr ) )
            I[ s ] = v
            return v, I

        if z3.is_finite_domain( expr ):
            pass

        if z3.is_fprm( expr ):
            pass

        if z3.is_fp( expr ):
            pass

        if z3.is_string( expr ):
            pass

        # SORTS

        if z3.is_arith_sort( expr ):
            if expr.is_int():
                return self.solver.getIntegerSort(), I
            elif expr.is_real():
                return self.solver.getRealSort(), I
            else:
                pass # todo: handle

        if z3.is_bv_sort( expr ):
            return self.solver.mkBitVectorSort( expr.size() ), I

        if z3.is_array_sort( expr ):
            d, I = self.z3_to_cvc5( expr.domain(), I )
            r, I = self.z3_to_cvc5( expr.range(), I )
            return self.solver.mkArraySort( d, r ), I

        if z3.is_finite_domain_sort( expr ):
            pass

        if z3.is_fp_sort( expr ):
            pass

        if z3.is_fprm_sort( expr ):
            pass

    ####
    # prep_sygus
    #
    # setup options + logic + grammar for sygus for synthesis
    #
    def prep_sygus( self, I ):

        # set options
        self.solver.setOption( 'lang', 'sygus2' )
        self.solver.setOption( 'incremental', 'false' )
        self.solver.setOption( 'verbose', 'true' )
        self.solver.setOption( 'verbosity', '2' )

        ###
        # debugging options
        #self.solver.setOption( 'trace', 'datatypes-check' )
        #self.solver.setOption( 'trace', 'datatypes-proc' )
        #self.solver.setOption( 'trace', 'datatypes-prereg' )
        #self.solver.setOption( 'trace', 'datatypes-debug' )
        #self.solver.setOption( 'trace', 'dt-expand' )
        #self.solver.setOption( 'trace', 'cegqi' )
        #self.solver.setOption( 'trace', 'cegqi-debug' )
        #self.solver.setOption( 'trace', 'cegqi-dt-debug' )

        # set logic
        self.solver.setLogic( 'AUFBV' )

        # add all input vars not in formulas to sygus context
        for v in self.E._fields:
            if v in I:
                continue
            _, I = self.z3_to_cvc5( getattr( self.E, v ) )

        for v in self.S._fields:
            if v in I:
                continue
            _, I = self.z3_to_cvc5( getattr( self.S, v ) )

        # define grammar terminals
        gbool = self.solver.mkVar( self.solver.getBooleanSort(), "Bool" )
        gbv32 = self.solver.mkVar( self.solver.mkBitVectorSort( 32 ), "BV32" )
        gbv24 = self.solver.mkVar( self.solver.mkBitVectorSort( 24 ), "BV24" )
        gbv16 = self.solver.mkVar( self.solver.mkBitVectorSort( 16 ), "BV16" )
        gbv08 = self.solver.mkVar( self.solver.mkBitVectorSort(  8 ), "BV08" )
        gbv01 = self.solver.mkVar( self.solver.mkBitVectorSort(  1 ), "BV01" )

        # make grammar, note that gbool needs to be there as the starting non-terminal
        g = self.solver.mkSygusGrammar( list( I.values() ), [ gbool, gbv32, gbv24, gbv16, gbv08, gbv01 ] )

        # define bitvector rules
        BV32Add = self.solver.mkTerm( pycvc5.kinds.BVAdd,  gbv32, gbv32 )
        BV32Mul = self.solver.mkTerm( pycvc5.kinds.BVMult, gbv32, gbv32 )
        BV32Sub = self.solver.mkTerm( pycvc5.kinds.BVSub,  gbv32, gbv32 )
        BV08Add = self.solver.mkTerm( pycvc5.kinds.BVAdd,  gbv08, gbv08 )
        BV08Mul = self.solver.mkTerm( pycvc5.kinds.BVMult, gbv08, gbv08 )
        BV08Sub = self.solver.mkTerm( pycvc5.kinds.BVSub,  gbv08, gbv08 )

        BV01Extract  = self.solver.mkTerm( self.solver.mkOp( pycvc5.kinds.BVExtract,  0,  0 ), gbv08 )
        BV08Extract0 = self.solver.mkTerm( self.solver.mkOp( pycvc5.kinds.BVExtract,  7,  0 ), gbv32 )
        BV08Extract1 = self.solver.mkTerm( self.solver.mkOp( pycvc5.kinds.BVExtract, 15,  8 ), gbv32 )
        BV08Extract2 = self.solver.mkTerm( self.solver.mkOp( pycvc5.kinds.BVExtract, 23, 16 ), gbv32 )
        BV08Extract3 = self.solver.mkTerm( self.solver.mkOp( pycvc5.kinds.BVExtract, 31, 24 ), gbv32 )
        BV08ZeroExt  = self.solver.mkTerm( self.solver.mkOp( pycvc5.kinds.BVZeroExtend, 7 ), gbv01 )

        BV16Concat = self.solver.mkTerm( pycvc5.kinds.BVConcat, gbv08, gbv08 )
        BV24Concat = self.solver.mkTerm( pycvc5.kinds.BVConcat, gbv16, gbv08 )
        BV32Concat = self.solver.mkTerm( pycvc5.kinds.BVConcat, gbv24, gbv08 )

        g.addRules( gbv32, { BV32Add, BV32Mul, BV32Sub, BV32Concat } )
        g.addRules( gbv24, { BV24Concat } )
        g.addRules( gbv16, { BV16Concat } )
        g.addRules( gbv08, { BV08Add, BV08Mul, BV08Sub, BV08Extract0, BV08Extract1, BV08Extract2, BV08Extract3, BV08ZeroExt } )
        for val in I.values():
            g.addRules( gbv08, { self.solver.mkTerm( pycvc5.kinds.Select, val, gbv32 ) } )

        # define bitvector constants
        g.addRules( gbv32, { self.solver.mkBitVector( 32, 0 ) } )
        for i in range( 32 ):
            g.addRules( gbv32, { self.solver.mkBitVector( 32, ( 1 << i ) ) } )

        g.addRules( gbv01, { self.solver.mkBitVector( 1, 0 ) } )
        g.addRules( gbv01, { self.solver.mkBitVector( 1, 1 ) } )

        # define boolean rules
        And     = self.solver.mkTerm( pycvc5.kinds.And, gbool, gbool )
        Or      = self.solver.mkTerm( pycvc5.kinds.Or,  gbool, gbool )
        Not     = self.solver.mkTerm( pycvc5.kinds.Not, gbool )
        Implies = self.solver.mkTerm( pycvc5.kinds.Implies, gbool, gbool )
        _True   = self.solver.mkTrue()
        _False  = self.solver.mkFalse()

        BV32Sle  = self.solver.mkTerm( pycvc5.kinds.BVSle, gbv32, gbv32 )
        BV32Ule  = self.solver.mkTerm( pycvc5.kinds.BVUle, gbv32, gbv32 )
        BV32Slt  = self.solver.mkTerm( pycvc5.kinds.BVSlt, gbv32, gbv32 )
        BV32Ult  = self.solver.mkTerm( pycvc5.kinds.BVUlt, gbv32, gbv32 )
        BV32Sge  = self.solver.mkTerm( pycvc5.kinds.BVSge, gbv32, gbv32 )
        BV32Uge  = self.solver.mkTerm( pycvc5.kinds.BVUge, gbv32, gbv32 )
        BV32Sgt  = self.solver.mkTerm( pycvc5.kinds.BVSgt, gbv32, gbv32 )
        BV32Ugt  = self.solver.mkTerm( pycvc5.kinds.BVUgt, gbv32, gbv32 )
        BV08Sle  = self.solver.mkTerm( pycvc5.kinds.BVSle, gbv08, gbv08 )
        BV08Ule  = self.solver.mkTerm( pycvc5.kinds.BVUle, gbv08, gbv08 )
        BV08Slt  = self.solver.mkTerm( pycvc5.kinds.BVSlt, gbv08, gbv08 )
        BV08Ult  = self.solver.mkTerm( pycvc5.kinds.BVUlt, gbv08, gbv08 )
        BV08Sge  = self.solver.mkTerm( pycvc5.kinds.BVSge, gbv08, gbv08 )
        BV08Uge  = self.solver.mkTerm( pycvc5.kinds.BVUge, gbv08, gbv08 )
        BV08Sgt  = self.solver.mkTerm( pycvc5.kinds.BVSgt, gbv08, gbv08 )
        BV08Ugt  = self.solver.mkTerm( pycvc5.kinds.BVUgt, gbv08, gbv08 )

        g.addRules( gbool, { And, Or, Not, Implies, _True, _False,
                             BV32Sle, BV32Ule, BV32Slt, BV32Ult, BV32Sge, BV32Uge, BV32Sgt, BV32Ugt,
                             BV08Sle, BV08Ule, BV08Slt, BV08Ult, BV08Sge, BV08Uge, BV08Sgt, BV08Ugt } )

        return g


    ####
    # run
    #
    # invoke appropriate runner for type of query
    def run( self ):
        return self.runners[ self.type ]()  # todo: handle error case

    ####
    # verif
    #
    # execute verification query
    #
    def verif( self ):
        self.solver.add(
            z3.Not(
                z3.Implies(
                    z3.And( self.phi(), self.psi(), self.pi() ),
                    self.beta() ) ) )

        unsat = ( self.solver.check() == z3.unsat )
        if unsat:
            return ( self.info, unsat, None )

        model = self.solver.model()

        for var in list( self.E ) + list( self.S ) + list( self.P ):
            model.eval( var, model_completion = True )

        return ( self.info, unsat, [ model ] )


    ####
    # scf
    #
    # execute single counterfactual query
    #
    def scf( self ):
        self.solver.add(
            z3.And(
                z3.And( self.phi(), self.psi(), self.pi() ),
                z3.Implies(
                    z3.And( self.phi(), self.psi(), self.pi() ),
                    self.beta() ) ) )

        unsat = ( self.solver.check() == z3.unsat )
        if unsat:
            return ( self.info, not unsat, None )

        model = self.solver.model()

        for var in list( self.E ) + list( self.S ) + list( self.P ):
            model.eval( var, model_completion = True )

        return ( self.info, not unsat, [ model ] )


    ####
    # nycf
    #
    # execute necessary counterfactual query
    #
    def nycf( self ):

        phi,  I = self.z3_to_cvc5( self.phi() )
        psi, I  = self.z3_to_cvc5( self.psi(), I )
        pi,   _ = self.z3_to_cvc5( self.pi() )
        beta, _ = self.z3_to_cvc5( self.beta() )

        if not phi:
            phi = self.solver.mkTrue()

        if not psi:
            psi = self.solver.mkTrue()

        g = self.prep_sygus( I )

        # define target function
        nf = self.solver.synthFun( "necessary", list( I.values() ), self.solver.getBooleanSort(), g )

        # invoke as uninterpretated function for use with semantic constraint
        args = [ self.solver.mkSygusVar( i.getSort(), str( i ) ) for i in I.values() ]
        necc = self.solver.mkTerm( pycvc5.kinds.ApplyUf, nf, *args )

        self.solver.addSygusConstraint(
            self.solver.mkTerm( pycvc5.kinds.And,
                                self.solver.mkTerm( pycvc5.kinds.And, [ necc, phi, psi, pi ] ),
                                self.solver.mkTerm( pycvc5.kinds.Implies,
                                                    self.solver.mkTerm( pycvc5.kinds.And, [ necc, phi, psi, pi ] ),
                                                    beta ) ) )

        if ( self.solver.checkSynth().isUnsat() ):
            terms = [ nf ]
            #self.synthd_pp( terms, self.solver.getSynthSolutions( terms ) )


    ####
    # stcf
    #
    # execute sufficient counterfactual query
    #
    def stcf( self ):
        pass



##########################
##### CLI FUNCTIONS ######
##########################



####
# query_pp
#
# pretty print logic formulas
# todo: either get beautifHOL working or reimplement it in Python
#
def query_pp( name, query ):

    if isinstance( query, bool ):
        formula = soidlib.symbols.true if query else soidlib.symbols.false
    else:
        formula = query.soid_pp

    if name == 'phi':
        print( f'\n\t                 environmental ({soidlib.symbols.phi}). {formula}' )
    elif name == 'psi':
        print( f'\n\t                         state ({soidlib.symbols.psi}). {formula}' )
    elif name == 'beta':
        print( f'\n\t                      behavior ({soidlib.symbols.beta}). {formula}' )

    return


####
# model_recurse
#
# walk through a model and convert bitvector arrays to reals/ints for pretty printing
#
def model_recurse( expr, tier = 3 ):

    # todo: make robust
    if z3.is_store( expr ) or z3.is_K( expr ):
        if len( expr.children() ) == 1 and isinstance( expr.children()[ 0 ], z3.BitVecNumRef ):
                return expr.children()[ 0 ].as_long()

        if len( expr.children() ) == 3:
            if z3.is_K( expr.children()[ 0 ] ) and isinstance( expr.children()[ 2 ], z3.BitVecNumRef ):
                if expr.children()[ 1 ].as_long() == 0:               # overwrite
                    return ( expr.children()[ 2 ].as_long() )
                else:                                                 # extend
                    return ( expr.children()[ 2 ].as_long() << tier ) + model_recurse( expr.children()[ 0 ], tier - 1 )

            elif z3.is_store( expr.children()[ 0 ] ) and isinstance( expr.children()[ 2 ], z3.BitVecNumRef ):
                return ( expr.children()[ 2 ].as_long() << tier ) + model_recurse( expr.children()[ 0 ], tier - 1 )

    elif z3.is_bv( expr ):
        return expr.as_long()

####
# model_pp
#
# pretty print a model as a counterexample or counterfactual
#
def model_pp( E, S, P, model ):
    vs = [ d for d in model.decls() if '__soid__' not in d.name() ]

    Es = []
    Ss = []
    Ps = []
    for v in vs:
        val   = model_recurse( model[ v ] )

        # sometimes there are other vars that aren't in the decls, e.g., xxx_ackermann!xx, so ignore them
        try:
            ref = ([ vr for vr in E if str( vr ) == v.name() ] + [ vr for vr in S if str( vr ) == v.name() ] + [ vr for vr in P if str( vr ) == v.name() ] ).pop()
        except:
            continue
        btype = ref.soid_base
        name  = v.name()

        if btype == 'bool':
            val = soidlib.symbols.true if val == 1 else soidlib.symbols.false

        if btype == 'u32':
            val = str( val )

        if hasattr( ref, 'soid_pp' ):
            name = ref.soid_pp

        if hasattr( ref, 'soid_val_pp' ) and val in ref.soid_val_pp:
            val = ref.soid_val_pp[ val ]

        if ref in E:
            Es.append((name, val))
        if ref in S:
            Ss.append((name, val))
        if ref in P:
            Ps.append((name, val))

    nl = max( [ len( name[0] ) for name in Es + Ss + Ps ] )
    for (name, val) in sorted( Es,  key = lambda x: x[ 0 ] ):
        print( f'\n\t                 {name.rjust( nl )}. {val}' )
    print( f'\n' )
    for (name, val) in sorted( Ss, key = lambda x: x[ 0 ] ):
        print( f'\n\t                 {name.rjust( nl )}. {val}' )
    print( f'\n' )
    for (name, val) in sorted( Ps, key = lambda x: x[ 0 ] ):
        print( f'\n\t                 {name.rjust( nl )}. {val}' )
    print( f'\n' )

    return


####
# synthd_pp
#
# pretty print a synthesized function (formula)
# copied from https://github.com/cvc5/cvc5/blob/39f90ff035a5e5024fe0cd11b965f1103d83e88d/examples/api/python/utils.py
#
def synthd_pp( terms, solutions ):

    def define_fun_to_string( f, params, body ):
        sort = f.getSort()
        if sort.isFunction():
            sort = f.getSort().getFunctionCodomainSort()
            result = ""
            result += "(define-fun " + str( f ) + " ("
            for param in params:
                if i > 0:
                    result += " "
                else:
                    result += "(" + str( param ) + " " + str( param.getSort() ) + ")"
        result += ") " + str( sort ) + " " + str( body ) + ")"
        return result


    result = ""
    for i, term in enumerate( terms ):
        params = []
        if solutions[ i ].getKind() == pycvc5.kinds.Lambda:
            params += solutions[ i ][ 0 ]
            body    = solutions[ i ][ 1 ]
        result += "  " + define_fun_to_string( term, params, body ) + "\n"
        print( result )

    return


####
# verif_pp
#
# pretty print output of verification query
#
def verif_pp( info, unsat, model = None ):
    ex = soidlib.symbols.true if info[ 'expect' ] else soidlib.symbols.false
    eq = ( unsat == info[ 'expect' ] )

    mark  = chr( int( '2713', 16 ) ) if eq else chr( int( '2717', 16 ) )
    color = Fore.GREEN if eq else Fore.RED

    print(
        f'\n\t                                                                                                              '
        f'\n\t{str(info[ "count" ]).zfill(7)}.  |  name: {info[ "name" ]}  |  type: verification                            '
    )
    print( info[ 'description' ] )
    print(
        f'\n\t                expect: {ex}  |  result: [{color}{mark}{Style.RESET_ALL}]                                     '
        f'\n\t                                                                                                              '
        f'\n\tconstraints:                                                                                                  '
        f'\n\t                                                                                                              '
    )

    query_pp( 'phi',  info[ 'phi' ]() )
    query_pp( 'psi',  info[ 'psi' ]() )
    query_pp( 'beta', info[ 'beta' ]() )

    if not unsat and model:
        print(
            f'\n\t                                                                                                          '
            f'\n\tcounterexample:                                                                                           '
            f'\n\t                                                                                                          '
        )
        model_pp( info[ 'E' ], info[ 'S' ], info[ 'P' ], model )

    print(
        f'\n\t                                                                                                              '
    )


####
# scf_pp
#
# pretty print output of single counterfactual query
#
def scf_pp( info, sat, model = None ):
    ex = soidlib.symbols.true if info[ 'expect' ] else soidlib.symbols.false
    eq = ( sat == info[ 'expect' ] )

    mark  = chr( int( '2713', 16 ) ) if eq else chr( int( '2717', 16 ) )
    color = Fore.GREEN if eq else Fore.RED

    print(
        f'\n\t                                                                                                              '
        f'\n\t{str(info[ "count" ]).zfill(7)}.  |  name: {info[ "name" ]}  |  type: counterfactual.single                   '
    )
    print( info[ 'description' ] )
    print(
        f'\n\t                expect: {ex}  |  result: [{color}{mark}{Style.RESET_ALL}]                                     '
        f'\n\t                                                                                                              '
        f'\n\tconstraints:                                                                                                  '
        f'\n\t                                                                                                              '
    )

    query_pp( 'phi',  info[ 'phi' ]() )
    query_pp( 'psi',  info[ 'psi' ]() )
    query_pp( 'beta', info[ 'beta' ]() )

    if sat and model:
        print(
            f'\n\t                                                                                                          '
            f'\n\tcounterfactual                                                                                            '
            f'\n\t                                                                                                          '
        )
        model_pp( info[ 'E' ], info[ 'S' ], info[ 'P' ], model )

    print(
        f'\n\t                                                                                                              '
    )




####
# parse_args
#
# parse command line arguments
#
def parse_args():

    parser = argparse.ArgumentParser( description = 'SMT-based oracles for investigating decisions.' )

    parser.add_argument( '-m', '--make', action = 'store', type = str, default = None, dest = 'make', required = True, \
                         help = 'Location of program makefile; if not a resolveable path soid will attempt to load ./Makefile.' )
    parser.add_argument( '-qs', '-queries', action = 'store', type = str, default = None, dest = 'queries', required = True, \
                         help = 'Location of queries directory; if not a resolveable path soid will attempt to use ./')

    parser.add_argument( '-vs', '--variants', action = 'store_true', default = False, dest = 'variants', \
                         help = 'Pass variable into makefile allowing use of source code variants.' )

    parser.add_argument( '-n', '--enum', action = 'store', type = int, default = 100, dest = 'enum', required = False, \
                         help = 'Number of candidates to enumerate, used for sufficient synthesis queries.' )

    args = parser.parse_args()

    if not os.path.exists( args.make ):
        args.make  = './Makefile'
    if not os.path.exists( args.queries ):
        args.queries = './'

    return args


####
# extract
#
# recurse through queries module and find all queries
#
def extract( qs, args, oracle, queue = [] ):

    if 'Soid' not in dir( qs ) and 'soidlib' not in dir( qs ):
        return queue

    for name in dir( qs ):
        obj = getattr( qs, name )

        if callable( obj ) and name == 'introduction':
            oracle.introduction = obj()  # todo: handle error case

        if isinstance( obj, types.ModuleType ):
            queue = extract( obj, args, oracle, queue )

        if isinstance( obj, soidlib.Soid ):
            queue.append( obj )

    return queue



###########################
##### MAIN INTERFACE ######
###########################



def invoke( make_path, query_path, enum = 100, variants = False ):

    oracle = Oracle()

    path, fn = os.path.split( query_path )
    sys.path.insert( 0, path )
    qs = importlib.import_module( fn )

    queries = extract( qs, args, oracle )
    queries.sort( key = lambda query: query.priority, reverse = True )

    yield ( { 'type': soidlib.introduction, 'description': oracle.introduction }, None, None )

    idx = 0
    while queries:
        idx += 1

        nxt = queries.pop()

        if nxt.skip:
            continue

        oracle.load( nxt )
        oracle.ld_agnt( args.make, args.variants, idx )

        yield oracle.run()


if __name__ == '__main__':
    args = parse_args()
    outs = invoke( args.make, args.queries, args.enum, args.variants )

    for ( info, res, models ) in outs:

        if info[ 'type' ] == soidlib.introduction:
            print( info[ 'description' ] + '\n\n' )

        if info[ 'type' ] == soidlib.verification:
            verif_pp( info, res, models[ 0 ] if models else None )

        if info[ 'type' ] == soidlib.counterfactual.single:
            scf_pp( info, res, models[ 0 ] if models else None )