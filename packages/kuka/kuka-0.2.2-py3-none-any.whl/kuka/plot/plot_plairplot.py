import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import matplotlib

from .. import utils

@utils.__input_type_validation
def plot_plairplot(
    df, 
    columns = ['all'],
    color_by = '',
    figsize = 'default',
    colors_reference = ['black', '#023eff', '#ff7c00', '#1ac938', '#e8000b', '#8b2be2', '#9f4800', '#f14cc1', '#a3a3a3', '#ffc400', '#00d7ff'],
    dict_colors_of_variable_by = False, #Dicionario para ditar a cor de cada valor para "unique_by"
    wspace = 0.12,
    hspace = 0.12,
    major_label_off = False,
    tick_labelsize = matplotlib.rcParams['font.size'],
    tick_format = '{x:.4g}',
    margins = 0.08, #dicionário com os argumentos e valores de plt.scatter()
    
    _input_type_dict = {
        'df': pd.DataFrame, 
        'columns': (list, tuple),
        'color_by': str,
        'figsize': (list, tuple, str),
        'colors_reference': (list, tuple),
        'dict_colors_of_variable_by': (bool, dict),
        'wspace': (int, float),
        'hspace': (int, float),
        'major_label_off': bool,
        'tick_labelsize': (int, float),
        'tick_format': str,
        'margins': (int, float),
    },
    
    **kwargs_scatter
    
    ) -> object:

  df = df.copy()

  if (figsize == 'default'):
    figsize = plt.rcParams['figure.figsize']

  if (color_by==''):
    unique_color_by = False
  else:
    column_color_by = df[color_by].copy()
    unique_color_by = column_color_by.unique()

  if (columns == ['all']):
    columns = df.columns

  # trabalhar apenas com as colunas numéricas
  print(f'\n    String type columns:\n')
  for i in columns:
    if (df[i].dtype == 'object'): #Retirar apenas as colunas com dtype=object
      print(i,'     ',df[i].dtype)
      df.drop( columns=i, inplace=True )
  columns = df.columns
  print('columns = ', list(columns))
  print('\n')

  #Definir as CORES para cada valor único da variável "unique_color_by".
  #Caso houver mais valores que o tamanho de "colors_reference", as cores serão repetidas:
  if (unique_color_by is False):
    colors = colors_reference[0]
  else:
    count, colors = (0, {})
    if (dict_colors_of_variable_by==False):
      for i in range(len(unique_color_by)):
        if (count==len(colors_reference)):
          count = 0
        colors[unique_color_by[count]] = colors_reference[count]
        count += 1
    else:
      for i in unique_color_by:
        colors[i] = dict_colors_of_variable_by[i]


  fig, ax = plt.subplots(ncols=len(columns)-1,
                         nrows=len(columns)-1,
                         figsize=figsize)


  def definicoes_de_cada_grafico():
    xlim = (df[col].min(), df[col].max())
    ylim = (df[row].min(), df[row].max())

    if not(np.isnan(xlim[0])) or not(np.isnan(xlim[1])):
      ampl_x = (xlim[1] - xlim[0])*margins
      ax[i,j].set_xlim([ xlim[0]-ampl_x, xlim[1]+ampl_x ])
    if not(np.isnan(ylim[0])) or not(np.isnan(ylim[1])):
      ampl_y = (ylim[1] - ylim[0])*margins
      ax[i,j].set_ylim([ ylim[0]-ampl_y, ylim[1]+ampl_y ])

    # ax[i,j].xaxis.set_major_locator(matplotlib.ticker.LinearLocator(numticks=2))
    ax[i,j].xaxis.set_major_locator(matplotlib.ticker.FixedLocator(xlim))
    # ax[i,j].yaxis.set_major_locator(matplotlib.ticker.LinearLocator(numticks=2))
    ax[i,j].yaxis.set_major_locator(matplotlib.ticker.FixedLocator(ylim))

    if major_label_off == True:
      ax[i,j].tick_params(axis = 'both', which='major', labelbottom=False, labelleft=False)
    else:
      ax[i,j].tick_params(axis = 'both', which='major', bottom=True, left=True, length=6)
      ax[i,j].tick_params(axis = 'both', labelsize=tick_labelsize)
      ax[i,j].xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter(tick_format))

    # X and Y labels
    if (i==(len(columns)-2)):#Se o grafico estiver na ultima linha
      ax[i,j].set_xlabel(col, fontweight="bold")
      ax[i,j].tick_params(axis='x', which='both', rotation=90)
    else:
      ax[i,j].tick_params(which='both', bottom=False, labelbottom=False)

    if (j==0):#se o grafico estiver na primeira coluna
      ax[i,j].set_ylabel(row, fontweight="bold")
    else:
      ax[i,j].tick_params(which='both', left=False, labelleft=False)


  i, j = (-1, -1)
  for row in columns: #i
    for col in columns: #j
      if (row==col):
        j = 0
        break
      # print(i, 'y=', row, '   | ', j, 'x=', col)
      if (unique_color_by is False):
        df_filtered = df.dropna(subset=[row, col])

        ax[i,j].scatter(x = df_filtered[col],
                        y = df_filtered[row],
                        color = colors,
                        **kwargs_scatter
                        )
        definicoes_de_cada_grafico()
      else:
        for by in unique_color_by:
          df_filtered = df.loc[ column_color_by==by, [row, col] ]
          ax[i,j].scatter(x = df_filtered[col],
                          y = df_filtered[row],
                          color = colors[by],
                          **kwargs_scatter
                         )
        definicoes_de_cada_grafico()
      j+=1
    i+=1

  #Remover eixos não usados
  aux = 0
  for row in range(len(columns)-1): #i
    for col in range(len(columns)-1): #j
      if col>row:
        ax[row,col].remove()

  # plt.tight_layout()

  plt.subplots_adjust(wspace=wspace, hspace=hspace)

  return fig, ax