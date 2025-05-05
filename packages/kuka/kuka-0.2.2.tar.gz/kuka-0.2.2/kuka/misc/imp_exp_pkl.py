import pickle
import os
import datetime

from .. import utils

@utils.__input_type_validation
def import_pkl(
    path,

    _input_type_dict = {
            'path': str,
            }
            
    ) -> object:
  
  '''
  This function returns a an variable after define it according to a pickle file in "path".
  "path" NEEDS contain the name of the file.
  '''

  with open( path, 'rb') as f:
    variable = pickle.load(f)
    print('Imported variable:',type(variable))

  return variable

@utils.__input_type_validation
def export_pkl(
  variable,
  path = 'default', #path for store the variable
  
  _input_type_dict = {
    'variable': object,
    'path': str,
    },
    
    ) -> None:
  '''
  This function exports a variable of python as pickle file to the "path".
  "path" NEEDS contain the name of the file.
  '''

  time = datetime.datetime.now()

  if path == 'default':
        filename = f"var_{time.strftime('%Y_%m_%d_%Hh%Mmin_%S_%f')}.pkl"
        path = os.path.join(os.getcwd(), filename)

  with open( path, 'wb' ) as f:
    pickle.dump( variable, f)
    print('Exported variable:',type(variable))