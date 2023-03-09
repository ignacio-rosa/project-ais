from sklearn.pipeline import make_pipeline, make_union
from sklearn.compose import make_column_transformer
from sklearn.preprocessing import RobustScaler, FunctionTransformer
import pandas as pd
from math import pi
from numpy import cos, sin


"""
# Code to extract dataframe and try code
import os
try:
        pwd = os.path.abspath(__file__)
        path_data = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(pwd))),
                                'raw_data')
        path_sentiment = os.path.join(path_data, 'sentiment_data')
        path_financial = os.path.join(path_data, 'financials')
    except:
        pwd = os.getcwd()
        path_data = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(pwd))),
                                'raw_data')
        path_sentiment = os.path.join(path_data, 'sentiment_data')
        path_financial = os.path.join(path_data, 'financials')

l_regIndex = ['year', 'month', 'woy', 'ticker']
df = pd.read_csv(f'{path_sentiment}/reddit_with_vader.csv')
df = pd.pivot_table(df, index=l_regIndex,
                            columns='polarity', values='id',
                            aggfunc='count').reset_index().fillna(0)
"""


def preprocess(df, iqr=(25, 75)):
    """
    Preprocess a dataframe mainly with a Robust Scaler and
    some feature engineering. Returns a dataframe
    """

    l_oriCols = list(df.columns)
    l_oriCols.remove('ticker')
    ss_ticker = df['ticker']
    del df['ticker']

    l_feat_pctSentiment = ['ttl_sentiment', 'neg_pct', 'neu_pct', 'pos_pct']
    def ttl_pct_sentiment(df):
        df['ttl_sentiment'] = df[['neg', 'neu', 'pos']].sum(axis=1)
        df['neg_pct'] = df['neg'] / df['ttl_sentiment']
        df['neu_pct'] = df['neu'] / df['ttl_sentiment']
        df['pos_pct'] = df['pos'] / df['ttl_sentiment']
        return df[l_feat_pctSentiment]
    l_feat_cyclical = ['month_sin', 'month_cos', 'woy_sin', 'woy_cos']
    def cyclical_feat(df):
        l_cols = ['month', 'woy']
        for col in l_cols:
            df[f'{col}_sin'] = sin(2 * pi * df[col] / df[col].max())
            df[f'{col}_cos'] = cos(2 * pi * df[col] / df[col].max())
        return df[l_feat_cyclical]
    def feature_engineering(df):
        l_features = [ttl_pct_sentiment(df),
                        cyclical_feat(df)]
        return pd.concat(l_features, axis=1)
    l_ftengin = l_feat_pctSentiment + l_feat_cyclical

    fun_ftengin = FunctionTransformer(feature_engineering,
                                      feature_names_out=l_ftengin)
    scaler_robust = RobustScaler(quantile_range=iqr)
    col_ftengin = make_column_transformer((scaler_robust, ['ttl_sentiment']),
                                            remainder='passthrough')
    pipe_ftengin = make_pipeline(fun_ftengin, col_ftengin)
    pipe_ori = make_pipeline(scaler_robust)
    pipe_end = make_union(pipe_ori, pipe_ftengin)
    df_end = pd.DataFrame(pipe_end.fit_transform(df))
    df_end.columns = l_oriCols + l_ftengin
    df_end = pd.concat([df_end, ss_ticker], axis=1)
    return df_end
