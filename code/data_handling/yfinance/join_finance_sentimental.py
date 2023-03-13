import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder

def prepare_finance_data(finance_df):
    finance_new = finance_df.drop(columns=['index','date','week_month'])
    finance_new.rename(columns = {'week_year':'woy'}, inplace = True)
    
    finance_new['tarjet_reg'] = finance_new['Adj Close'].shift(-1)
    # Si el adj close es menor que el tarjet es igual a 1
    finance_new['tarjet_cla'] = np.where( finance_new['Adj Close'] < finance_new['tarjet_reg'] , 1, 0)
    
    return finance_new

def prepare_sentimental_data(sentimental_df):
    sentimental_df.sort_values(by=['ticker','year','month','woy'], inplace=True)
    
    ohe = OneHotEncoder(sparse=False)
    ohe.fit(sentimental_df[['polarity']])
    
    sentimental_full = sentimental_df.copy()
    # sentimental_full = pd.concat([sentimental_df,new_sentimental_df])
    sentimental_full[ohe.get_feature_names_out()] = ohe.transform(sentimental_full[['polarity']])

    sentimental_full.drop(columns=['polarity'], inplace=True)
    sentimental_ohe = sentimental_full.groupby(['ticker','year','month','woy'])['polarity_neu','polarity_pos','polarity_neg'].sum()
    # sentimental_ohe.to_csv('ohe.csv')
    
    return sentimental_ohe

def join_data(finance_df, sentimental_df):
    data = finance_df.merge(sentimental_df, how='left')
    data['rsi'] = data['rsi'].fillna(0)
    data['macd'] = data['macd'].fillna(0)
    data['macd_h'] = data['macd_h'].fillna(0)
    data['macd_s'] = data['macd_s'].fillna(0)
    data['polarity_neg'] = data['polarity_neg'].fillna(0)
    data['polarity_neu'] = data['polarity_neu'].fillna(0)
    data['polarity_pos'] = data['polarity_pos'].fillna(0)
    
    return data