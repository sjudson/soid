from queue import LifoQueue
from collections import namedtuple

import os
import os.path
import sys
import argparse
import importlib
import types
import functools
import inspect

import z3



########################
# Inaccessible Globals #
########################



_cf = namedtuple( 'counterfactual', [ 'single', 'necessary', 'sufficient' ] )
_bh = namedtuple( 'behavior', [ 'necessary', 'sufficient' ] )

synthesis = False



###########################################
# User Accessible Functions and Constants #
###########################################



verification   = 0
counterfactual = cf( single = 1, necessary = 2, sufficient = 3 )
behavior       = bh(             necessary = 4, sufficient = 5 )
agent          = 6



def And( a, b ):
    return z3.And( a, b ) if not synthesis else None


def Or( a, b ):
    return z3.Or( a, b ) if not synthesis else None



############
# Core API #
############



class _SoidAPI():

    def __init__( self ):

        self.solver = pycvc4.Solver() if synthesis else z3.Solver()

        self.reset()
        self.populate_maps()

        self._ = None    # ignored


    def populate_maps( self ):
        self.regmap =  {
            'environmental' : self.reg_env,
            'state'         : self.reg_st,
            'behavior'      : self.reg_bhv,
            'declare'       : self.reg_decl,
            'descriptor'    : self.reg_desc,
            'query_type'    : self.reg_qt
        }

        self.runmap = [ self.run_verification, ]
        #self.run_single_counterfactual, self.run_necessary_counterfactual, self.run_sufficient_counterfactual,
        #self.run_necessary_behavior, self.run_sufficient_behavior,
        #self.run_agent ]

        self.typemap = {
            'bool'  : lambda n: self.bv32( n ),
            'int'   : lambda n: self.bv32( n ),
            'uint32': lambda n: self.bv32( n ),
            # todo: add more
        }


    def reset( self ):
        self.E = None # environmental vars
        self.S = None # state vars
        self.P = None # program vars

        self.phi  = None # environmental
        self.vphi = None # state
        self.pi   = None # agent
        self.beta = None # behavior

        # observed, optional for pretty printing counterfactuals
        self.obs_phi = None  # environmental
        self.obs_vphi = None # state

        self.descriptor = None
        self.query_type = None


    def wrap( self, f, store1, store2 = None ):
        def __inner( *args, **kwargs ):
            ret = f( *args, **kwargs )
            if type( ret ) == tuple and store2:
                store1, store2 = ret
            store1 = ret
            return ret
        return __inner


    def reg_env( self, f ):
        return self.wrap( f, self.phi, self.obs_phi )


    def reg_st( self, f ):
        return self.wrap( f, self.vphi, self.obs_vphi )


    def reg_bhv( self, f ):
        return self.wrap( f, self.beta )


    def reg_desc( self, f ):
        return self.wrap( f, self.descriptor )


    def req_qt( self, f ):
        return self.wrap( f, self.query_type )


    def varset( self, vdict ):
        vs  = list( vdict.keys() )
        evs = namedtuple( 'E', vs )

        for i, v in enumerate( vs ):
            evs[ i ] = self.typemap[ vdict[ v ] ]( v )

        return evs


    def reg_decl( self, f ):
        def __inner( *args, **kwargs ):
            E, S, P = f( *args, **kwargs )
            if E:
                self.E = self.varset( E )
            if S:
                self.S = self.varset( S )
            if P:
                self.P = self.varset( P )
            return
        return __inner


    def call_decl( self, ctx ):
        ctx[ 'declare' ]()


    def call_env( self, ctx ):
        ctx[ 'environmental' ]( self.E )


    def call_st( self, ctx ):
        ctx[ 'state' ]( self.S )


    def call_bhv( self, ctx ):
        info = inspect.getfullargspec( ctx[ 'behavior' ] )

        if info.args == [ 'P' ]:
            ctx[ 'behavior' ]( self.P )
        elif info.args == [ 'E', 'P' ]:
            ctx[ 'behavior' ]( self.E, self.P )
        elif info.args == [ 'S', 'P' ]:
            ctx[ 'behavior' ]( self.S, self.P )
        elif info.args == [ 'E', 'S', 'P' ]:
            ctx[ 'behavior' ]( self.E, self.S, self.P )
        else:
            pass # todo: handle



    def bv32( self, name ):
        return z3.Array( 'name', z3.BitVecSort( 32 ), z3.BitVecSort( 8 ) )



    def run_verification( self, ctx ):
        self.reset()

        self.call_decl( ctx )
        self.call_env( ctx )
        self.call_st( ctx )
        self.call_bhv( ctx )



#####################
# Utility Functions #
#####################



def _parse_args():

    parser = argparse.ArgumentParser( description = 'SMT-based oracles for investigating decisions.' )

    parser.add_argument( '-f', '--float', action = 'store_true', default = False, dest = 'float', \
                         help = 'Use alternative symbolic execution (KLEE) engine with experimental support for floats.' )
    parser.add_argument( '-m', '--make', action = 'store', type = str, default = None, dest = 'make', required = True, \
                         help = 'Location of program makefile; if not a resolveable path soid will attempt to load ./Makefile.' )
    parser.add_argument( '-qs', '-queries', action = 'store', type = str, default = None, dest = 'queries', required = True, \
                         help = 'Location of queries directory; if not a resolveable path soid will attempt to use ./')
    parser.add_argument( '-q', '--query', action = 'store', type = str, default = None, nargs = '*', dest = 'query', required = False, \
                         help = 'List of queries from directory to execute; if this parameter is not provided then all are attempted.' )
    parser.add_argument( '-n', '--enum', action = 'store', type = int, default = 100, dest = 'enum', required = False, \
                         help = 'Number of candidates to enumerate, used for sufficient synthesis queries.' )

    args = parser.parse_args()

    if not os.path.exists( args.make ):
        args.make  = './Makefile'
    if not os.path.exists( args.queries ):
        args.query = './'

    return args


def _extract( qs, args, queue = LifoQueue() ):

    if 'soid' not in dir( qs ):
        return queue

    for name in dir( qs ):
        obj = getattr( qs, name )

        if isinstance( obj, types.ModuleType ):
            queue = extract( obj, args, queue )

        if name == 'query_type':
            if args.query and q.__name__ not in args.query:
                continue

            q   = qs
            fs  = [ f for f in dir( q ) if f in soid.regmap.keys() ]
            ctx = { 'name' : q.__name__ }

            for f in fs:
                obj = getattr( q, f )
                if isinstance( obj, types.FunctionType ):
                    setattr( q, f, soid.regmap[ f ]( obj ) )
                    ctx[ f ] = getattr( q, f )
            queue.put( ctx )

    return queue


if __name__ == '__main__':

    soid = _SoidAPI()
    args = _parse_args()

    # load query module

    path, fn = os.path.split( args.queries )
    sys.path.insert( 0, path )
    qs = importlib.import_module( fn )

    # wrap query functions
    queries = _extract( qs, args )

    while not queries.empty():
        nxt = queries.get()
        qt  = nxt[ 'query_type' ]()

        synthesis = ( qt not in [ verification, counterfactual.single ] )
        soid.runmap[ qt ]( nxt )
