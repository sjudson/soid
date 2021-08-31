from queue import LifoQueue
from collections import namedtuple

import os
import os.path
import sys
import argparse
import importlib
import types
import functools

import z3


def parse_args():

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



class SoidAPI():

    verification      = 1
    counterfactual = {
        'single'      : 2,
        'necessary'   : 3,
        'sufficient'  : 4,
    }
    behavior = {
        'necessary'   : 5,
        'sufficient'  : 6,
    }
    agent             = 7


    def __init__( self ):

        self.solver = z3.Solver()

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

        self._ = None    # ignored

        self.funcmap = {
            'environmental' : self._environmental,
            'state'         : self._state,
            'behavior'      : self._behavior,
            'constrain'     : self._constrain,
            'descriptor'    : self._descriptor,
            'query_type'    : self._query_type,
        }

        self.typemap = {
            'bool'  : lambda n: bv32( n ),
            'int'   : lambda n: bv32( n ),
            'uint32': lambda n: bv32( n ),
            # todo: add more
        }


    def wrap( self, f, store1, store2 = None ):
        def __inner( *args, **kwargs ):
            ret = f( *args, **kwargs )
            if type( ret ) == tuple and store2:
                store1, store2 = ret
            store1 = ret
            return
        return __inner


    def _environmental( self, f ):
        return self.wrap( f, self.phi, self.obs_phi )


    def _state( self, f ):
        return self.wrap( f, self.vphi, self.obs_vphi )


    def _behavior( self, f ):
        return self.wrap( f, self.beta )


    def _constrain( self, f ):
        return self.wrap( f, self._ )


    def _descriptor( self, f ):
        return self.wrap( f, self.descriptor )


    def _query_type( self, f ):
        return self.wrap( f, self.query_type )


    def bv32( self, name ):
        return Array( 'name', BitVec( '_', 32 ), BitVec( '_', 8 ) )


    def varset( self, vdict ):
        vs  = list( vdict.keys() )
        evs = namedtuple( 'E', vs )

        for i, v in enumerate( vs ):
            evs[ i ] = self.typemap( vdict[ v ] )( v )

        return evs


    def E( self, vdict ):
        self.E = self.varset( vdict );
        return self.E


    def S( self, vdict ):
        self.S = self.varset( vdict );
        return self.S


    def P( self, vdict ):
        self.P = self.varset( vdict );
        return self.P


def extract( qs, queue = LifoQueue() ):

    if 'soid' not in dir( qs ):
        return queue

    for name in dir( qs ):
        obj = getattr( qs, name )

        if isinstance( obj, types.ModuleType ):
            queue = extract( obj, queue )

        if name == 'query_type':
            q   = qs
            fs  = [ f for f in dir( q ) if f in soid.funcmap.keys() ]
            ctx = { 'name' : q.__name__ }

            for f in fs:
                obj = getattr( q, f )
                if isinstance( obj, types.FunctionType ):
                    setattr( q, f, soid.funcmap[ f ]( obj ) )
                    ctx[ f ] = getattr( q, f )
            queue.put( ctx )

    return queue


if __name__ == '__main__':

    soid = SoidAPI()
    args = parse_args()

    # load query module

    path, fn = os.path.split( args.queries )
    sys.path.insert( 0, path )
    qs = importlib.import_module( fn )

    # wrap query functions
    queries = extract( qs )

    # todo: make sure ctx has everything we need
