import os
import pandas as pd
import ast

try:
    pwd = os.path.abspath(__file__)
    path_project = os.path.join(os.path.dirname(os.path.dirname(pwd)))
    path_preds = os.path.join(path_project, 'model_data')
    path_param = os.path.join(path_project, 'parameters')
except:
    pwd = os.getcwd()
    path_preds = os.path.join(pwd, 'model_data')
    path_param = os.path.join(pwd, 'parameters')

d_risk_type = {'moderate': 0.8, 'high': 1.2}

def get_recommendation(year, week, investment, risk=None, industries=None):
    try:
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
                    'data': df_end.to_json(),
                    'total_earnings': int(v_ttl_earn),
                    'roi': v_ttl_earn_pct}
    except Exception as e:
        j_res = {'type': 'error',
                 'error_message': getattr(e, 'message', repr(e))}
    return j_res
