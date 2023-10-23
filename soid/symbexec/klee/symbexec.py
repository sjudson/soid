import os
import os.path
import re
import subprocess
import z3
from .. import SymbExec


###
# KleeSymbExec
#
# symbolic execution module for KLEE and KLEE-Float
#
class KleeSymbExec( SymbExec ):


    ####
    # __init__
    #
    # initializer
    #
    def __init__( self, path ):
        super().__init__( 'klee', path )


    ####
    # preprocess
    #
    # preprocessing hook, takes query and query index
    #
    def preprocess( self, query, idx ):
        # TODO: finish symbolizer support
        pass


    ####
    # execute
    #
    # run symbolic execution
    #
    def execute( self, query, idx ):
        mdir, _ = os.path.split( self.path )

        print( '##################\n## INVOKING KLEE #\n##################\n\n' )

        # todo: tie in symbolize
        cmd = [ 'make', 'symbolic' ]

        if idx != None:
            nm   = query.query_type + '.' + f'{idx}'
            cmd += [ f'SOID_QUERY={nm}' ]

        ret = subprocess.run( cmd, cwd = mdir )
        return


    ####
    # parse
    #
    # parse the symbolic execution output
    #
    def parse( self, query, idx ):
        mdir, _ = os.path.split( self.path )
        klee_last = mdir + '/klee-last'

        i  = 1
        fs = []
        while True:
            fn = klee_last + '/test' + str( i ).zfill( 6 ) + '.smt2'
            if not os.path.isfile( fn ):
                break

            fs.append( fn )
            i += 1

        if not fs:
            raise Exception('Unable to find symbolic execution output')

        paths = []
        for f in fs:
            path_components = z3.parse_smt2_file( f )
            if not path_components:
                raise Exception('Unable to parse symbolic execution output')
            if len( path_components ) == 1:
                paths.append( path_components[ 0 ] )
                continue

            paths.append( z3.And( *path_components ) )

        return paths


    ####
    # clean
    #
    # clean up after the symbolic execution
    #
    def clean( self, query, idx ):
        mdir, _ = os.path.split( self.path )

        print( '\n\n##################\n## CLEANING KLEE #\n##################\n\n' )
        ret = subprocess.run( [ 'make', 'clean' ], cwd = mdir )
        print( '\n\n##################\n## FINISHED KLEE #\n##################' )

        return


    ####
    # postprocess
    #
    # postprocessing after the symbolic execution
    #
    def postprocess( self, query, idx, E, S, D, ext, varset ):
        varlist = list( varset )

        def bind( v ):
            if not v.soid_isbv and not v.soid_isflt and not v.soid_isdbl:
                return True

            for vl in varlist:
                if str( v ) == re.sub( r'_ackermann![0-9]+', '', str( vl ) ):
                    if v.soid_isflt or v.soid_isdbl:
                        return ( z3.fpToIEEEBV( v ) == vl )
                    else:
                        return ( v == vl )

            return True

        amends = []
        if E:
            amends += [ bind( e ) for e in E ]
        if S:
            amends += [ bind( s ) for s in S ]
        if D:
            amends += [ bind( d ) for d in D ]

        amends += [ bind( v ) for v in ext ]
        return amends
