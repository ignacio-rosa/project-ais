import requests
import time
import datetime as dt
import os
import pandas as pd
import time
#import praw

CLIENT_ID = os.environ.get("RD_CLIENT_ID")
SECRET_TOKEN = os.environ.get("RD_SECRET_TOKEN")
PASSWORD = os.environ.get("RD_PASSWORD")
USER_AGENT = os.environ.get("RD_USER_AGENT")
USERNAME = os.environ.get("RD_USERNAME")
PJ_NAME = os.environ.get('PJ_NAME')

def reddit_search_api(day_diff=7, s_check=0):

    """
    This function searches submissions through Reddit API in different
    subreddits defined previously in the parameters
    """

    print('## Reddit submissions search by API started')
    from_date = dt.date.today() - dt.timedelta(days=day_diff)
    from_date = dt.datetime(from_date.year, from_date.month, from_date.day)
    try:
        pwd = os.path.abspath(__file__)
        pwd = os.path.join(pwd[:pwd.rfind(PJ_NAME)], PJ_NAME)
        path_data = os.path.join(pwd, 'raw_data')
        path_out = os.path.join(path_data, 'reddit_api')
        path_param = os.path.join(pwd, 'parameters')
    except:
        pwd = os.getcwd()
        pwd = os.path.join(pwd[:pwd.rfind(PJ_NAME)], PJ_NAME)
        path_data = os.path.join(pwd, 'raw_data')
        path_out = os.path.join(path_data, 'reddit_api')
        path_param = os.path.join(pwd, 'parameters')

    # Open subreddits targets
    df_subreddits = pd.read_csv(f'{path_param}/subreddits_list.csv')

    # Create tickers and names to search
    df_tickers = pd.read_csv(f'{path_param}/tickers_names.csv')
    l_tickers = list(df_tickers['ticker'].unique())
    d_tickers = {}
    for ticker in l_tickers:
        _l = list(df_tickers[df_tickers['ticker'] == ticker]['name_simple'].values)
        d_tickers[ticker] = ' OR '.join(_l)


    def get_headers(username, password):
        # note that CLIENT_ID refers to 'personal use script' and SECRET_TOKEN to 'token'
        auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET_TOKEN)

        # here we pass our login method (password), username, and password
        data = {'grant_type': 'password',
                'username': username,
                'password': password}

        # setup our header info, which gives reddit a brief description of our app
        headers = {'User-Agent': 'post_analyzer 0.0.1 by /u/aeri4ls'}

        # send our request for an OAuth token
        res = requests.post('https://www.reddit.com/api/v1/access_token',
                            auth=auth, data=data, headers=headers)

        # convert response to JSON and pull access_token value
        TOKEN = res.json()['access_token']

        # add authorization to our headers dictionary
        return {**headers, **{'Authorization': f"bearer {TOKEN}"}}

    #headers = get_headers(USERNAME, PASSWORD)
    headers = {'User-Agent': 'post_analyzer 0.0.1 by /u/aeri4ls'}
    l_ticker = []
    l_subr = []
    l_content = []
    for subreddit in df_subreddits['subreddit'].values[s_check:]:
        new_url= f'https://www.reddit.com/r/{subreddit}/search.json'
        for ticker, simple_names in d_tickers.items():
            print(f'Extracting from subreddit: {subreddit}, ticker: {ticker}')
            last_post_id = None
            last_post_date = dt.datetime.today()
            d_params = {'q': f'{ticker} OR ({simple_names})',
                        'sort': 'new',
                        'limit': 100,
                        'show': 'all',
                        't': 'all',
                        'restrict_sr': 'on'}
            a=0
            b=0
            while last_post_date >= from_date:
                if last_post_id != None:
                    d_params['after'] = last_post_id
                for wait_time in range(60, 600, 60):
                    try:
                        r_get = requests.get(new_url, headers=headers, params=d_params)
                    except:
                        print(f'Waiting {wait_time} due to connection')
                        time.sleep(wait_time)
                        r_get = requests.get(new_url, headers=headers, params=d_params)
                    if r_get.status_code == 200:
                        break
                    else:
                        print(f'Waiting {wait_time}')
                        time.sleep(wait_time)
                if r_get.status_code == 200:
                    r_get = r_get.json()['data']['children']
                    if len(r_get) > 0:
                        last_post_date = dt.datetime.fromtimestamp(r_get[-1]['data']['created'])
                        last_post_id = str(r_get[-1]['data']['name'])
                        l_ticker = l_ticker + [ticker for x in r_get]
                        l_subr = l_subr +  [subreddit for x in r_get]
                        l_content = l_content + r_get
                        a+=1
                        print(f'Attempt {a}: {len(r_get)}')
                    else:
                        b += 1
                        break
                else:
                    b += 1
                    break
                time.sleep(1)
        df_out = pd.DataFrame({'subreddit': l_subr,
                            'ticker': l_ticker,
                            'content': l_content})
        df_out.to_csv(f'{path_out}/{subreddit}.csv', sep=',', index=False)
    print('## Reddit submissions search by API finished')
