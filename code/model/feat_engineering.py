from math import pi
from numpy import cos, sin
import pandas as pd

def feat_engin(df_unscaled):
    """
    This function creates features for unscaled data. Returns a DataFrame
    that includes all original features and the new ones
    """
    df_unscaled = df_unscaled.copy()
    l_feat_pctSentiment = ['ttl_sentiment', 'polarity_neg_pct',
                            'polarity_neu_pct', 'polarity_pos_pct']
    def ttl_pct_sentiment(data):
        data['ttl_sentiment'] = data[['polarity_neg', 'polarity_neu', 'polarity_pos']].sum(axis=1)
        data['polarity_neg_pct'] = data['polarity_neg'] / data['ttl_sentiment']
        data['polarity_neu_pct'] = data['polarity_neu'] / data['ttl_sentiment']
        data['polarity_pos_pct'] = data['polarity_pos'] / data['ttl_sentiment']
        return data[l_feat_pctSentiment]
    l_feat_cyclical = ['month_sin', 'month_cos', 'woy_sin', 'woy_cos']
    def cyclical_feat(data):
        l_cols = ['month', 'woy']
        for col in l_cols:
            data[f'{col}_sin'] = sin(2 * pi * data[col] / data[col].max())
            data[f'{col}_cos'] = cos(2 * pi * data[col] / data[col].max())
        return data[l_feat_cyclical]
    def feature_engineering(data):
        l_features = [ttl_pct_sentiment(data),
                    cyclical_feat(data)]
        return pd.concat(l_features, axis=1)
    l_ftengin = l_feat_pctSentiment + l_feat_cyclical
    df_feat = df_unscaled.copy()
    df_feat = feature_engineering(df_feat)
    return pd.concat([df_unscaled, df_feat], axis=1).fillna(0)
