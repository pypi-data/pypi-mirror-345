# csvinspector/utils.py

import pandas as pd
import numpy as np

def detect_feature_types(df):
    types = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            types[col] = "Numerical"
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            types[col] = "Datetime"
        elif pd.api.types.is_categorical_dtype(df[col]) or df[col].nunique() < 20:
            types[col] = "Categorical"
        else:
            types[col] = "Text"
    return types

def get_missing_data_info(df):
    missing_info = df.isnull().sum()
    missing_percent = (missing_info / len(df)) * 100
    return pd.DataFrame({
        "Missing Count": missing_info,
        "Missing %": missing_percent
    }).sort_values(by="Missing Count", ascending=False)

def get_outlier_summary(df):
    summary = {}
    for col in df.select_dtypes(include='number').columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        summary[col] = {
            "count": len(outliers),
            "percent": (len(outliers) / len(df)) * 100
        }
    return pd.DataFrame(summary).T.sort_values(by="count", ascending=False)

def get_skewed_features(df, threshold=1.0):
    from scipy.stats import skew
    skewness = df.select_dtypes(include='number').apply(skew).sort_values(ascending=False)
    suggestions = {}
    for col, skew_val in skewness.items():
        if abs(skew_val) > threshold:
            suggestions[col] = {
                "skew": skew_val,
                "suggested_transform": "log1p" if (df[col] > 0).all() else "sqrt"
            }
    return suggestions

def get_normalization_summary(df):
    from sklearn.preprocessing import StandardScaler, MinMaxScaler

    scaler_results = {}
    numeric_df = df.select_dtypes(include='number')

    for name, scaler in [("StandardScaler", StandardScaler()), ("MinMaxScaler", MinMaxScaler())]:
        scaled = scaler.fit_transform(numeric_df)
        scaled_df = pd.DataFrame(scaled, columns=numeric_df.columns)
        scaler_results[name] = scaled_df.describe().T

    return scaler_results


def remove_outliers_iqr(df, features, factor=1.5):
    clean_df = df.copy()
    removed_stats = {}
    for col in features:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - factor * IQR
        upper_bound = Q3 + factor * IQR
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        removed_stats[col] = {
            "original_count": df.shape[0],
            "outlier_count": outliers.shape[0],
            "retained_count": df[(df[col] >= lower_bound) & (df[col] <= upper_bound)].shape[0]
        }
        clean_df = clean_df[(clean_df[col] >= lower_bound) & (clean_df[col] <= upper_bound)]
    return clean_df, removed_stats


def get_correlation_matrix(df):
    return df.select_dtypes(include='number').corr()
