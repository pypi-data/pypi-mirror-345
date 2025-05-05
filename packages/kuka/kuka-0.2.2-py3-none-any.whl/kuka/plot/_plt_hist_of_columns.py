
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from .. import utils

@utils.__input_type_validation
def plt_hist_of_columns(
  df,

  _input_type_dict = {
    'df':type(pd.DataFrame())
    }

  ) -> None:
  '''
  Plot a histogram for each numeric column of a 
  dataframe in a more organized way than just calling pandas hist()
  '''
  def put_labels(ax_list):
    for row in ax_list:
      for ax in row:
        ax.set_xlabel('Values')
        ax.set_ylabel('Frequency')
    plt.tight_layout()
    

  #1- Convert numeric columns to float
  float_df_columns = []
  for i in df.columns:
    try:
      df[i] = df[i].astype(float)
    except:
      print(f'heatmap_pearson function: X column "{i}" is a {df[i].dtype}')
    else:
      float_df_columns += [i]

  hist_row = []
  for i in float_df_columns:
    hist_row += [i]
    if (len(hist_row)==4):
      try:
        df[hist_row] = df[hist_row].astype(float)
      except:
        print()
      axes = df[hist_row].hist()
      put_labels(axes)
      hist_row = []
  
  if hist_row:
    axes = df[hist_row].hist()
    put_labels(axes)
  
  plt.show()