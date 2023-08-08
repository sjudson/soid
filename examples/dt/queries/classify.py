import soid.soidlib as soidlib


def introduction():
    return f'\n\ttesting buggy decision tree-based decision counterfactuals...'


def declare():

    E = { 'Pregnancies'              : soidlib.types.double( 'Pregnancies',              pp = None, raw = 'data0' ),
          'Glucose'                  : soidlib.types.double( 'Glucose',                  pp = None, raw = 'data1' ),
          'BloodPressure'            : soidlib.types.double( 'BloodPressure',            pp = None, raw = 'data2' ),
          'SkinThickness'            : soidlib.types.double( 'SkinThickness',            pp = None, raw = 'data3' ),
          'Insulin'                  : soidlib.types.double( 'Insulin',                  pp = None, raw = 'data4' ),
          'Height'                   : soidlib.types.double( 'Height',                   pp = None, raw = 'data5' ),
          'Weight'                   : soidlib.types.double( 'Weight',                   pp = None, raw = 'data6' ),
          'DiabetesPedigreeFunction' : soidlib.types.double( 'DiabetesPedigreeFunction', pp = None, raw = 'data7' ),
          'Age'                      : soidlib.types.double( 'Age',                      pp = None, raw = 'data8' ) }

    S = {}

    D = { 'cls' : soidlib.types.bool_as_int_bv( 'cls' ) }

    return E, S, D
