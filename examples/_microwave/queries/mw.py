import soid

start  = 0
cancel = 1
dopen  = 2
dclose = 3
nothng = 4

def declare():

    E = { 'error' : 'bool', 'close' : 'bool', 'heat'  : 'bool', 'start' : 'bool' }
    S = { 'started' : 'bool' }
    P = { 'decision' : 'uint32' }

    return E, S, P
