###
# SymbExec
#
# symbolic execution module base class
#
class SymbExec( object ):


    ####
    # __init__
    #
    # initializer
    #
    def __init__( self, name, path ):
        self.name = name
        self.path = path


    ####
    # preprocess
    #
    # preprocessing hook, takes query and query index
    #
    def preprocess( self, query, idx ):
        pass


    ####
    # execute
    #
    # run symbolic execution
    #
    def execute( self, query, idx ):
        pass


    ####
    # parse
    #
    # parse the symbolic execution output
    #
    def parse( self, query, idx ):
        pass


    ####
    # clean
    #
    # clean up after the symbolic execution
    #
    def clean( self, query, idx ):
        pass


    ####
    # postprocess
    #
    # postprocessing after the symbolic execution
    # occurs after soid typecasts and introduces auxillary variables
    #
    def postprocess( self, query, idx, E, S, V, ext, varset ):
        pass
