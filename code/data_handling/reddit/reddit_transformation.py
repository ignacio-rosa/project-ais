import pandas as pd
import datetime as dt
import calendar
import os

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


def week_of_month(tgtdate):
    days_this_month = calendar.mdays[tgtdate.month]
    for i in range(1, days_this_month):
        d = dt.date(tgtdate.year, tgtdate.month, i)
        if d.day - d.weekday() > 0:
            startdate = d
            break
    # now we canuse the modulo 7 approach
    return (tgtdate - startdate).days // 7 + 1

df = pd.read_csv(f'{path_clean}/subreddit_clean_filtered.csv',
                 sep=',', escapechar='\\')
df['created'] = pd.to_datetime(df['created'])
df['ym'] = df['created'].apply(lambda x: int(str(x.year) + str(x.month+100)[-2:]))
df = df[df['ym']>=201301]
_dups = df[['id', 'ticker']].groupby('id').count()
_dups = _dups.rename(columns={'ticker': 'dups'})
df = pd.merge(df, _dups, on='id', how='left')
df['dups'] = df['dups'].apply(lambda x: 1 if x > 1 else 0)
df['year'] = df['created'].apply(lambda x: x.year)
df['month'] = df['created'].apply(lambda x: x.month)
df['woy'] = df['created'].apply(lambda x: x.isocalendar()[1])
#df['wom'] = df['created'].apply(lambda x: week_of_month(dt.datetime.timestamp(x)))
l_cols_order = ['year', 'month', 'woy', 'ticker', 'subreddit', 'id', 'created',
          'title', 'text', 'dups']
df = df[l_cols_order]
df.to_csv(f'{path_clean}/reddit_new_submissions_filter_clean.csv', index=False,
          sep=',', escapechar='\\')

"""
df_pivot = pd.pivot_table(df, index=['ticker', 'ym', 'dups'],
                          values='id', aggfunc='count').reset_index()
df_pivot.to_csv(f'{path_clean}/filter_pivot.csv', index=False,
          sep=';', escapechar='\\')
"""
