import pandas as pd
import datetime as dt

df = pd.read_csv('sentimental_finance_features.csv')
df_data = filter_ticker(df, avg_comments=4)
df_data = feat_engin(df_data)

FOLD_LENGTH = 4 * 6 #
FOLD_STRIDE = 4 * 1 # Three months as stride
TRAIN_TEST_RATIO = 0.7
#N_TRAIN =
#N_TEST =
INPUT_LENGTH = 4 * 2 # Two months to predict the next day
OUTPUT_LENGTH = 1 # Just one week to predict
SEQ_STRIDE = 1 # Just one week
TARGET = 'tarjet_cla'

dtnow = dt.datetime.utcnow().strftime('%Y%m%d%H%M')
for ticker in df_data['ticker'].unique():
    model, history = cross_validate(data=df_data, ticker=ticker,
                                        list_years=[2021, 2022, 2023],
                                        pred_type='cla', epochs=1000,
                                        seq_stride=SEQ_STRIDE, target=TARGET,
                                        input_length=INPUT_LENGTH)
    model.save(f'model_data/model_saves/{ticker}_{dtnow}.h5')
    model.save(f'model_data/model_saves/{ticker}_last.h5')
