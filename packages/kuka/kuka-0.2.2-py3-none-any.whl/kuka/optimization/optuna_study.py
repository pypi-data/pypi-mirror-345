from sklearn.metrics import make_scorer
import sklearn
import numpy as np
import optuna
from pathlib import Path
import os

from ..score.metrics import *
from ..misc.imp_exp_pkl import import_pkl, export_pkl
from ..utils import _is_valid_path

class optuna_study:
    '''
    '''

    def __init__(self,
                 model:object,
                 x_train:pd.DataFrame,
                 y_train:pd.DataFrame,
                 
                 study:object|str = 'new', # Can be "new", a path of a pickle file or a object
                 study_name:str = None,
                 direction:str = None, #'minimize' OR 'maximize'
                 ):
        
        self.model = model
        self.x_train = x_train
        self.y_train = y_train
        
        #DEFINE "self.study", "self.study_name", "self.direction", "self.scorer", self.
        if study == 'new':
            self.study_name = study_name #if study_name is not None else None
            self.direction = direction
            self.scorer = None
            self._objective_mode = None
            self._create_study()
            self.describe_study()
        elif isinstance(study, str):
            self.study_path = study
            msg = 'optuna_study ERROR: "study" is not a valid path'
            assert _is_valid_path(self.study_path, type_path = 'file'), msg
            self._import_study()
        elif isinstance(study, optuna.study.study.Study):
            self.study = study
            self.study_name = self.study.study_name
            self.direction = self.study.direction
            self.scorer = None
            self._objective_mode = None
            self.describe_study()
        elif isinstance(study, optuna_study):
            msg = 'Study is a "optuna_study class". optuna_study returned'
            raise TypeError(msg)
        else:
            raise TypeError('"study" is not  valid')
    
    def _create_study(self) -> None:
        self.study = optuna.create_study(
            study_name = self.study_name,
            direction = self.direction
            )
        # Update the self.study_name and self.direction which was None
        self.study_name = self.study.study_name
        self.direction = self.study.direction
        print('new study created: ', self.study_name)
        print()

    def _import_study(self) -> None:
        imported_obj = import_pkl(path=self.study_path)
        if isinstance(imported_obj, optuna.study.study.Study ):
            self.study = imported_obj
            self.study_name = self.study.study_name
            self.direction = self.study.direction
            self.scorer = None
            self._objective_mode = None
            self.describe_study()
        elif isinstance(imported_obj, optuna_study):
            msg = 'Study is a "optuna_study class". optuna_study returned'
            raise TypeError(msg)
        else:
            self.study = None
            msg = 'optuna_study ERROR: the file imported is not of type "optuna study object" or a "optuna_study class" '
            raise TypeError(msg)

    def describe_study(self) -> None:
        dict_direc = {1:'Minimize', 2:'Maximize'}
        print('Name: ', self.study_name)
        print('Model: ', self.model)
        if len(self.study.trials) > 0:
            print('Trial(s): ', len(self.study.trials), ' | Best value: ', self.study.best_value)
        else:
            print('Trial(s): ', len(self.study.trials),' | Best value: None')
        print('Dataset: ', self.x_train.shape[0], 'rows, ', self.x_train.shape[1], 'columns', )
        print('Direction: ', dict_direc[self.direction], ' | Scorer:', self.scorer)
        use_cv = True if self._objective_mode == 'cv' else False
        print('Objective function use Cross-Validation: ', use_cv)
        print()



    def set_objective_conditions(self, 
                       hparams_cat:dict = None, 
                       hparams_int:dict = None, 
                       hparams_float:dict = None, 
                       model_locals:dict = None, #kargs of the model object
                       
                       mode:str = 'default', # ['default','cv']

                       scorer:object = None,
                       scorer_locals:dict = {}, #DICT: kargs of the scorer function. dictionary where key = name of function
                       
                       cv_scorers:str|object = None, #string or function(y_true, y_pred) or sklearn.metrics object. It can be a list of these things
                       cv_scorers_weight:float|int = None, # list of the weights of each score function.
                       cv:int = 5,
                       use_cv_train:bool = False,
                       cv_train_weight:float|int = 0, #range of 0-1
                       
                       fobj_mult = 1000
                       ) -> None:
        
        '''
        The hparams (hyperparameters) must have the format:
            `hparams = { attribute_name : [ optuna_suggest_args, optuna_suggest_kargs ] }`
        where:
            `attribute_name -> str`
            `optuna_suggest_args -> (list, tuple)`
            `optuna_suggest_kargs -> dict`

        cv_scorers -> string or function(y_true, y_pred) or list of strings/functions
                object sklearn.metrics https://scikit-learn.org/stable/api/sklearn.metrics.html
        '''

        if mode=='default':
            msg = 'Set a score in `scorer`'
            assert scorer is not None, msg

        if mode=='cv':
            msg = 'Set a score in `cv_scorers` or a cross-validation number splitting'
            assert all( [cv_scorers is not None, cv is not None] ), msg

        
        # ACCORDING TO THE METRICS AVAILABLE IN THIS LIBRARY (KUKA) (IN SCORE.METRICS)
        scorers_class_list = ['neg_r2', 'r2', 'rmse', 'mape']

        # ENSURE THAT "cv_scorers" IS A LIST OF SCORES FUNCTION OR THAT "scorer" IS A SCORES FUNCTION
        if mode=='cv':
            if not( isinstance(cv_scorers, (list, tuple)) ):
                cv_scorers = [cv_scorers]

            for i, string in enumerate(cv_scorers):
                if isinstance(string, str):
                    if string in scorers_class_list:
                        cv_scorers[i] = eval(string)
                    else:
                        raise AssertionError(f'OBJECTIVE FUNCTION ERROR: The scorer name doesnt exist in scorers class list {scorers_class_list}')
            
            cv_scorers_name = [func.__name__ for func in cv_scorers]
            cv_scorers = [ make_scorer(func) for func in cv_scorers ]
            cv_scorers = dict( zip(cv_scorers_name, cv_scorers) )

            if not(cv_scorers_weight):
                cv_scorers_weight = np.array( [1]*len(cv_scorers) )

            self.scorer = cv_scorers

        elif mode=='default':
            if isinstance(scorer, str):
                if scorer in scorers_class_list:
                    scorer = eval(scorer)
                else:
                    raise AssertionError(f'OBJECTIVE FUNCTION ERROR: The scorer name doesnt exist in scorers class list {scorers_class_list}')
        
            self.scorer = scorer
        
        # store the Fobj parameters
        self._objective_mode = mode
        self._fobj_mult = fobj_mult

        self._objective_mode_default = {
            'scorer': scorer,
            'scorer_locals': scorer_locals
        }
        
        self._objective_mode_cv = {
            'cv_scorers': cv_scorers,
            'cv_scorers_weight': cv_scorers_weight,
            'cv': cv,
            'use_cv_train': use_cv_train,
            'cv_train_weight': cv_train_weight
        }

        self._hparams = {
            'cat': hparams_cat,
            'int': hparams_int,
            'float': hparams_float,
            'model': model_locals
        }
    

    def _create_objective(self) -> object:
        ''' Define objective function '''

        def objective(trial) -> float:
            #####################################################################################
            #################### SET THE RANGE SEARCH OF THE HYPERPARAMETERS ####################
            #####################################################################################
            model_kargs = {}

            if self._hparams['cat']:
                for arg, values in self._hparams['cat'].items():
                    msg = '`hparams_cat` doesnt have a list of strings'
                    assert isinstance(values, (list, tuple)), msg
                    model_kargs[arg] = trial.suggest_categorical( arg, values )

            if self._hparams['int']:
                for arg, values in self._hparams['int'].items():
                    if len(values)==1 or not( isinstance(values[1], dict) ):
                        values = [ values, {} ]
                    model_kargs[arg] = trial.suggest_int( arg, *values[0], **values[1] )

            if self._hparams['float']:
                for arg, values in self._hparams['float'].items():
                    if len(values)==1 or not( isinstance(values[1], dict) ):
                        values = [ values, {} ]
                    model_kargs[arg] = trial.suggest_float( arg, *values[0], **values[1] )

            #####################################################################################
            #################### SET THE RANGE SEARCH OF THE HYPERPARAMETERS ####################
            #####################################################################################
            
            # DEFINE THE MODEL
            if self._hparams['model']:
                for arg, values in self._hparams['model'].items():
                    model_kargs[arg] = values
            
            model = self.model(
                **model_kargs
            )            

            # RETURN THE OBJECTIVE VALUE
            mode = self._objective_mode
            cv = self._objective_mode_cv['cv']

            if mode=='cv' and isinstance(cv, int):
                cv_scorers = self._objective_mode_cv['cv_scorers']
                use_cv_train = self._objective_mode_cv['use_cv_train']
                cv_train_weight = self._objective_mode_cv['cv_train_weight']
                cv_scorers_weight = self._objective_mode_cv['cv_scorers_weight']

                cv_result = sklearn.model_selection.cross_validate(
                    estimator = model,
                    X = self.x_train.values,
                    y = self.y_train.values.ravel(),
                    scoring = cv_scorers,
                    cv = cv,
                    return_train_score = use_cv_train,
                    )

                fobj = []
                for i, score_name in enumerate(cv_scorers.keys()):
                    fobj += [(1-cv_train_weight)*cv_result['test_'+score_name].mean()]
                    if use_cv_train:
                        fobj[i] += cv_train_weight*cv_result['train_'+score_name].mean()

                return float( np.average( np.array(fobj), weights=cv_scorers_weight) )*self._fobj_mult

            elif mode=='default':
                scorer = self._objective_mode_default['scorer']
                scorer_locals = self._objective_mode_default['scorer_locals']

                model.fit(self.x_train.values, self.y_train.values.ravel())
                y_pred = model.predict(self.x_train.values)
                return float( scorer(self.y_train.values, y_pred, **scorer_locals) )*self._fobj_mult
        
        return objective
    
    


    def optimize(self,
                 n_trials:int,
                 stop_criterium:str = 'n_trials', #'n_trials', 'best_score_gradient', 'flex_range'
                 
                 checkpoint:int = None,
                 checkpoint_path:str = None,
                 timeout:int = 10, #seconds
                 
                 score_gradient:float = None,
                 min_runs_score_gradient:int = 3,

                 set_flex_protocol:dict = None
                 ) -> None:
        '''
        'n_trials' -> Trials of one optimization run. The optimization will stop after n_trials.
        'best_score_gradient' -> The optimization will stop after the difference of the best scores from the last optimization runs is less than "score_gradient.
        'flex_range' -> After each optimization run, the range (min and max) of the numerical hyperparameters will increase if their best value is on the boundary of the search range
        '''
        
        optuna.logging.set_verbosity(optuna.logging.WARNING)
        
        stop_criterium_list = ['n_trials', 'best_score_gradient', 'flex_range']
        if stop_criterium not in stop_criterium_list:
            raise ValueError(f'`stop criterion` must be a value in the list {stop_criterium_list}')

        if stop_criterium=='best_score_gradient' and score_gradient is None:
            raise ValueError(f'Set a value for `score_gradient`')
        
        if stop_criterium=='flex_range' and set_flex_protocol is None:
            raise ValueError(f'Set a value for `set_flex_protocol`')
        

        #DEFINE THE OBJECTIVE FUNCTION
        fobj = self._create_objective()

        best_scores = []
        run = 0
        
        
        while True:
            print()
            print(f'############# RUN {run+1} #############')
            
            # RUN OPTIMIZATION
            existing_trials = len(self.study.trials)
            if checkpoint:

                number_of_loops = int(n_trials/checkpoint) + 1

                for batch in range(number_of_loops):
                    total_timeout = checkpoint*timeout
                    if not(batch == number_of_loops - 1):
                        self.study.optimize(
                            fobj,
                            n_trials = checkpoint,
                            show_progress_bar=True,
                            timeout = total_timeout
                            )
                        total_trials = existing_trials + batch*checkpoint + checkpoint

                    else:
                        if (n_trials%checkpoint!=0):
                            total_timeout = n_trials%checkpoint*timeout
                            self.study.optimize(
                                fobj,
                                n_trials = n_trials%checkpoint,
                                show_progress_bar=True,
                                timeout = total_timeout
                                )
                            total_trials = existing_trials + int(n_trials/checkpoint)*checkpoint + (n_trials%checkpoint)
                        else:
                            continue

                    # Export backup .pkl file
                    if checkpoint_path:
                        # IF checkpoint_path IS A REAL DIRECTORY
                        if _is_valid_path(checkpoint_path, type_path='dir'):
                            export_pkl( self, path=os.path.join(checkpoint_path,f'{self.study_name}_{total_trials}_trials.pkl') )
                        # IF checkpoint_path IS A REAL FILE
                        elif _is_valid_path(checkpoint_path, type_path='file'):
                            raise FileExistsError('WARNING: This file already exists. `checkpoint_path` is not a valid path.')
                        # IF checkpoint_path SYNTAX IS VALID
                        elif _is_valid_path(checkpoint_path, check_only_syntax=True):
                            checkpoint_path_object = Path(checkpoint_path)
                            dir_name = os.path.dirname(checkpoint_path_object)
                            if dir_name:
                                os.makedirs(os.path.dirname(checkpoint_path_object), exist_ok=True)
                            file_name = f'{checkpoint_path_object.stem}_{total_trials}_trials{checkpoint_path_object.suffix}'
                            export_pkl( self, path=str(checkpoint_path_object.with_name(file_name)) )
                        #IF checkpoint_path SYNTAX IS NOT VALID
                        else:
                            print('ok1')
                            export_pkl(self) #this will export the .pkl in actual path with the default "export_pkl" name
                            print('WARNING: `checkpoint_path` is not a valid path. File name of study was exported as datetime')
                    else:
                        export_pkl(self) #this will export the .pkl in actual path with the default "export_pkl" name
                        print('WARNING: no `checkpoint_path` defined. File name of study was exported as datetime')
                    
            else:
                total_timeout = n_trials*timeout
                self.study.optimize(
                        fobj, 
                        n_trials = n_trials,
                        show_progress_bar=True,
                        timeout = total_timeout
                        )

            run += 1
            
            if stop_criterium == 'n_trials': break
            
            if stop_criterium == 'best_score_gradient':
                best_scores.append(self.study.best_value)
                print(best_scores)
                if run >= min_runs_score_gradient:
                    last_best_scores = best_scores[-min_runs_score_gradient:]
                    diff = np.abs( np.diff( last_best_scores ) )
                    mean_diff = np.mean(diff)

                    display(last_best_scores)
                    display(diff)
                    display(mean_diff)
                    print('score-gradient = ', mean_diff )
                    if mean_diff<=score_gradient:
                        print()
                        print(f'{run*n_trials} trials done')

                        break
            
            if stop_criterium == 'flex_range':
                # hyperparameters of the last trial
                hparams = list(self.study.trials[-1].distributions.keys())
                # hyperparameters distribution of the last trial
                distribution = self.study.trials[-1].distributions

                changes = 0
                for param in set_flex_protocol.keys():
                    if param in hparams:
                        best_value = self.study.best_trial.params[param]
                        min_value = distribution[param].low
                        max_value = distribution[param].high
                        
                        if best_value<=min_value or best_value>=max_value:
                            if (best_value>=max_value):
                                index = 1 #index for maximum
                            else:
                                index = 0 #index for minimum
                            # Search "param" in "_hparams" (variable defined in set_objective_conditions method)
                            for type_hparam, fobj_hparam_dict in self._hparams.items():
                                if param in fobj_hparam_dict.keys():
                                    limit_value = self._hparams[type_hparam][param][0][index] #1-> max, 0->min
                                    protocol = set_flex_protocol[param][index] #1-> max, 0->min
                                    if protocol:
                                        changes += 1
                                        if protocol[0] == 'add':
                                            limit_value += protocol[1]
                                        elif protocol[0] == 'mult':
                                            limit_value *= protocol[1]
                                        else:
                                            raise ValueError(f'Protocol {protocol} is not valid.')
                                        old_limits = self._hparams[type_hparam][param][0].copy()
                                        self._hparams[type_hparam][param][0][index] = limit_value
                                        print(f'> Search range of {param} changed from {old_limits} to {self._hparams[type_hparam][param][0]}')
                
                if changes:
                    # Redefine the objective function
                    fobj = self._create_objective()
                else:
                    print()
                    print(f'{run*n_trials} trials done')
                    
                    break

        optuna.logging.set_verbosity(optuna.logging.INFO)


