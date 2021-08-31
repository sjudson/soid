from collections import namedtuple

import os
import argparse
import z3


def parse_args():

    parser = argparse.ArgumentParser( description = 'SMT-based oracles for investigating decisions.' )

    parser.add_argument( '-f', '--float', action = 'store_true', default = False, dest = 'float', \
                         help = 'Use alternative symbolic execution (KLEE) engine with experimental support for floats.' )
    parser.add_argument( '-c', '--config', action = 'store', type = str, default = None, dest = 'config', required = True, \
                         help = 'Location of program configuration file; if not resolveable path it will attempt to load ./{argument}.config.toml.' )
    parser.add_argument( '-q', '--query', action = 'store', type = str, default = None, dest = 'query', required = True, \
                         help = 'Location of query file; if not resolveable path it will attempt to load ./{argument}.query.toml.' )
    parser.add_argument( '-n', '--enum', action = 'store', type = int, default = 100, dest = 'enum', required = False, \
                         help = 'Number of candidates to enumerate, used for sufficient synthesis queries.' )


    return parser.parse_args()



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
        self.solver = z3.solver()

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
            store = ret
            return


    def environmental( self, f ):
        return wrap( self, f, self.phi, self.obs_phi )


    def state( self, f ):
        return wrap( self, f, self.vphi, self.obs_vphi )


    def behavior( self, f ):
        return wrap( self, f, self.beta )


    def constrain( self, f ):
        return wrap( self, f, self._ )


    def bv32( self, name ):
        return Array( 'name', BitVec( '_', 32 ), BitVec( '_', 8 ) )


    def varset( self, vdict ):
        vs  = list( vdict.keys() )
        evs = namedtuple( 'E', vs )

        for i, v in enumerate( vs ):
            evs[ i ] = self.typemap( vdict[ v ] )( v )

        return evs


    def E( self, vdict ):
        self.E = varset( vdict );
        return self.E


    def S( self, vdict ):
        self.S = varset( vdict );
        return self.S


    def P( self, vdict ):
        self.P = varset( vdict );
        return self.P


    def state( self, f ):
        return wrap( self, f, self.vphi )


    def behavior( self, f ):
        return wrap( self, f, self.beta )


    def cpp_writer( self ):
        pass



if __name__ == '__main__':

    args = parse_args()
