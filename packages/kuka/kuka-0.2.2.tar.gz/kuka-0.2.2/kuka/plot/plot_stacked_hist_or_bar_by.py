import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from .. import utils

@utils.__input_type_validation
def plot_stacked_hist_or_bar_by(
    df, variable = '',
    by = '',
    mode = 'bar or hist',
    alpha = 0.3,
    colors_reference = ['b','g','r','c','m','y','k'],
    dict_colors_of_variable_by = False, #Dicionario para ditar a cor de cada valor para "unique_by"
    figsize = [6.4, 4.8],
    width_bar = 'default',
    bar_norm = False,
    bar_labels=False,
    bins_hist = 1,
    x_log_scale_hist = False,
    hist_average_line = False,
    use_external_fig_and_ax = False,
    external_fig_and_ax = 'tuple of fig and ax, respectively',
    verbose = True,
    
    _input_type_dict = {
        'df': pd.DataFrame,
        'variable': str,
        'by': str,
        'mode': str,
        'alpha': (float, int),
        'colors_reference': list,
        'dict_colors_of_variable_by': (bool, dict), #Dicionario para ditar a cor de cada valor para "unique_by"
        'figsize': (list, tuple),
        'width_bar': (str, int, float),
        'bar_norm': bool,
        'bar_labels': bool,
        'bins_hist': (float, int),
        'x_log_scale_hist': bool,
        'hist_average_line': bool,
        'use_external_fig_and_ax': bool,
        'external_fig_and_ax': (str, tuple, list),
        'verbose': bool,
    },
    
    ) -> object:
  '''
  Histogramas empilhados por classe "by"
  Exemplos semelhantes de grafico de barras: https://matplotlib.org/stable/gallery/lines_bars_and_markers/bar_stacked.html#sphx-glr-gallery-lines-bars-and-markers-bar-stacked-py

  Essa função se baseia na criação de dicionários para os valores da base (variável "bottom"
  do matplotlib) e das frequencias (variável "height" do matplotlib). As chaves(keys) desses
  dicionários são os valores únicos de "df[variable]" e os valores são referentes à frequencia
  (obtidas a partir da função "value_counts").

  Essa função retorna "fig" e "ax" do Matplotlib. Portanto, o gráfico criado pode ser editado
  posteriormente, mesmo com certa limitação.

  O modo 'hist' serve apenas para quando "variable" possui valores numéricos.
  '''
  import numpy as np
  import copy
  import math
  import scipy
  df = df.copy()

  if (use_external_fig_and_ax == False):
    fig, ax = plt.subplots(figsize=figsize)
  if (use_external_fig_and_ax == True):
    fig, ax = external_fig_and_ax

  df.dropna(subset=[variable], inplace=True)
  x_range = [df[variable].min(), df[variable].max()]

  unique_by = df[by].unique()
  #Definir as CORES para cada valor único da variável "by".
  #Caso houver mais valores que o tamanho de "colors_reference", as cores serão repetidas:
  count, colors = (0, {})
  if (dict_colors_of_variable_by==False):
    for i in range(len(unique_by)):
      if (count==len(colors_reference)):
        count = 0
      colors[unique_by[count]] = colors_reference[count]
      count += 1
  else:
    for i in unique_by:
      colors[i] = dict_colors_of_variable_by[i]

  #dicionario com os valores da base:
  unique_variable = df[variable].unique()
  bottoms = dict(zip(unique_variable,len(unique_variable)*[0]))
  #variavel referencia - dicionario com valores zerados:
  values_0 = copy.copy(bottoms)

  #Histograma - o dicionário para o "x", "height" e "bottom" é diferente quando se deseja construir um histograma:
  #             faz-se necessário trabalhar com numeros/floats
  if (mode=='hist'):
    if (x_log_scale_hist==False):
      histogram_width = (x_range[1]-x_range[0])/bins_hist
      histogram_x = np.arange( x_range[0], x_range[1], histogram_width ).tolist()
      histogram_bottoms = dict(zip(histogram_x,len(histogram_x)*[0])) ##valores com o valor da base
      histogram_0 = copy.copy(histogram_bottoms) #variavel referencia - dicionario com valores zerados
    elif(x_log_scale_hist==True):
      x_range_log = [0,0]
      x_range_log[0] = math.log10(x_range[0])
      x_range_log[1] = math.log10(x_range[1])

      histogram_width_log = (x_range_log[1]-x_range_log[0])/bins_hist
      histogram_x_log = np.arange( x_range_log[0], x_range_log[1], histogram_width_log ).tolist()

      histogram_x = []
      for log_number in histogram_x_log:
        histogram_x += [10**log_number]

      histogram_width = []
      for i in range(len(histogram_x)):
        histogram_width += [ 10**(x_range_log[0]+histogram_width_log*(i+1)) - 10**(x_range_log[0]+histogram_width_log*i) ]

      histogram_bottoms = dict(zip(histogram_x,len(histogram_x)*[0]))
      histogram_0 = copy.copy(histogram_bottoms)
    else:
      print('ERRO: x_log_scale_hist')
      return



  #Definir variável com o valor total de frequência para cada "variable"
  if (bar_norm==True):
    total_value_counts = df[variable].value_counts()

  count = 0
  for i in unique_by:
    values = copy.copy(values_0) #armazenará os "value_counts" referentes a vada valor unico de uma variavel

    #Obter os value counts de cada "variable" para cada "unique_by"
    df_filtrado = df.loc[df[by]==i, variable]
    hist_aux_df = df_filtrado.value_counts()
    for j in hist_aux_df.index:
      if (bar_norm==True):
        values[j] += hist_aux_df[j]/total_value_counts[j] #Normalizar "values" pelo valor total
      else:
        values[j] += hist_aux_df[j]


    if (mode=='bar'):
      ## Grafico ##
      if (width_bar=='default') and not(isinstance(x_range[1], str)): width_bar = (x_range[1]-x_range[0])/len(unique_variable)
      if isinstance(x_range[1], str): width_bar=0.8

      graph = ax.bar(x=list(values.keys()), #https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.bar.html#matplotlib.axes.Axes.bar
            height=list(values.values()),
            width=width_bar,
            bottom=list(bottoms.values()),
            align = 'center',
            color = colors[i],
            #edgecolor='black',
            #hatch='//',
            alpha=alpha,
            label= i
            )

      ## Grafico ##
      for j in bottoms.keys():
        bottoms[j] += values[j]

    elif (mode=='hist'):
      histogram_values = copy.copy(histogram_0)
      for j in values.keys():
        for k in histogram_x[::-1]:
          if (j>=k):
            histogram_values[k] += values[j]
            break
      ## Grafico ##
      ax.bar(x=list(histogram_values.keys()), #https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.bar.html#matplotlib.axes.Axes.bar
            height=list(histogram_values.values()),
            width=histogram_width,
            bottom=list(histogram_bottoms.values()),
            align = 'edge',
            color = colors[i],
            #edgecolor='black',
            #hatch='//',
            alpha=alpha,
            label= i
            )
      if (x_log_scale_hist==True): plt.xscale('log')
      ## Grafico ##
      for j in histogram_bottoms.keys():
        histogram_bottoms[j] += histogram_values[j]

    count += 1

  # Bar labels
  if (mode=='bar') and (bar_labels==True):
    value_counts = df[variable].value_counts()
    for height,x in zip(value_counts, value_counts.index):
      ax.annotate('{}'.format(height),
                  xy=(x, height),
                  xytext=(0, 5), # 5 points vertical offset
                  textcoords="offset points",
                  ha='center', va='bottom',
                  #fontsize=15,
                  rotation=0)

  ## Grafico ##
  ax.set(#title=f'Frequência de {variable} por tipo de membrana',
         xlabel=variable,
         ylabel='Frequência')
  ax.legend();
  ax.margins(0.1)
  ## Grafico ##

  ## Histogram average lines ##
  if (hist_average_line==True):
    if (x_log_scale_hist == False):
      # USANDO gaussian_kde
      value_counts = df[variable].value_counts()
      density = scipy.stats.gaussian_kde(df[variable].astype(np.float64))
      xlim = ax.get_xlim()
      x = np.linspace(xlim[0], xlim[1], 1000)
      ax.stackplot(x, density(x)*sum(list(value_counts))*histogram_width,
                   color='black',
                   alpha = 0.4,
                   linewidth = 0)
    elif (x_log_scale_hist == True): #precisa aprimorar o codigo!!
      # USANDO gaussian_kde
      density = scipy.stats.gaussian_kde( np.log10(df[variable].astype(np.float64)) )
      xlim = ax.get_xlim()
      x = np.geomspace(xlim[0], xlim[1], 1000)

      previous_x_non_log = df[variable].min()
      next_x_non_log = previous_x_non_log + histogram_width[0]
      histogram_width_for_gaussian_kde = [ np.log10(next_x_non_log) - np.log10(previous_x_non_log) ]
      for i in range(len(histogram_width)-1):
        previous_x_non_log = next_x_non_log
        next_x_non_log = previous_x_non_log + histogram_width[i+1]
        histogram_width_for_gaussian_kde += [ np.log10(next_x_non_log) - np.log10(previous_x_non_log) ]

      ax.stackplot(x, density(np.log10(x))*np.dot( list(histogram_bottoms.values()), histogram_width_for_gaussian_kde ),
                   color='black',
                   alpha = 0.4,
                   linewidth = 0)
#definir um modelo de Probabilidade de distribuição, ajustar e prever
# model = scipy.stats.norm
# params = model.fit(np.log10(df[variable]))
# print(params)
# density = model(*params)
# xlim = ax.get_xlim()
# x = np.linspace(xlim[0], xlim[1], 1000)
# ax.stackplot(x, density.pdf(x)*sum(list(value_counts))*histogram_width)
  ## Histogram average lines ##

  if verbose==True:
    print('min =',df[variable].min())
    print('max =',df[variable].max())

  return fig, ax