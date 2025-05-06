import random

def inject_edge_cases(df, description):
    if 'amount' in df.columns:
        df.loc[random.randint(0, len(df)-1), 'amount'] = -99999
    if 'email' in df.columns:
        df.loc[random.randint(0, len(df)-1), 'email'] = '!!!INVALID_EMAIL!!!'
    return df
