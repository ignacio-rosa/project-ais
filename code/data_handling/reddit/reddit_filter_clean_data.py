import pandas as pd
import os
import datetime as dt

try:
    pwd = os.path.abspath(__file__)
    path_data = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(pwd)))),
                             'raw_data')
    path_clean = os.path.join(path_data, 'reddit_clean')
except:
    pwd = os.getcwd()
    path_data = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(pwd)))),
                             'raw_data')
    path_clean = os.path.join(path_data, 'reddit_clean')

df_tickers = pd.read_csv(f'{path_data}/tickers_names.csv', sep=';')
d_tickers_regex = {}
l_tickers = list(df_tickers['ticker'].unique())
for ticker in l_tickers:
    _l = list(df_tickers[df_tickers['ticker'] == ticker]['name_simple'].values)
    d_tickers_regex[ticker] = ' | '.join(_l)
chunksize = 10 ** 5
ttl_submissions = sum(1 for row in open(f'{path_clean}/reddit_submissions.csv', 'r'))
a = 0
with pd.read_csv(f'{path_clean}/reddit_submissions.csv', sep='|',
                 escapechar='\\', chunksize=chunksize) as reader:
    for chunk in reader:
        df_chunk_fin = pd.DataFrame()
        a+=1
        print(f'Chunk {a} of {ttl_submissions/chunksize}')
        chunk = chunk.fillna('')
        chunk['created'] = pd.to_datetime(chunk['created'])
        chunk = chunk[chunk['created']>=dt.datetime(2023, 1, 1)]
        if len(chunk) > 0:
            for key, value in d_tickers_regex.items():
                _1 = chunk[chunk['text'].str.contains(fr'\b{key}\b', case=True)]
                _2 = chunk[chunk['text'].str.contains(fr'\b{value}\b', case=False)]
                if (len(_1) > 0) | (len(_2) > 0):
                    df_filter = pd.concat([_1, _2]).drop_duplicates()
                    df_filter['ticker'] = key
                    if len(df_chunk_fin) == 0:
                        df_chunk_fin = df_filter
                    else:
                        df_chunk_fin = pd.concat([df_chunk_fin, df_filter])
            write_mode = 'a' if os.path.exists(f'{path_clean}/subreddit_clean_filtered.csv') else 'w'
            header_mode = False if os.path.exists(f'{path_clean}/subreddit_clean_filtered.csv') else True
            df_chunk_fin.to_csv(f'{path_clean}/subreddit_clean_filtered.csv',
                                mode=write_mode, sep=',', escapechar='\\',
                                index=False, header=header_mode)

"""
ticker = 'AAPL'
name_simple = 'Apple'
test = rf'{ticker}|(?i){name_simple}'
df_try_reg = pd.DataFrame({'text': ['Nothing new inside Apple   ',
                            'I\'ve been searching for AAPL stocks',
                            'But not looking for aapl']})
key='AAPL'
value = 'Apple'
df_try_reg[df_try_reg['text'].str.findall(fr'{key}|(?i){value}')]
df_try_reg[df_try_reg['text'].str.contains('AAPL')]
df_try_reg[df_try_reg['text'].str.contains(r'\bApple\b', case=False)]
import re
def reg_ulti(x):
    return re.findall(r'AAPL|(?i)Apple', x)
df_try_reg['text'].apply(lambda x: reg_ulti(x))
re.findall(r'(AAPL)|((?i)Apple)', 'But not looking for aAPL')
"""
