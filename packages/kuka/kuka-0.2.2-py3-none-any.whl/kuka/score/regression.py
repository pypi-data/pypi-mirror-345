import sklearn.metrics
import pandas as pd
import numpy as np

from .. import utils


def rmse(v_real,v_pred):
  return np.sqrt(sklearn.metrics.mean_squared_error(v_real,v_pred)) #leia sobre sklearn.metrics.mean_squared_error
def r2(v_real,v_pred):
  return sklearn.metrics.r2_score(v_real,v_pred) #leia sobre sklearn.metrics.r2_score
def mape(v_real,v_pred):
  return sklearn.metrics.mean_absolute_percentage_error(v_real,v_pred) #https://scikit-learn.org/stable/modules/model_evaluation.html#mean-absolute-percentage-error
def c_coeff(v_real = 'class numpy.ndarray',
            v_pred = 'class numpy.ndarray'
            ): #https://www.sciencedirect.com/science/article/abs/pii/S0376738817311572?via%3Dihub
  '''
  Coeficiente proposto por Wessling et al (1997) (https://doi.org/10.1016/0376-7388(93)E0168-J)

  The neural network works predictively if C is smaller than 1. For C=l, the
  predicted permeability for an unknown polymer would be  equal to the average
  permeability of all polymers presented in the set (which is, in fact, useless).

  '''
  import numpy as np
  v_real = v_real.ravel()
  v_pred = v_pred.ravel()
  denominador = sum(abs(v_real.mean() - v_real))
  if denominador!=0:
    return sum(abs(v_pred-v_real))/denominador
  else:
    return np.nan
  

@utils.__input_type_validation
def display_score(
    m,
    x_train,
    x_test,
    y_train,
    y_test,
    delog_y=False,
    base=10,
    untransform_y = 'Zscore or normalize',
    dict_params_transform = 'dicionario parametros',
    
    _input_type_dict = {
      'm': object,
      'x_train': np.ndarray,
      'x_test': np.ndarray,
      'y_train': np.ndarray,
      'y_test': np.ndarray,
      'delog_y': bool,
      'base': (int, float),
      'untransform_y': str,
      'dict_params_transform': dict
    }
    
    ) -> pd.DataFrame:
  '''
  função para avaliar RMSE, R2 e OOB_score
  
  Exemplo de dict_params_transform para Zscore:
  dict_params_transform = {'mean':'mean_value_for_target_variable', 'std':'std_value_for_target_variable'}
  Exemplo de dict_params_transform para normalize:
  IMPLEMENTAR AINDA
  '''
  y_train_pred = m.predict(x_train)
  y_test_pred = m.predict(x_test)


  if (untransform_y!='Zscore or normalize'):
    if (untransform_y=='Zscore'):
      y_train_pred = y_train_pred*dict_params_transform['std'] + dict_params_transform['mean']
      y_test_pred = y_test_pred*dict_params_transform['std'] + dict_params_transform['mean']
      y_train = y_train*dict_params_transform['std'] + dict_params_transform['mean']
      y_test = y_test*dict_params_transform['std'] + dict_params_transform['mean']
  if (delog_y==True):
    y_train_pred = np.power(base, y_train_pred)
    y_test_pred = np.power(base, y_test_pred)
    y_train = np.power(base,y_train)
    y_test = np.power(base,y_test)

  res = [ [rmse( y_train,y_train_pred ), r2( y_train,y_train_pred ),
           mape( y_train,y_train_pred ), c_coeff( y_train,y_train_pred )],
          [rmse( y_test,y_test_pred ), r2( y_test,y_test_pred ),
           mape( y_test,y_test_pred ), c_coeff( y_test,y_test_pred )] ]
           #a função display score irá retornar uma tabela

  score = pd.DataFrame(res, columns=['RMSE','R2','MAPE','C_coeff'], index = ['Treino','Teste'])

  if hasattr(m, 'oob_score_'): #https://www.programiz.com/python-programming/methods/built-in/hasattr

    if (delog_y==False):
      score.loc['OOB'] = [rmse(y_train, m.oob_prediction_), m.oob_score_,
                          mape(y_train, m.oob_prediction_), c_coeff(y_train,m.oob_prediction_)]
    else:
      y_train_pred = np.power(base, m.oob_prediction_)
      score.loc['OOB'] = [rmse(y_train, y_train_pred), m.oob_score_,
                          mape(y_train, y_train_pred), c_coeff(y_train,y_train_pred)]

  return score



@utils.__input_type_validation
def predictions_separate_by_a_variable(
    model,
    x_train,
    x_test,
    y_test,
    variable_in_original_databank, #coluna
    original_databank_train,
    original_databank_test,
    variable_subgroup = 'all', #coluna_subgrupo
    delog_y = False,
    base = 10,
    untransform_y = 'Zscore or normalize',
    dict_params_transform = 'dicionario parametros',

    _input_type_dict = {
        'model': object,
        'x_train': np.ndarray,
        'x_test': np.ndarray,
        'y_test': np.ndarray,
        'variable_in_original_databank': str,
        'original_databank_train': pd.DataFrame,
        'original_databank_test': pd.DataFrame,
        'variable_subgroup': (list, str),
        'delog_y': bool,
        'base': (int, float),
        'untransform_y': str,
        'dict_params_transform': dict,
    }
    
    ) -> pd.DataFrame:
    '''
    DEFINIÇÕES E HIPÓTESES:
    Denomina-se databank original como aquele cujos valores não passaram por
    transformações (encoders, padronização, normalização etc.), que são
    iguais/semelhantes ao escrito na fonte de referência.
    A conexão entre os conjuntos de teste/treino e os databanks originais são
    estabelecidos pelos índices dos mesmos.

    model = modelo
    x_train = conjunto de treino com variáveis de entrada
    x_test = conjunto de teste com variáveis de entrada
    y_test = conjunto de teste com variáveis alvo
    variable_in_original_databank = COLUNA CATEGÓRICA cujos valores ÚNICOS
                                    servirão como referência para separar as
                                    predições
    original_databank_train = databank original, com valores originais NÃO
                                escalonados e sem transformações do conjunto de
                                treino
    original_databank_test = databank original, com valores originais NÃO
                            escalonados e sem transformações do conjunto de
                            teste
    subgroup = COLUNA CATEGÓRICA cujos valores ÚNICOS servirão como referência
                para separar as predições em subgrupos (OPCIONAL)

    Exemplo de dict_params_transform para Zscore:
    dict_params_transform = {'mean':'mean_value_for_target_variable', 'std':'std_value_for_target_variable'}
    Exemplo de dict_params_transform para normalize:
    IMPLEMENTAR AINDA
    '''
    #R2 para cada conjunto de teste separado por "gases"
    tabela = pd.DataFrame([], columns=[ 'fração_treino (%)','fração_teste (%)', 'R2_teste', 'RMSE_teste', 'MAPE_teste', 'C_coeff_teste' ] )

    #Pegar a COLUNA ORIGINAL de "variable" (valores originais direto do databank de origem)
    original_column_x_test = original_databank_test.loc[ x_test.index.values, variable_in_original_databank ]
    original_column_x_train = original_databank_train.loc[ x_train.index.values, variable_in_original_databank ]

    #Fração treino & Fração teste
    x_train_size = int(x_train.shape[0])
    x_test_size = int(x_test.shape[0])

    unique_values = set(original_column_x_test.unique().tolist() + original_column_x_train.unique().tolist())
    for i in unique_values:
        #print('    i=',i)
        index_i = original_column_x_test.loc[ original_column_x_test==i ].index
        separate_x_test = x_test.loc[ index_i ]
        separate_y_test = y_test.loc[ index_i ]

        #Tamanho da Fração treino & Fração teste
        index_i_x_train = original_column_x_train.loc[ original_column_x_train==i ].index
        separate_x_train_size = int(index_i_x_train.size)
        separate_x_test_size = int(separate_x_test.shape[0])

        #Salvar parametros na tabela
        fracao_treino = np.nan if x_train_size==0 else (separate_x_train_size/x_train_size)
        fracao_teste  = np.nan if x_test_size==0 else (separate_x_test_size/x_test_size)

        if (index_i.size==0):
            resultados_teste = [np.nan]*4
        else:
            valor_real = separate_y_test.values
            valor_predito = model.predict(separate_x_test.values)
            #destransformar Y
            if (untransform_y != 'Zscore or normalize'):
                if (untransform_y == 'Zscore'):
                    valor_real = valor_real*dict_params_transform['std'] + dict_params_transform['mean']
                    valor_predito = valor_predito*dict_params_transform['std'] + dict_params_transform['mean']
            #deslogaritmizar Y
            if (delog_y == True):
                valor_real = np.power( base, valor_real )
                valor_predito = np.power( base, valor_predito )

            resultados_teste = [r2( valor_real, valor_predito ),
                                rmse( valor_real, valor_predito ),
                                mape( valor_real, valor_predito ),
                                c_coeff( valor_real, valor_predito )]

        tabela.loc[ i ] = [f'{fracao_treino:.2%} ({separate_x_train_size})',
                        f'{fracao_teste:.2%} ({separate_x_test_size})',
                        f'{resultados_teste[0]:.5}',
                        f'{resultados_teste[1]:.5}',
                        f'{resultados_teste[2]:.5}',
                        f'{resultados_teste[3]:.5}']


        #laço para os subgrupo 'i' dentro do grupo 'i' - mesma lógica do codigo escrito acima
        if variable_subgroup!='all':
            subgroup_original_column_x_test = original_databank_test.loc[ index_i, variable_subgroup ]
            subgroup_original_column_x_train = original_databank_train.loc[ index_i_x_train, variable_subgroup ]

            x_train_size_subgroup = int(index_i_x_train.size)
            x_test_size_subgroup = int(index_i.size)

            #print('treino=',x_train_size_subgroup)
            #print('teste=',x_test_size_subgroup)
            #print()

            unique_values_subgroup = set(subgroup_original_column_x_test.unique().tolist() + subgroup_original_column_x_train.unique().tolist())
            for j in unique_values_subgroup:
                #print('j=',j)
                index_i = subgroup_original_column_x_test.loc[ subgroup_original_column_x_test==j ].index
                separate_x_test = x_test.loc[ index_i ]
                separate_y_test = y_test.loc[ index_i ]

                #Tamanho da Fração treino & Fração teste
                index_i_x_train = subgroup_original_column_x_train.loc[ subgroup_original_column_x_train==j ].index
                separate_x_train_size = int(index_i_x_train.size)
                separate_x_test_size = int(separate_x_test.shape[0])

                #Salvar parametros na tabela
                fracao_treino = np.nan if x_train_size_subgroup==0 else (separate_x_train_size/x_train_size_subgroup)
                fracao_teste  = np.nan if x_test_size_subgroup==0 else (separate_x_test_size/x_test_size_subgroup)

                if (index_i.size==0):
                    resultados_teste = [np.nan]*4
                else:
                    valor_real = separate_y_test.values
                    valor_predito = model.predict(separate_x_test.values)
                    #destransformar Y
                    if (untransform_y != 'Zscore or normalize'):
                        if (untransform_y == 'Zscore'):
                            valor_real = valor_real*dict_params_transform['std'] + dict_params_transform['mean']
                            valor_predito = valor_predito*dict_params_transform['std'] + dict_params_transform['mean']
                    #deslogaritmizar Y
                    if (delog_y == True):
                        valor_real = np.power( base, valor_real )
                        valor_predito = np.power( base, valor_predito )
                    
                    resultados_teste = [r2( valor_real, valor_predito ),
                                        rmse( valor_real, valor_predito ),
                                        mape( valor_real, valor_predito ),
                                        c_coeff( valor_real, valor_predito )]

                tabela.loc[ str(i)+' / '+str(j) ] = [f'{fracao_treino:.2%} ({separate_x_train_size})',
                                                    f'{fracao_teste:.2%} ({separate_x_test_size})',
                                                    f'{resultados_teste[0]:.5}',
                                                    f'{resultados_teste[1]:.5}',
                                                    f'{resultados_teste[2]:.5}',
                                                    f'{resultados_teste[3]:.5}'
                                                    ]


    valor_real = y_test.values
    valor_predito = model.predict(x_test.values)
    #destransformar Y
    if (untransform_y != 'Zscore or normalize'):
        if (untransform_y == 'Zscore'):
            valor_real = valor_real*dict_params_transform['std'] + dict_params_transform['mean']
            valor_predito = valor_predito*dict_params_transform['std'] + dict_params_transform['mean']
    #deslogaritmizar Y
    if (delog_y == True):
        valor_real = np.power( base, valor_real )
        valor_predito = np.power( base, valor_predito )


    tabela.loc[ 'all' ] = [f'100% ({x_train_size})',
                            f'100% ({x_test_size})',
                            f'{r2( valor_real, valor_predito):.5}',
                            f'{rmse( valor_real, valor_predito):.5}',
                            f'{mape( valor_real, valor_predito):.5}',
                            f'{c_coeff( valor_real, valor_predito):.5}'
                            ]
    
    return tabela