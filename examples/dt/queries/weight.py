from soid.soidlib import *

from .classify import declare

soid = Soid( 'weight', counterfactual.single, priority = 2 )
soid.register( declare )

@soid.register
def descriptor():
    return f'\n\tfinding weight with different outcome...'

@soid.register
def environmental( E ):
    return And( E.Pregnancies              ==   1.0,
                E.Glucose                  == 199.0,
                E.BloodPressue             ==  76.0,
                E.SkinThickness            ==  43.0,
                E.Insulin                  ==   0.0,
                E.Height                   ==  54.0,
                E.DiabetesPedigreeFunction ==   1.394,
                E.Age                      ==  22.0    )

@soid.register
def state( S ):
    return True


@soid.register
def behavior( D ):
    return D.cls == True
