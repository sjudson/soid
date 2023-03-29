import os
import json

if __name__ == '__main__':

    for model in [ 'standard', 'impatient', 'pathological' ]:

        path = f'/usr/src/soid/examples/gui/duckietown-soid/learning/reinforcement/q-learning/models/saved/{model}/10k_train'
        with open( path, 'r' ) as fp:
            qtable = []
            for line in fp.readlines():
                qtable.append( list( map( float, line.split( ',' ) ) ) )


        folder = f'/usr/src/soid/examples/gui/benchmarks/queries/{model}'
        if not os.path.exists( folder ):
            os.makedirs( folder )

        for test in [ 'moved', 'always_move', 'ever_not_move',
                      'range_always_move', 'range_ever_not_move',
                      'car_always_move', 'car_ever_not_move' ]:

            template = f'/usr/src/soid/examples/gui/benchmarks/queries/templates/{test}.json'
            with open( template, 'r' ) as tfp:
                temp = json.loads( tfp.read() )
                temp[ 'environment' ][ 'model' ] = qtable

                generated = f'/usr/src/soid/examples/gui/benchmarks/queries/{model}/{test}.json'
                with open( generated, 'w' ) as gfp:
                    gfp.write( json.dumps( temp ) )
