from collections import namedtuple

import os
import argparse
import Z3



def parse_args():

    parser = argparse.ArgumentParser( description = 'SMT-based oracles for investigating decisions.' )

    parser.add_argument( '-f', '--float', action = 'store_true', type = bool, default = False, dest = 'float', \
                         help = 'Use alternative symbolic execution (KLEE) engine with experimental support for floats.' )
    parser.add_argument( '-c', '--config', action = 'store', type = str, default = None, dest = 'config', required = True \
                         help = 'Location of program configuration file; if not resolveable path it will attempt to load ./{argument}.config.toml.' )
    parser.add_argument( '-q', '--query', action = 'query', type= str, default = None, dest = 'query', required = True \
                         help = 'Location of query file; if not resolveable path it will attempt to load ./{argument}.query.toml.' )


    return parser.parse_args()



class SoidAPI():


    def __init__( self ):
        self.solver = Z3.solver()

        self.E = None # environmental vars
        self.S = None # state vars
        self.P = None # program vars

        self.phi  = None # environmental
        self.vphi = None # state
        self.pi   = None # agent
        self.beta = None # behavior

        self._ = None    # ignored

        self.typemap = {
            'bool' : lambda n: bv32( n ),
            'int'  : lambda n: bv32( n ),
            # todo: add more
        }


    def wrap( self, f, store ):
        def __inner( *args, **kwargs ):
            store = f( *args, **kwargs )
            return


    def environmental( self, f ):
        return wrap( self, f, self.phi )


    def state( self, f ):
        return wrap( self, f, self.vphi )


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
