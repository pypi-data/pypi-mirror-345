import functools

def __type_validation(input_dict: dict, #dict with the arguments of the function
                      ) -> None:

  # Check if the number of arguments and expected types match
  msg = f'VALIDATION TYPE ERROR: The number of arguments and expected types does not match.\nPlease check the function signature.'
  assert len(input_dict['_input_type_dict']) >= (len(input_dict) - 1), msg  
  
  # Check if the types of the arguments match the expected types
  input_dict_copy = input_dict.copy()
  input_dict_copy = input_dict.pop('_input_type_dict')

  for k, v in input_dict.items():
    msg = f'VALIDATION TYPE ERROR: The argument {k} (type {type(v)}) is not of type {input_dict_copy[k]} (defined in function signature).'
    assert isinstance(v, input_dict_copy[k]), msg


def __input_type_validation(func):
  '''
  Decorator to validate the input types of a function.
  The input types are defined in the function signature.

  The function signature must have a specific `_input_type_dict` default argument.
  The `_input_type_dict` argument must be a list of types like:
  `  _input_type_dict = {
              'variable_name': type, 
              ...
              }
  `
  If theres no constraint for a variable, use `object` as the type.
  '''
  @functools.wraps(func)
  def wrapper(*args, **kwargs):

    #### 1. Get the default arguments from the function signature ####
    # Gets the names of the arguments of the original function
    input_names = func.__code__.co_varnames[:func.__code__.co_argcount]
    # Gets the default values of the arguments (if they exist)
    defaults = func.__defaults__ or ()
    num_defaults = len(defaults)
    # Maps the default arguments to their names
    defaults_dict = dict(zip(input_names[-num_defaults:], defaults))
    # Remove the kwargs from the defaults_dict
    for key in kwargs.keys():
      defaults_dict.pop(key) if key in defaults_dict else None

    ######## 1.1. Verify the existence of the `_input_type_dict` argument ########
    msg = 'VALIDATION FUNCTION ERROR: The `_input_type_dict` argument used for type atribute validation is missing.\n Please add it to the function signature or remove the decorator `__input_type_validation` from the function.'
    assert defaults_dict.get('_input_type_dict'), msg

    #### 2. Create a dictionary with the args and their names ####
    arg_names = input_names[:len(args)]
    args_dict = dict(zip(arg_names, args))

    #### 2.1. Remove the agrs from the defaults_dict ####
    # Sometimes default variables are called like the args, 
    # so we need to remove them from the defaults_dict
    defaults_dict = {k: defaults_dict[k] for k in set( defaults_dict.keys() ) - set( args_dict.keys() )}

    #### 3. Merge the dictionaries with ALL the arguments and its values ####
    input_dict = {**args_dict, **kwargs, **defaults_dict}

    #### 4. Update the _input_type_dict with not_defined arguments in signature function or ####
    ####    with unexplicity types in _input_type_dict ####
    # Sometimes the function is called with arguments that are not defined in its signature or
    # the _input_type_dict does not have the type of some argument.
    foreign_args = {k: input_dict[k] for k in set( input_dict.keys() ) - set( input_dict['_input_type_dict'].keys() )}
    foreign_args.pop('_input_type_dict') if '_input_type_dict' in foreign_args else None
    #Update the _input_type_dict with the foreign arguments and object type (generic type):
    input_dict['_input_type_dict'].update({k: object for k in foreign_args.keys()})

    #### 5. Call the function for validate the arguments ####
    __type_validation(input_dict)

    return func(*args, **kwargs)
  
  return wrapper

