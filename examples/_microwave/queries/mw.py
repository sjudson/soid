import soid

start  = 0
cancel = 1
dopen  = 2
dclose = 3
nothng = 4

@soid.constrain
def constrain():

    E = soid.E( {
        'error' : 'bool',
        'close' : 'bool',
        'heat'  : 'bool',
        'start' : 'bool',
    } )
    S = soid.S ( { 'started' : 'bool' } )
    P = soid.P( { 'decision' : 'uint32' } )
