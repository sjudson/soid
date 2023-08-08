import subprocess
import re

from functools import reduce

ITERS = 10

def mark( tval ):
    return '\cmark' if tval else '\\xmark'

def amend( base, i, nxt ):
    return ( base * i + nxt ) / ( i + 1.0 )

def run( test, model ):
    pattern = re.compile( r'Result: ([A-Za-z]+) Resources: (\{.*\})', re.IGNORECASE )

    runs = []
    for i in range( ITERS ):
        res = subprocess.run( [ 'python', '/usr/src/soid/examples/dt/query.py', test ],
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
        add += f'    {test[ 2 ]}{chr(92)}rule{{0pt}}{{2.5ex}} & {chr(92)}multicolumn{{5}}{{|l}}{{{test[ 1 ]}}}{chr(92)}{chr(92)}{chr(92)}midrule\n'

        for model in [ 'dt' ]:
            results = run( test[ 0 ], model )
            add += f'    {model} & {mark(results[ 0 ])} & {results[ 1 ]:.3e} & { results[ 2 ]:.3e} & {results[ 3 ]:.3e} & {results[ 4 ]}{chr(92)}{chr(92)}{chr(92)}midrule\n'

    return add


if __name__ == '__main__':

    base = '''
\documentclass{article}

\\usepackage{amsmath}
\\usepackage{amssymb}
\\usepackage{pifont}
\\newcommand{\cmark}{\ding{52}}%
\\newcommand{\\xmark}{\ding{56}}%
\\usepackage{tabularx, booktabs}
\\newcolumntype{Y}{>{\centering\\arraybackslash}X}
\\usepackage{fullpage}
\\usepackage{hhline}

\\newcommand{\counterfactual}{\ensuremath{%
    \\mathrel{\Box\kern-1.5pt\\raise0.8pt\hbox{\\vspace{10pt}$\mathord{\\rightarrow}$}}}}
\\newcommand{\\fprop}{\ensuremath{\\to_{\\mathcal{A}, t, \ell}}}
\\newcommand{\cprop}{\ensuremath{\counterfactual_{\\mathcal{A}, t^*, \ell}}}

\\begin{document}

\scriptsize

$$\\begin{tabularx}{\\textwidth}{c *{5}{Y}}

\\toprule
    \multicolumn{2}{c|}{} & \multicolumn{3}{c|}{\\vspace{1mm}\\underline{timings (avg.~$n = 10$)}} & \multicolumn{1}{c}{}\\\\
    \\textbf{model} & \\textbf{output} & \\textbf{symbolic ($s$)} & \\textbf{solving ($s$)} & \\textbf{total ($s$)} & \\textbf{paths} \\\\[2pt]\midrule
'''

    base += execute(
        [
            ( 'verify', '$\\varphi_{fact}$, \\textit{high risk?}', '\\fprop' ),
            ( 'weight', '$\\varphi^* \equiv \\varphi_{fact}[(\\texttt{height} = 54.0) \mapsto \\top]$, \\textit{ever high risk?}', '\cprop' ),
        ]
    )

    base += '''
\\bottomrule
\end{tabularx}$$

\end{document}
    '''

    print(base)
