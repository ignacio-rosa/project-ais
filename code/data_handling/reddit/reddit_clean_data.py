import pandas as pd
import os
import ast
import datetime as dt

try:
    pwd = os.path.abspath(__file__)
    path_data = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(pwd)))),
                             'raw_data')
    path_historic = os.path.join(path_data, 'reddit_historic', 'csv')
    path_recent = os.path.join(path_data, 'reddit_api')
    path_out = os.path.join(path_data, 'reddit_clean')
except:
    pwd = os.getcwd()
    path_data = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(pwd))),
                             'raw_data')
    path_data = os.path.join(pwd, 'raw_data')
    path_historic = os.path.join(path_data, 'reddit_historic', 'csv')
    path_recent = os.path.join(path_data, 'reddit_api')
    path_out = os.path.join(path_data, 'reddit_clean')


l_files_hist = os.listdir(path_historic)
l_files_rece = os.listdir(path_recent)
df_subreddits = pd.read_csv(f'{path_data}/subreddits_list.csv', sep=';')
df_tickers = pd.read_csv(f'{path_data}/tickers_names.csv', sep=';')
def extract_data(d):
    v_subr = d.get('subreddit')
    v_id = d.get('id')
    v_created = d.get('created_utc')
    if (v_created != None):
        v_created = dt.datetime.fromtimestamp(int(v_created))
    else:
        v_created = None
    v_title = d.get('title')
    v_title = None if v_title in ['[removed]', '[deleted]'] else v_title
    v_txt = d.get('selftext')
    v_txt = None if v_txt in ['[removed]', '[deleted]'] else v_txt
    return [v_subr, v_id, v_created, v_title, v_txt]

# Extracción de archivos históricos
l_subr = []
l_id = []
l_created = []
l_title = []
l_txt = []
len_files_hist = len([x for x in l_files_hist if 'submissions' in x])
a=0
for file in l_files_hist:
    if 'submissions' in file:
        a+=1
        print(f'{file}, number {a} of {len_files_hist}')
        df = pd.read_csv(f'{path_historic}/{file}')
        for index, row in df.iterrows():
            if index % 25000 == 0:
                print(f'Progress: {index/len(df)* 100:.0f}%')
            l_res = extract_data(ast.literal_eval(row['content']))
            l_subr.append(l_res[0])
            l_id.append(l_res[1])
            l_created.append(l_res[2])
            l_title.append(l_res[3])
            l_txt.append(l_res[4])
        if len(l_subr) > 10000:
            df_new = pd.DataFrame({'subreddit': l_subr, 'id': l_id,
                                   'created': l_created, 'title': l_title,
                                   'text': l_txt})
            df_new.to_csv(f'{path_out}/reddit_submissions.csv',
                          sep='|', index=False, mode='a', header=False,
                          escapechar='\\')
            del df_new
            l_subr.clear()
            l_id.clear()
            l_created.clear()
            l_title.clear()
            l_txt.clear()
df_new = pd.DataFrame({'subreddit': l_subr, 'id': l_id,
                        'created': l_created, 'title': l_title,
                        'text': l_txt})
df_new.to_csv(f'{path_out}/reddit_submissions.csv',
                sep='|', index=False, mode='a', header=False,
                escapechar='\\')

# Extraction from API created files
a=0
len_files_rece = len(l_files_rece)
l_subr = []
l_id = []
l_created = []
l_title = []
l_txt = []
for file in l_files_rece:
    a+=1
    print(f'{file}, number {a} of {len_files_rece}')
    df = pd.read_csv(f'{path_recent}/{file}')
    for index, row in df.iterrows():
        if index % 25000 == 0:
            print(f'Progress: {index/len(df)* 100:.0f}%')
        l_res = extract_data(ast.literal_eval(row['content'])['data'])
        l_subr.append(l_res[0])
        l_id.append(l_res[1])
        l_created.append(l_res[2])
        l_title.append(l_res[3])
        l_txt.append(l_res[4])
    if len(l_subr) > 10000:
        df_new = pd.DataFrame({'subreddit': l_subr, 'id': l_id,
                                'created': l_created, 'title': l_title,
                                'text': l_txt})
        df_new.to_csv(f'{path_out}/reddit_submissions.csv',
                        sep='|', index=False, mode='a', header=False,
                        escapechar='\\')
        del df_new
        l_subr.clear()
        l_id.clear()
        l_created.clear()
        l_title.clear()
        l_txt.clear()
df_new = pd.DataFrame({'subreddit': l_subr, 'id': l_id,
                        'created': l_created, 'title': l_title,
                        'text': l_txt})
df_new.to_csv(f'{path_out}/reddit_submissions.csv',
                sep='|', index=False, mode='a', header=False,
                escapechar='\\')

"""
#Backup para volver a crear archivo base limpio
df_test = pd.DataFrame({'subreddit': [], 'id': [],
                       'created': [], 'title': [],
                       'text': []})
df_test.to_csv(f'{path_out}/reddit_submissions.csv',
               sep='|', escapechar='\\', index=False)
df_test = pd.read_csv(f'{path_out}/reddit_submissions.csv',
               sep='|', escapechar='\\')"""
