import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

def clean_and_transform(df):
    cols_to_drop = [col for col in df.columns if (df[col] == -1).all()]
    df = df.drop(columns=cols_to_drop)

    for col in df.columns:
        if df[col].dtype in ['int64', 'float64']:
            median_val = df[df[col] != -1][col].median()
            df[col] = df[col].replace(-1, median_val)

    skewed_cols = ['Submit Time', 'Wait Time', 'Run Time', 'Requested Time']
    for col in skewed_cols:
        if col in df.columns:
            df[col] = np.log1p(df[col])

    return df, skewed_cols

def scale_data(df):
    scaler = StandardScaler()
    scaled = scaler.fit_transform(df)
    return scaled, scaler