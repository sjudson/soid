import soid.soidlib as soidlib


def introduction():
    return f'\n\ttesting buggy decision tree-based decision counterfactuals...'


def declare():

    E = { 'Pregnancies'              : soidlib.types.double( 'data0' ),
          'Glucose'                  : soidlib.types.double( 'data1' ),
          'BloodPressure'            : soidlib.types.double( 'data2' ),
          'SkinThickness'            : soidlib.types.double( 'data2' ),
          'Insulin'                  : soidlib.types.double( 'data2' ),
          'Height'                   : soidlib.types.double( 'data2' ),
          'Weight'                   : soidlib.types.double( 'data2' ),
          'DiabetesPedigreeFunction' : soidlib.types.double( 'data7' ),
          'Age'                      : soidlib.types.double( 'data2' ) }

    S = {}

    D = { 'cls' : soidlib.types.bool( 'cls' ) }
    
    return E, S, D
