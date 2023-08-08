from soid.soidlib import *

from .classify import declare

soid = Soid( 'verify', verification, priority = 1 )
soid.register( declare )

@soid.register
def descriptor():
    return f'\n\tverifing output...'

@soid.register
def environmental( E ):
    return And( E.Pregnancies              ==   1.0,
                E.Glucose                  == 199.0,
                E.BloodPressue             ==  76.0,
                E.SkinThickness            ==  43.0,
                E.Insulin                  ==   0.0,
                E.Height                   ==  54.0,
                E.Weight                   == 249.973,
                E.DiabetesPedigreeFunction ==   1.394,
                E.Age                      ==  22.0    )

@soid.register
def state( S ):
    return True


@soid.register
def behavior( D ):
    return D.cls == False
