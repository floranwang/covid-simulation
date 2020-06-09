import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.insert(1,'C:\\Users\\alexs\\covid-simulation\\IHME\\src')

from src.curvefit.core.model import CurveModel
from src.curvefit.core.functions import ln_gaussian_cdf
from src.curvefit.core.functions import gaussian_cdf

import sys
import os

import pathlib
import math


class ihme:
    def __init__(self,region=None,user_df=None,region_df=None):
        
        file = sorted(pathlib.Path('IHME/data').iterdir(), key=os.path.getmtime)[-1]
        df_all = pd.read_csv('IHME/data/'+file.name)
        df_all = df_all[['Date_reported','Country','Cumulative_deaths']]
        df_all.columns = ['date','group','cum_deaths']

        # If user specifies the name of a country we use the existing dataframe
        if region!=None:
            self.df = df_all[df_all.group==region].copy()
            self.region = region
            self.df.date = pd.to_datetime(self.df.date, format='%m/%d/%Y', errors='ignore')
            if self.df.shape[0]==0:
                raise NameError('Region not found in exisiting dataset')
        # Otherwise, use the dataset uploaded by the user
        else:
            self.df = pd.read_csv(user_df)
            self.df.columns = ['group','date','cum_deaths']
            self.df.date = pd.to_datetime(self.df.date, format='%m/%d/%Y', errors='ignore')
            
        if region_df is not None:
            self.region_df = pd.read_csv(region_df)

        self.df = self.df.sort_values('date')

        self.df['intercept'] = 1.0

        self.df['time'] = range(1,self.df.shape[0]+1,1)

        # Set up the CurveModel
        self.model = CurveModel(
            df=self.df,
            col_t='time',
            col_obs='cum_deaths',
            col_group='group',
            col_covs=[['intercept'], ['intercept'], ['intercept']],
            param_names=['alpha', 'beta', 'p'],
            link_fun=[lambda x: x, lambda x: x, lambda x: x],
            var_link_fun=[lambda x: x, lambda x: x, lambda x: x],
            fun=gaussian_cdf
        )

        # Defining beta init
        self.df['diff'] = self.df.cum_deaths - self.df.cum_deaths.shift(+1)
        t_infl = self.df[self.df['diff']==np.max(self.df['diff'])].time.values[0]
        beta_init = t_infl if t_infl >=30 else 30

        # Alpha init
        alpha_init = np.mean(self.df['diff'])

        # p init
        time_left = beta_init - self.df.time.max()
        p_init = np.max(self.df.cum_deaths)+self.df['diff'].tolist()[-1]*(time_left+beta_init)

        fe_init   = [alpha_init, beta_init, p_init]

        # Fit the model to estimate parameters
        self.model.fit_params(fe_init=fe_init,
                             fe_bounds = [ [0,1],[fe_init[1],200], [fe_init[2],np.inf]],
                             fe_gprior=[[fe_init[0], np.inf], [fe_init[1], np.inf], [fe_init[2], np.inf]])
        
    def predict(self,future=0):
        delta = (pd.to_datetime('today') - self.df.date.tolist()[-1]).days + future
        df_out = pd.DataFrame({'time':self.df.time.tolist() + list(range(self.df.shape[0],future+self.df.shape[0],1))})
        df_out['group'] = self.df.group.unique()[0]
        df_out['date'] = pd.date_range(start=self.df.date.unique()[0],periods=df_out.shape[0])

        # Get predictions
        df_out['pred'] = self.model.predict(
            t=df_out.time,
            group_name=df_out['group'].unique()
        )
        
        df_out = df_out.merge(self.df[['date','group','cum_deaths']],how='left',on=['date','group'])
        
        death_rate_dic = {"Age 0-9":0.05*0.3,
                 "Age 10-19":0.1*0.3,
                 "Age 20-29":0.1*0.3,
                 "Age 30-39":0.15*0.3,
                 "Age 40-49":0.2*0.3,
                 "Age 50-59":0.25*0.4,
                 "Age 60-69":0.35*0.4,
                 "Age 70-79":0.45*0.5,
                 "Age 80+":0.5*0.55}
        
        age_ranges = list(death_rate_dic.keys())
        
        self.region_df[age_ranges] = self.region_df[age_ranges]/np.sum(self.region_df[age_ranges],axis=1).values[0]
        avg_death_rate = np.sum(self.region_df[age_ranges]*list(death_rate_dic.values()),axis=1).values[0]
        
        df_out['infected'] = df_out.pred/avg_death_rate
        
        return df_out