import os
import pandas as pd
import ast
import datetime as dt

try:
    pwd = os.path.abspath(__file__)
    path_project = os.path.join(pwd[:pwd.rfind('project-ais')], 'project-ais')
    path_preds = os.path.join(path_project, 'model_data')
    path_param = os.path.join(path_project, 'parameters')
except:
    pwd = os.getcwd()
    path_project = os.path.join(pwd[:pwd.rfind('project-ais')], 'project-ais')
    path_preds = os.path.join(path_project, 'model_data')
    path_param = os.path.join(path_project, 'parameters')

d_risk_type = {'moderate': 0.8, 'high': 1.2}

def get_recommendation(year, week, investment, risk=None, industries=None):
    try:
        year = int(year)
        week = int(week)
        investment = int(investment)
        if (industries != None) & (industries != 'None'):
            industries = ast.literal_eval(industries)
        df_test = pd.read_csv(f'{path_preds}/predictions.csv')
        df_tickerDetails = pd.read_csv(f'{path_param}/ticker_details.csv')
        df_test = pd.merge(df_test, df_tickerDetails, how='left',
                           on='ticker')
        l_colsEnd = ['ticker', 'name', 'industry', 'last_price', 'pred_pct']
        df_test = df_test[(df_test['pred_year'] == year) &
                        (df_test['pred_week'] == week)]
        if industries != None:
            df_test = df_test[df_test['industry'].isin(industries)]
        if risk == 'low':
            df_test = df_test[df_test['risk_type'].isin(['low'])]
        elif risk == 'moderate':
            df_test = df_test[df_test['risk_type'].isin(['moderate', 'low'])]
        df_test = df_test.sort_values(by=['pred_pct', 'risk'],
                                    ascending=[False, True])
        df_end = df_test[0:5][l_colsEnd]
        if len(df_end) == 0:
            j_res = {'type': 'no_strategy'}
        else:
            df_end['earnings'] = df_end['pred_pct'] * (investment / 5)
            df_end['pred_pct'] = (df_end['pred_pct']*100).round(2)
            v_ttl_earn = df_end['earnings'].sum()
            v_ttl_earn_pct = round(v_ttl_earn / investment * 100, 2)
            j_res = {'type': 'strategy',
                    'data': df_end.to_json(index=False,
                                           orient='split'),
                    'total_earnings': int(v_ttl_earn),
                    'roi': v_ttl_earn_pct}
    except Exception as e:
        j_res = {'type': 'error',
                 'error_message': getattr(e, 'message', repr(e))}
    return j_res

def get_historic_sample(year, week, investment, risk=None, industries=None):
    try:
        year = int(year)
        week = int(week)
        investment = int(investment)
        l_yw=[]
        d = dt.datetime.strptime(f'{year}-{week}-1', '%Y-%W-%w')
        for n in range(1, 5):
            d2 = d - dt.timedelta(days=7*n)
            d_f = d - dt.timedelta(days=7*(n-1))
            y1 = d_f.isocalendar()[0]
            w1 = d_f.isocalendar()[1]
            y = d2.isocalendar()[0]
            w = d2.isocalendar()[1]
            l_yw.append((y, w, y1, w1))
        if (industries != None) & (industries != 'None'):
            industries = ast.literal_eval(industries)
        df_test = pd.read_csv(f'{path_preds}/predictions.csv')
        df_tickerDetails = pd.read_csv(f'{path_param}/ticker_details.csv')
        df_test = pd.merge(df_test, df_tickerDetails, how='left',
                           on='ticker')
        if industries != None:
            df_test = df_test[df_test['industry'].isin(industries)]
        if risk == 'low':
            df_test = df_test[df_test['risk_type'].isin(['low'])]
        elif risk == 'moderate':
            df_test = df_test[df_test['risk_type'].isin(['moderate', 'low'])]
        df_test = df_test.sort_values(by=['pred_pct', 'risk'],
                                    ascending=[False, True])
        df_end = pd.DataFrame()
        df_summary = pd.DataFrame()
        #l_colsEnd = ['ticker', 'name', 'industry', 'last_price', 'pred_pct']
        #df_test = df_test[l_colsEnd]
        for y, w, y1, w1 in l_yw:
            _df = df_test[(df_test['pred_year']==y) &
                          (df_test['pred_week']==w)]
            _df_future = df_test[(df_test['pred_year']==y1) &
                                 (df_test['pred_week']==w1)][['ticker', 'last_price']].rename(columns={'last_price': 'future_price'})
            _df = pd.merge(_df, _df_future, how='left', on='ticker')
            df_end = pd.concat([df_end, _df[0:5]])
            df_end['real_pctc'] = df_end['future_price'] / df_end['last_price'] - 1
            df_end['real_earnings'] = df_end['real_pctc'] * (investment / 5)
            df_end['pred_earnings'] = df_end['pred_pct'] * (investment / 5)
            df_end['pred_pct'] = (df_end['pred_pct']*100).round(2)
            v_pred_earn = df_end['pred_earnings'].sum()
            v_real_earn = df_end['real_earnings'].sum()
            v_pred_earn_pct = round(v_pred_earn / investment * 100, 2)
            v_real_earn_pct = round(v_real_earn / investment * 100, 2)
            df_end = pd.DataFrame({'pred_year': [y],
                                   'pred_week': [w],
                                   'pred_earnings': [v_pred_earn],
                                   'real_earnings': [v_real_earn],
                                   'pred_earnings_pct': [v_pred_earn_pct],
                                   'real_earnings_pct': [v_real_earn_pct]})
            df_summary = pd.concat([df_summary, df_end])
        v_ttl_pred_earn = df_summary['pred_earnings'].sum()
        v_ttl_real_earn = df_summary['real_earnings'].sum()
        v_ttl_pred_earn_pct = round(v_ttl_pred_earn / investment * 100, 2)
        v_ttl_real_earn_pct = round(v_ttl_real_earn / investment * 100, 2)
        if len(df_summary) == 0:
            j_res = {'type': 'no_strategy'}
        else:

            j_res = {'type': 'strategy',
                    'data': df_summary.to_json(index=False,
                                               orient='split'),
                    'pred_total_earnings': int(v_ttl_pred_earn),
                    'real_total_earnings': int(v_ttl_real_earn),
                    'pred_roi': v_ttl_pred_earn_pct,
                    'real_roi': v_ttl_real_earn_pct}
    except Exception as e:
        j_res = {'type': 'error',
                 'error_message': getattr(e, 'message', repr(e))}
    return j_res
