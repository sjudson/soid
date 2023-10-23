import subprocess
import re

from functools import reduce

ITERS = 10

def mark( tval ):
    return '\cmark' if tval else '\\xmark'

def amend( base, i, nxt ):
    return ( base * i + nxt ) / ( i + 1.0 )

def run( test ):
    pattern = re.compile( r'Result: ([A-Za-z]+) Resources: (\{.*\})', re.IGNORECASE )

    runs = []
    for i in range( ITERS ):
        res = subprocess.run( [ 'python', '/usr/src/soid/examples/other/query.py', test ],
                              capture_output = True, text = True ).stdout.rsplit('\n##################\n## FINISHED KLEE #\n##################\n')[ 1 ]

        # this is morally rephensible, but it works and I'm lazy
        search    = pattern.match( res.splitlines()[ 0 ] ).groups()
        result    = eval( search[ 0 ] )
        resources = eval( search[ 1 ] )

        runs.append( ( result, resources[ 'time' ][ 'symbolic' ], resources[ 'time' ][ 'solving' ], resources[ 'time' ][ 'total' ], resources[ 'paths' ] ) )

        return reduce( lambda acc, r: ( acc[ 0 ] and r[ 1 ][ 0 ],
                                        amend( acc[ 1 ], r[ 0 ], r[ 1 ][ 1 ] ),
                                        amend( acc[ 2 ], r[ 0 ], r[ 1 ][ 2 ] ),
                                        amend( acc[ 3 ], r[ 0 ], r[ 1 ][ 3 ] ),
                                        r[ 1 ][ 4 ] ), enumerate( runs ), ( True, 0.0, 0.0, 0.0, 0 ) )


def execute( tests ):
    add = ''
    for test in tests:
        results = run( test )
        add += f'\, {test} \, & \, {results[ 1 ]:.3e} \, & \, {results[ 2 ]:.3e} \, & \, {results[ 3 ]:.3e} \, & \, {results[ 4 ]} \, \\\\'

    return add


if __name__ == '__main__':

        base = '''
\documentclass{article}

\\usepackage{amsmath}
\\usepackage{amssymb}
\\usepackage{fullpage}

\\begin{document}

\\begin{table}[!t]
\centering
\\tiny
\\begin{tabular}{|l || c | c | c | c |}
\hline
\, name \, & \, symbolic (s) \, & \, solving (s) \, & \, total (s) \, & \, paths \, \\\\
\hline
'''
    base += execute( [ 'test.float.basic',
                       'test.mw.cancel', 'test.mw.nothing', 'test.mw.open', 'test.mw.options', 'test.mw.close', 'test.mw.never',
		       'test.car.confirm', 'test.car.causal', 'test.car.swapped', 'test.car.front', 'test.car.away' ] )
    base += '''
\hline
\end{tabular}
\\vspace{2mm}
\caption{Additional Benchmarks (reported avg. $n = 10$).}
\label{tbl:ab}
\end{table}

\end{document}
    '''

    print(base)
