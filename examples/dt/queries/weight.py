from soid.soidlib import *

from .classify import declare

soid = Soid( 'weight', counterfactual.single, priority = 2 )
soid.register( declare )

@soid.register
def descriptor():
    return f'\n\tfinding weight with different outcome...'

@soid.register
def environmental( E ):
    return And( Equal ( E.Pregnancies,                1.0   ),
                Equal ( E.Glucose,                  199.0   ),
                Equal ( E.BloodPressure,             76.0   ),
                Equal ( E.SkinThickness,             43.0   ),
                Equal ( E.Insulin,                    0.0   ),
                Equal ( E.Weight,                   249.973 ),
                Equal ( E.DiabetesPedigreeFunction,   1.394 ),
                Equal ( E.Age,                       22.0   ) )

@soid.register
def falsified( E ):
    return And( Equal ( E.Pregnancies,                1.0   ),
                Equal ( E.Glucose,                  199.0   ),
                Equal ( E.BloodPressure,             76.0   ),
                Equal ( E.SkinThickness,             43.0   ),
                Equal ( E.Insulin,                    0.0   ),
                Equal ( E.Height,                    54.0   ),
                Equal ( E.Weight,                   249.973 ),
                Equal ( E.DiabetesPedigreeFunction,   1.394 ),
                Equal ( E.Age,                       22.0   ) )

@soid.register
def state( S ):
    return True

@soid.register
def behavior( D ):
    return Equal( D.cls, True )
