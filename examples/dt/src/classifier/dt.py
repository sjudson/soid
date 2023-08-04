import csv
import random
from copy import copy
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.model_selection import train_test_split

if __name__ == '__main__':

    with open( './data/diabetes.csv' ) as csvfile:
        raw  = csv.reader( csvfile )
        raw.__next__()

        data = [ ( list( map( float, row[ :8 ] ) ), int( row[ 8 ] ) ) for row in raw ]
        X, y = zip( *data )
        X, y = list( X ), list( y )

        Xtrain, Xtest, ytrain, ytest = train_test_split( X, y, test_size = 0.2, random_state = 0 )

        dtc = DecisionTreeClassifier( random_state = 0 )
        dtc.fit( Xtrain, ytrain )

        cnames = [ '0', '1' ]
        export_graphviz( dtc, out_file = './tree/dt.dot', class_names = cnames )

        i = None
        for i, X in enumerate( Xtest ):
            cX = copy(X)
            cX[ 5 ] = 1.0

            f  = dtc.predict([X])
            cf = dtc.predict([cX])

            if f != cf:
                break

        avg_i = 54.0
        avg_m = 1.6256
        sqd_m = avg_m ** 2

        xp = Xtest[ i ]
        yp = ytest[ i ]

        bmi = xp[ 5 ]
        kgs = bmi * sqd_m
        lbs = kgs * 2.205

        xp[ 5 ] = avg_i
        xp.insert( 6, lbs )

        with open( './tree/test.in', 'w' ) as fp:
            fp.write( f'{" ".join( map( str, xp ) )}\n{yp}' )
