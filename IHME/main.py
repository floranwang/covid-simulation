import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from src.curvefit.core.model import CurveModel
from src.curvefit.core.functions import ln_gaussian_cdf
from src.curvefit.core.functions import gaussian_cdf

import sys
import os

import pathlib

#Importing data from all countries
file = sorted(pathlib.Path('data').iterdir(), key=os.path.getmtime)[-1]
df_all = pd.read_csv('data/'+file.name)
df_all = df_all[['day','Country Name','Cumulative Deaths']]
df_all.columns = ['date','group','cum_deaths']

region = 'Jamaica'

#If user specifies the name of a country we use the existing dataframe
if region!=None:
    df = df_all[df_all.group==region].copy()
    df.date = pd.to_datetime(df.date, format='%Y-%m-%d', errors='ignore')
#Otherwise, use the dataset uploaded by the user
else:
    df = user_df
    df.columns = ['group','date','cum_deaths']
    df.date = pd.to_datetime(df.date, format='%Y/%m/%d', errors='ignore')
    
df = df.sort_values('date')
df['time'] = range(1,df.shape[0]+1,1)
    
df['intercept'] = 1.0

# Set up the CurveModel
model = CurveModel(
    df=df,
    col_t='time',
    col_obs='cum_deaths',
    col_group='group',
    col_covs=[['intercept'], ['intercept'], ['intercept']],
    param_names=['alpha', 'beta', 'p'],
    link_fun=[lambda x: x, lambda x: x, lambda x: x],
    var_link_fun=[lambda x: x, lambda x: x, lambda x: x],
    fun=gaussian_cdf
)

# Fit the model to estimate parameters
model.fit_params(fe_init=[0, 0, 1.],
                 fe_gprior=[[0, np.inf], [0, np.inf], [1., np.inf]])
				 
# Get predictions
y_pred = model.predict(
    t=df_out.time,
    group_name=df_out['group'].unique()
)

# Plot results
plt.plot(df_out.date, y_pred, '-')
plt.plot(df.date, df.cum_deaths, '.')

plt.xlabel("Date")
plt.ylabel("Cumulative Deaths")