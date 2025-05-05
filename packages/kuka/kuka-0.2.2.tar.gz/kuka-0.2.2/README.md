# 📁 Directory Summary

```
kukalib/
├── LICENSE
├── README.md
├── doc/
│   └── summary_project.txt
├── kuka/
│   ├── __init__.py
│   ├── importance/
│   │   ├── __init__.py
│   │   └── permutation_importance.py
│   ├── info/
│   │   ├── __init__.py
│   │   ├── info.py
│   │   └── texts/
│   │       ├── colors/
│   │       │   ├── def_show_named_plotly_colours.txt
│   │       │   └── matplotlib_colors.txt
│   │       ├── custom_functions/
│   │       │   └── pdp_plot.txt
│   │       ├── matplotlib_api.txt
│   │       └── pickle.txt
│   ├── misc/
│   │   ├── __init__.py
│   │   ├── get_key.py
│   │   └── imp_exp_pkl.py
│   ├── plot/
│   │   ├── __init__.py
│   │   ├── compare_hists_by.py
│   │   ├── draw_tree.py
│   │   ├── heatmap_corr.py
│   │   ├── heatmap_correlations.py
│   │   ├── plot_confusion_matrix.py
│   │   ├── plot_hist_of_columns.py
│   │   ├── plot_permutation_importance.py
│   │   ├── plot_plairplot.py
│   │   ├── plot_predictions.py
│   │   ├── plot_stacked_hist_or_bar_by.py
│   │   ├── plotar_importancias.py
│   │   └── plt_missingno_by.py
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   ├── cat_cols.py
│   │   └── num_cols.py
│   ├── score/
│   │   ├── __init__.py
│   │   ├── categorization.py
│   │   └── regression.py
│   └── utils/
│       ├── __init__.py
│       └── __input_type_validation.py
└── setup.py
```

# 📚 API Reference

## __input_type_validation.py:__input_type_validation
**Parameters:** `func`

**Description:**
```python
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
```

--------------------------------------------------

## __input_type_validation.py:__type_validation
**Parameters:** `input_dict`

**Description:**
```python
No description available
```

--------------------------------------------------

## __input_type_validation.py:wrapper
**Parameters:** ``

**Description:**
```python
No description available
```

--------------------------------------------------

## _plt_hist_of_columns.py:plt_hist_of_columns
**Parameters:** `df, _input_type_dict={'df': type(pd.DataFrame())}`

**Description:**
```python
Plot a histogram for each numeric column of a 
dataframe in a more organized way than just calling pandas hist()
```

--------------------------------------------------

## _plt_hist_of_columns.py:put_labels
**Parameters:** `ax_list`

**Description:**
```python
No description available
```

--------------------------------------------------

## cat_cols.py:str2int_hot_encoder
**Parameters:** `df, columns='all', _input_type_dict={'df': pd.DataFrame, 'columns': (str, list, tuple)}`

**Description:**
```python
No description available
```

--------------------------------------------------

## cat_cols.py:str2int_simple_encoder
**Parameters:** `df, columns='all', _input_type_dict={'df': pd.DataFrame, 'columns': (str, list, tuple)}`

**Description:**
```python
No description available
```

--------------------------------------------------

## categorization.py:classification_metrics
**Parameters:** `y_real, y_pred, _input_type_dict={'y_real': np.ndarray, 'y_pred': np.ndarray}`

**Description:**
```python
No description available
```

--------------------------------------------------

## compare_hists_by.py:compare_hists_by
**Parameters:** `df1, df2, variable='', by='', df1_name='default', df2_name='default', alpha=0.7, bins_hist=1, colors_reference=['b', 'g', 'r', 'c', 'm', 'y', 'k'], figsize=[12.8, 7.2], _input_type_dict={'df1': pd.DataFrame, 'df2': pd.DataFrame, 'variable': str, 'by': str, 'df1_name': str, 'df2_name': str, 'alpha': (float, int), 'bins_hist': int, 'colors_reference': (list, tuple), 'figsize': (list, tuple)}`

**Description:**
```python
"variable" precisa ter valores numéricos.

Essa função retorna "fig" e "ax" do Matplotlib. Portanto, o gráfico criado pode ser editado
posteriormente, mesmo com certa limitação.

A lógica dessa função foi copiada da função "plot_stacked_hist_or_bar_by".
Para melhor compreender esse cógido, ler antes o código da função "plot_stacked_hist_or_bar_by"
```

--------------------------------------------------

## draw_tree.py:draw_tree
**Parameters:** `t, dados, size=10, ratio=1, precision=0, _input_type_dict={'t': object, 'dados': pd.DataFrame, 'size': int}`

**Description:**
```python
No description available
```

--------------------------------------------------

## get_key.py:get_key
**Parameters:** `val, my_dict, default=None, _input_type_dict={'val': object, 'my_dict': dict, 'default': object}`

**Description:**
```python
Given a certain "value" in a dictionary, what is the "key" associated with it?

Returns the key associated with a specific value in a dictionary.

Args:
    val: The value to search for in the dictionary.
    my_dict: The dictionary to search in.
    default: The value to return if the value is not found (default: None).
    
Returns:
    The key associated with the value if found, otherwise the default value.
    
Examples:
    >>> get_key(2, {'a': 1, 'b': 2, 'c': 3})
    'b'
    >>> get_key(5, {'a': 1, 'b': 2, 'c': 3}, "Not found")
    'Not found'
```

--------------------------------------------------

## heatmap_corr.py:heatmap_corr
**Parameters:** `df, x='all', y='all', method='pearson', min_periods=1, color='di', _input_type_dict={'df': pd.DataFrame, 'x': (str, list, str), 'y': (str, list, str), 'method': str, 'min_periods': int, 'color': str}`

**Description:**
```python
No description available
```

--------------------------------------------------

## heatmap_correlations.py:heatmap_correlations
**Parameters:** `method='pearson or spearman', df='pandas_DataFrame', x='all', y='all', allow_duplicates=True, color='di', graphic='coeff', min_periods=2, figsize='default', use_external_fig_and_ax=False, external_fig_and_ax='tuple of fig and ax, respectively', verbose_n_periods=False, _input_type_dict={'method': str, 'df': pd.DataFrame, 'x': (str, list, tuple), 'y': (str, list, tuple), 'allow_duplicates': bool, 'color': str, 'graphic': str, 'min_periods': int, 'figsize': (str, list, tuple), 'use_external_fig_and_ax': bool, 'external_fig_and_ax': (list, tuple), 'verbose_n_periods': bool}`

**Description:**
```python
URGENTLY NEEDED OPTIMIZATION
Returns a heatmap plot with pearson's coefficients or their p-values.

method    = "pearson" or "spearman"
df      = Dataframe
x and y = list of x and y heatmap columns/axis
color   = "di" or "mono"
graphic = "coeff" or "pvalue"
```

--------------------------------------------------

## imp_exp_pkl.py:export_pkl
**Parameters:** `variable, path='default', _input_type_dict={'variable': object, 'path': str}`

**Description:**
```python
This function exports a variable of python as pickle file to the "path".
"path" NEEDS contain the name of the file.
```

--------------------------------------------------

## imp_exp_pkl.py:import_pkl
**Parameters:** `path='default', _input_type_dict={'path': str}`

**Description:**
```python
This function returns a an variable after define it according to a pickle file in "path".
"path" NEEDS contain the name of the file.
```

--------------------------------------------------

## info.py:__getattr__
**Parameters:** `self, name`

**Description:**
```python
No description available
```

--------------------------------------------------

## info.py:__init__
**Parameters:** `self, folder=None, level=0`

**Description:**
```python
No description available
```

--------------------------------------------------

## info.py:_list_dir_content
**Parameters:** `self, just_consult=False`

**Description:**
```python
No description available
```

--------------------------------------------------

## info.py:info.__getattr__
**Parameters:** `self, name`

**Description:**
```python
No description available
```

--------------------------------------------------

## info.py:info.__init__
**Parameters:** `self, folder=None, level=0`

**Description:**
```python
No description available
```

--------------------------------------------------

## info.py:info._list_dir_content
**Parameters:** `self, just_consult=False`

**Description:**
```python
No description available
```

--------------------------------------------------

## info.py:info.ls
**Parameters:** `self`

**Description:**
```python
No description available
```

--------------------------------------------------

## info.py:ls
**Parameters:** `self`

**Description:**
```python
No description available
```

--------------------------------------------------

## num_cols.py:Zscores
**Parameters:** `df_for_scaled, df_reference, _input_type_dict={'df_for_scaled': pd.DataFrame, 'df_reference': pd.DataFrame}`

**Description:**
```python
Escalonar cada coluna de um DataFrame utilizando o "z score"
```

--------------------------------------------------

## num_cols.py:Zscores_with_param
**Parameters:** `df_real, dict_params, _input_type_dict={'df_real': pd.DataFrame, 'dict_params': dict}`

**Description:**
```python
Aplicar o escalonamento zscore para cada coluna de um DataFrame a partir dos parametros 
(média e desvio padrão)

If the variable is an "np.array", its necessary to convert it to a "DataFrame".

Example of dict_params:
dict_params = {
  'columns_dataframe_name1': {'mean':'mean_value1', 'std':'std_value1'},
  'columns_dataframe_name2': {'mean':'mean_value2', 'std':'std_value2'},
  'columns_dataframe_name3': {'mean':'mean_value3', 'std':'std_value3'}
}
```

--------------------------------------------------

## num_cols.py:normalize
**Parameters:** `df_for_norm, df_reference, _input_type_dict={'df_for_norm': pd.DataFrame, 'df_reference': pd.DataFrame}`

**Description:**
```python
Normalizar cada coluna de um DataFrame
```

--------------------------------------------------

## num_cols.py:undo_Zscores
**Parameters:** `df_scaled, df_reference, _input_type_dict={'df_scaled': pd.DataFrame, 'df_reference': pd.DataFrame}`

**Description:**
```python
desfazer o escalonamento realizado para cada coluna de um DataFrame utilizando
o "z score"
```

--------------------------------------------------

## num_cols.py:undo_Zscores_with_param
**Parameters:** `df_scaled, dict_params, _input_type_dict={'df_scaled': pd.DataFrame, 'dict_params': dict}`

**Description:**
```python
desfazer o escalonamento realizado para cada coluna de um DataFrame utilizando
o "z score" a partir dos parametros

If the variable is an "np.array", its necessary to convert it to a "DataFrame".

Example of dict_params:
dict_params = {
  'columns_dataframe_name1': {'mean':'mean_value1', 'std':'std_value1'},
  'columns_dataframe_name2': {'mean':'mean_value2', 'std':'std_value2'},
  'columns_dataframe_name3': {'mean':'mean_value3', 'std':'std_value3'}
}
```

--------------------------------------------------

## num_cols.py:undo_normalize
**Parameters:** `df_normalized, df_reference, _input_type_dict={'df_normalized': pd.DataFrame, 'df_reference': pd.DataFrame}`

**Description:**
```python
desfazer a normalização realizada para cada coluna de um DataFrame
```

--------------------------------------------------

## permutation_importance.py:permutation_importance
**Parameters:** `model, x_val, y_val, n_repeats=5, scoring='r2', _input_type_dict={'model': object, 'x_val': np.ndarray, 'y_val': np.ndarray, 'n_repeats': int, 'scoring': str}`

**Description:**
```python
No description available
```

--------------------------------------------------

## plot_confusion_matrix.py:plot_confusion_matrix
**Parameters:** `y_true, y_pred, labels=None, cmap='Blues', figsize=(6, 5), _input_type_dict={'y_true': (np.ndarray, list), 'y_pred': (np.ndarray, list), 'labels': (list, tuple, None), 'cmap': str, 'figsize': (tuple, list)}`

**Description:**
```python
No description available
```

--------------------------------------------------

## plot_hist_of_columns.py:plot_hist_of_columns
**Parameters:** `df, _input_type_dict={'df': type(pd.DataFrame())}`

**Description:**
```python
Plot a histogram for each numeric column of a dataframe in a
more organized and secury way than just calling pandas hist().

The function recognize and plot histogram only numeric columns
```

--------------------------------------------------

## plot_hist_of_columns.py:put_labels
**Parameters:** `ax_list`

**Description:**
```python
No description available
```

--------------------------------------------------

## plot_permutation_importance.py:plot_permutation_importance
**Parameters:** `model, x_val, y_val, scoring='r2_score', n_repeats=30, height=0.8, espaco_colunas=0.2, figsize=[6.4, 4.8], separar_por_cor=False, bycolor='dict', bar_labels=False, fontsize_bar_labels=10, _input_type_dict={'model': object, 'x_val': pd.DataFrame, 'y_val': pd.DataFrame, 'scoring': str, 'n_repeats': int, 'height': (int, float), 'espaco_colunas': (int, float), 'figsize': (list, tuple), 'separar_por_cor': bool, 'bycolor': dict, 'bar_labels': bool, 'fontsize_bar_labels': (int, float)}`

**Description:**
```python
Exemplo para variável "bycolor"

bycolor = {'variável1':'color1',
           'variável2':'color1',
           'variável3':'color3',
           'variável4':'color1',
           'variável5':'color3',}
```

--------------------------------------------------

## plot_plairplot.py:definicoes_de_cada_grafico
**Parameters:** ``

**Description:**
```python
No description available
```

--------------------------------------------------

## plot_plairplot.py:plot_plairplot
**Parameters:** `df, columns=['all'], color_by='', figsize='default', colors_reference=['black', '#023eff', '#ff7c00', '#1ac938', '#e8000b', '#8b2be2', '#9f4800', '#f14cc1', '#a3a3a3', '#ffc400', '#00d7ff'], dict_colors_of_variable_by=False, wspace=0.12, hspace=0.12, major_label_off=False, tick_labelsize=matplotlib.rcParams['font.size'], tick_format='{x:.4g}', margins=0.08, _input_type_dict={'df': pd.DataFrame, 'columns': (list, tuple), 'color_by': str, 'figsize': (list, tuple, str), 'colors_reference': (list, tuple), 'dict_colors_of_variable_by': (bool, dict), 'wspace': (int, float), 'hspace': (int, float), 'major_label_off': bool, 'tick_labelsize': (int, float), 'tick_format': str, 'margins': (int, float)}`

**Description:**
```python
No description available
```

--------------------------------------------------

## plot_predictions.py:mape
**Parameters:** `v_real, v_pred`

**Description:**
```python
No description available
```

--------------------------------------------------

## plot_predictions.py:plot_predictions
**Parameters:** `y_real='list', y_pred='list', figsize=[15.0, 6.0], y_scale='default', put_major_label_tick_every='default', put_minor_label_tick_every='default', show_error_axis=True, error_axis='absolute or relative', font_size=11.0, report_big_relative_errors=True, big_errors_limit=100, _input_type_dict={'y_real': (list, tuple, np.ndarray), 'y_pred': (list, tuple, np.ndarray), 'figsize': (list, tuple), 'y_scale': str, 'put_major_label_tick_every': (str, int, float), 'put_minor_label_tick_every': (str, int, float), 'show_error_axis': bool, 'error_axis': str, 'font_size': (int, float), 'report_big_relative_errors': bool, 'big_errors_limit': (int, float)}`

**Description:**
```python
No description available
```

--------------------------------------------------

## plot_predictions.py:rmse
**Parameters:** `v_real, v_pred`

**Description:**
```python
No description available
```

--------------------------------------------------

## plot_stacked_hist_or_bar_by.py:plot_stacked_hist_or_bar_by
**Parameters:** `df, variable='', by='', mode='bar or hist', alpha=0.3, colors_reference=['b', 'g', 'r', 'c', 'm', 'y', 'k'], dict_colors_of_variable_by=False, figsize=[6.4, 4.8], width_bar='default', bar_norm=False, bar_labels=False, bins_hist=1, x_log_scale_hist=False, hist_average_line=False, use_external_fig_and_ax=False, external_fig_and_ax='tuple of fig and ax, respectively', verbose=True, _input_type_dict={'df': pd.DataFrame, 'variable': str, 'by': str, 'mode': str, 'alpha': (float, int), 'colors_reference': list, 'dict_colors_of_variable_by': bool, 'figsize': list, 'width_bar': (str, int, float), 'bar_norm': bool, 'bar_labels': bool, 'bins_hist': (float, int), 'x_log_scale_hist': bool, 'hist_average_line': bool, 'use_external_fig_and_ax': bool, 'external_fig_and_ax': (tuple, list), 'verbose': bool}`

**Description:**
```python
Histogramas empilhados por classe "by"
Exemplos semelhantes de grafico de barras: https://matplotlib.org/stable/gallery/lines_bars_and_markers/bar_stacked.html#sphx-glr-gallery-lines-bars-and-markers-bar-stacked-py

Essa função se baseia na criação de dicionários para os valores da base (variável "bottom"
do matplotlib) e das frequencias (variável "height" do matplotlib). As chaves(keys) desses
dicionários são os valores únicos de "df[variable]" e os valores são referentes à frequencia
(obtidas a partir da função "value_counts").

Essa função retorna "fig" e "ax" do Matplotlib. Portanto, o gráfico criado pode ser editado
posteriormente, mesmo com certa limitação.

O modo 'hist' serve apenas para quando "variable" possui valores numéricos.
```

--------------------------------------------------

## plotar_importancias.py:plotar_importancias
**Parameters:** `modelo, tags, n=10, _input_type_dict={'modelo': object, 'tags': (list, tuple), 'n': int}`

**Description:**
```python
No description available
```

--------------------------------------------------

## plt_missingno_by.py:plt_missingno_by
**Parameters:** `df=pd.DataFrame(), variable=[], by='', consider_none=True, consider_zeros=True, library='plotly or matplotlib', matplotlib_figsize='default', matplotlib_bar_space=0.8, matplotlib_colors='default', _input_type_dict={'df': pd.DataFrame, 'variable': list, 'by': str, 'consider_none': bool, 'consider_zeros': bool, 'library': str, 'matplotlib_figsize': (str, list), 'matplotlib_bar_space': (int, float), 'matplotlib_colors': (str, list)}`

**Description:**
```python
Plotar a qtd de valores existentes da variavel="variable" para cada classe da variável "by"

OBS.:
- A espessura das barras é controlada pela largura (width) da figura
```

--------------------------------------------------

## regression.py:c_coeff
**Parameters:** `v_real='class numpy.ndarray', v_pred='class numpy.ndarray'`

**Description:**
```python
Coeficiente proposto por Wessling et al (1997) (https://doi.org/10.1016/0376-7388(93)E0168-J)

The neural network works predictively if C is smaller than 1. For C=l, the
predicted permeability for an unknown polymer would be  equal to the average
permeability of all polymers presented in the set (which is, in fact, useless).
```

--------------------------------------------------

## regression.py:display_score
**Parameters:** `m, x_train, x_test, y_train, y_test, delog_y=False, base=10, untransform_y='Zscore or normalize', dict_params_transform='dicionario parametros', _input_type_dict={'m': object, 'x_train': np.ndarray, 'x_test': np.ndarray, 'y_train': np.ndarray, 'y_test': np.ndarray, 'delog_y': bool, 'base': (int, float), 'untransform_y': str, 'dict_params_transform': dict}`

**Description:**
```python
função para avaliar RMSE, R2 e OOB_score

Exemplo de dict_params_transform para Zscore:
dict_params_transform = {'mean':'mean_value_for_target_variable', 'std':'std_value_for_target_variable'}
Exemplo de dict_params_transform para normalize:
IMPLEMENTAR AINDA
```

--------------------------------------------------

## regression.py:mape
**Parameters:** `v_real, v_pred`

**Description:**
```python
No description available
```

--------------------------------------------------

## regression.py:predictions_separate_by_a_variable
**Parameters:** `model, x_train, x_test, y_test, variable_in_original_databank, original_databank_train, original_databank_test, variable_subgroup='all', delog_y=False, base=10, untransform_y='Zscore or normalize', dict_params_transform='dicionario parametros', _input_type_dict={'model': object, 'x_train': np.ndarray, 'x_test': np.ndarray, 'y_test': np.ndarray, 'variable_in_original_databank': str, 'original_databank_train': pd.DataFrame, 'original_databank_test': pd.DataFrame, 'variable_subgroup': (list, str), 'delog_y': bool, 'base': (int, float), 'untransform_y': str, 'dict_params_transform': dict}`

**Description:**
```python
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
```

--------------------------------------------------

## regression.py:r2
**Parameters:** `v_real, v_pred`

**Description:**
```python
No description available
```

--------------------------------------------------

## regression.py:rmse
**Parameters:** `v_real, v_pred`

**Description:**
```python
No description available
```

--------------------------------------------------

