import argparse


def parse_args():

    parser = argparse.ArgumentParser( description = 'SMT-based oracles for investigating decisions.' )

    parser.add_argument( '-f', '--float', action = 'store_true', type = bool, default = False, dest = 'float', \
                         help = 'Use alternative symbolic execution (KLEE) engine with experimental support for floats.' )
    parser.add_argument( '-c', '--config', action = 'store', type = str, default = None, dest = 'config', required = True \
                         help = 'Location of program configuration file; if not resolveable path it will attempt to load ./{argument}.config.toml.' )
    parser.add_argument( '-q', '--query', action = 'query', type= str, default = None, dest = 'query', required = True \
                         help = 'Location of query file; if not resolveable path it will attempt to load ./{argument}.query.toml.' )


    return parser.parse_args()





if __name__ == '__main__':

    args = parse_args()
