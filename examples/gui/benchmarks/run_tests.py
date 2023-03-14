import subprocess
from functools import reduce

def mark( tval ):
    return '\cmark' if tval else '\\xmark'

def amend( base, i, nxt ):
    return ( base * i + nxt ) / ( i + 1.0 )

def run( test, model ):

    runs = []
    for i in range( ITERS ):
        subprocess.run( [ 'python',
                          '/usr/src/soid/examples/gui/duckietown-soid/src/webserver/counterfactual.py',
                          '/usr/src/soid/examples/gui/benchmarks/queries' + '/' + model + '/' + test + '.json' ],
                        stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL )

        res = subprocess.run( [ 'python',
                                '/usr/src/soid/examples/gui/duckietown-soid/src/webserver/soid_query.py',
                                '/usr/src/soid/examples/gui/benchmarks/queries' + '/' + model + '/' + test + '.json' ],
                              capture_output = True, text = True ).stdout.rsplit('\n##################\n## FINISHED KLEE #\n##################\n')[ 1 ]

        # this is morally rephensible, but it works and I'm lazy
        search    = pattern.match( res.splitlines()[ 0 ] ).groups()
        result    = eval( search[ 0 ] )
        resources = eval( search[ 1 ] )

        runs.append( ( result, resources[ 'time' ][ 'symbolic' ], resources[ 'time' ][ 'verification' ], resources[ 'time' ][ 'total' ], resources[ 'paths' ] ) )

        return reduce( lambda acc, r: ( acc[ 0 ] and r[ 1 ][ 0 ],
                                        amend( acc[ 1 ], r[ 0 ], r[ 1 ][ 1 ] ),
                                        amend( acc[ 2 ], r[ 0 ], r[ 1 ][ 2 ] ),
                                        amend( acc[ 3 ], r[ 0 ], r[ 1 ][ 3 ] ),
                                        r[ 1 ][ 4 ] ), enumerate( runs ), ( True, 0.0, 0.0, 0.0, 0 ) )


def execute( tests ):
    add = ''
    for test in tests:
        add += f'    ---{chr(92)}rule{{0pt}}{{2.5ex}} & {chr(92)}multicolumn{{5}}{{l}}{{{test[ 1 ]}}}{chr(92)}{chr(92)}{chr(92)}midrule\n'

        for model in [ 'standard', 'impatient', 'pathological' ]:
            results = ( test[ 0 ], model )
            add += f'   {model} & {mark(results[ 0 ])} & {results[ 1 ]:.3e} & {results[ 2 ]:.3e} & {results[ 3 ]:.3e} & {results[ 4 ]}{chr(92)}{chr(92)}{chr(92)}midrule'

    return add


if __name__ == '__main__':

    base = '''
\documentclass{article}

\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{pifont}
\newcommand{\cmark}{\ding{52}}%
\newcommand{\xmark}{\ding{56}}%
\usepackage{tabularx, booktabs}
\newcolumntype{Y}{>{\centering\arraybackslash}X}
\usepackage{fullpage}
\usepackage{hhline}

\begin{document}

\scriptsize

$$\begin{tabularx}{\textwidth}{c *{5}{Y}}

\toprule
    \multicolumn{2}{c|}{} & \multicolumn{3}{c|}{\vspace{1mm}\underline{timings}} & \multicolumn{1}{c}{}\\
    \textbf{model} & \textbf{output} & \textbf{total ($s$)} & \textbf{symbolic ($s$)} & \textbf{solving ($s$)} & \textbf{paths} \\[2pt]\midrule
'''

    execute(
        [
            ( 'moved', '$\\varphi_{fact}$, \\textit{moved?}' ),
            ( 'always_move', '$\\varphi^* \equiv \\varphi_{fact}[(\\texttt{agent1\_signal\_choice} = 2) \mapsto (\\texttt{agent1\_signal\_choice} \in \{ 0, \, 1, \, 2 \})]$, \\textit{always move?}' ),
            ( 'ever_not_move', '$\\varphi^* \equiv \\varphi_{fact}[(\\texttt{agent1\_signal\_choice} = 2) \mapsto (\\texttt{agent1\_signal\_choice} \in \{ 0, \, 1, \, 2 \})]$, \\textit{ever not move?}' ),
            ( 'range_always_move', '$\\varphi^*[(\\texttt{agent1\_pos\_z} = 1.83) \mapsto (1.65 \leq \\texttt{agent1\_pos\_z} \leq 2.0) ]$, \\textit{always move?}' ),
            ( 'range_ever_not_move', '$\\varphi^*[(\\texttt{agent1\_pos\_z} = 1.83) \mapsto (1.65 \leq \\texttt{agent1\_pos\_z} \leq 2.0) ]$, \\textit{ever not move?}' ),
            ( 'car_always_move', '$\\varphi^* \land (\\texttt{agent2\_pos\_x} = X.X) \land (\\texttt{agent2\_pos\_z} = X.X) \land \cdots$, \\textit{always move?}' ),
            ( 'car_ever_not_move', '$\\varphi^* \land (\\texttt{agent2\_pos\_x} = X.X) \land (\\texttt{agent2\_pos\_z} = X.X) \land \cdots$, \\textit{ever not move?}' ),
        ]
    )

    base += '''
    \bottomrule
    \end{tabularx}$$

    \end{document}
    '''

    print(base)
