from sklearn.pipeline import make_pipeline
from sklearn.compose import make_column_transformer
from sklearn.preprocessing import RobustScaler
import pandas as pd


def filter_ticker(df, avg_comments=4, exclusion=True):
    """
    This function takes a DataFrame with "ticker" column and filters
    out the ones with less than the defined average comments per month
    and the tickers with value 1 in the exclusion column
    """
    df_tickers = pd.read_csv('tickers_handler.csv')
    l_tickers = []
    if exclusion == True:
        l_tickers = l_tickers + list(df_tickers[df_tickers['exclusion'] == 1]['ticker'].values)
    l_tickers = l_tickers + list(df_tickers[df_tickers['average_comments'] < avg_comments]['ticker'].values)
    df_end = df[~df['ticker'].isin(l_tickers)].copy()
    df_end = df_end.dropna(subset=['ticker'])
    return df_end

def init_preproc_pipe(cols_robust, iqr=(25, 75)):
    """
    Initialize a pipeline mainly with a Robust Scaler.
    Returns a pipeline
    names
    """
    scaler_robust = RobustScaler(quantile_range=iqr)
    pipe_ori = make_column_transformer((scaler_robust, cols_robust),
                                       remainder='passthrough')
    pipe_end = make_pipeline(pipe_ori)
    return pipe_end

def data_transform(data, ticker, list_years, target,
                   l_colsNoScale = ['tarjet_reg', 'tarjet_cla',
                                    'polarity_neg_pct', 'polarity_neu_pct',
                                    'polarity_pos_pct', 'month_sin',
                                    'month_cos', 'woy_sin', 'woy_cos',
                                    'target_pctc']):
    """
    This function takes a DataFrame, selects only rows of a specific ticker
    and years, to return two DataFrames with preprocessing applied and
    already formatted to pass them to a model for training or testing.
    The DataFrames returned are training (all data except last 5 weeks) and
    testing (only last 5 weeks)
    """
    data_2 = data.copy()
    data_2 = data_2[data_2['ticker']==ticker].drop(columns=['ticker'])
    data_2 = data_2[data_2['year'].isin(list_years)]
    data_2['target_pctc'] = data_2['tarjet_reg'] / data_2['Adj Close'] - 1
    data_2['target_pctc'] = data_2['target_pctc'].shift(1)
    data_2['tarjet_cla'] = data_2['tarjet_cla'].shift(1)
    data_2['tarjet_reg'] = data_2['tarjet_reg'].shift(1)
    data_test = data_2[-5:]
    data_train = data_2[1:-5]
    l_colsScale = list(data_train.columns)
    for col in l_colsNoScale:
        l_colsScale.remove(col)
    pipe_preproc = init_preproc_pipe(l_colsScale)
    pipe_preproc.fit(data_train)
    data_train = pipe_preproc.transform(data_train)
    data_test = pipe_preproc.transform(data_test)
    l_drop = ['tarjet_cla', 'tarjet_reg', 'target_pctc']
    l_drop.remove(target)
    data_train = pd.DataFrame(data_train, columns=l_colsScale+l_colsNoScale)[1:].drop(columns=l_drop)
    data_test = pd.DataFrame(data_test, columns=l_colsScale+l_colsNoScale).drop(columns=l_drop)
    return data_train, data_test
