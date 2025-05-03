from typing import List
import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin


class OutlierHandler(BaseEstimator, TransformerMixin):
    """Handle outliers in the dataset."""

    def __init__(self, columns: List[str], threshold: float = 3.0):
        self.columns = columns
        self.threshold = threshold

    def fit(self, X: pd.DataFrame, y: pd.Series = None):
        # we need the fit statement to accomodate the sklearn pipeline
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        df = X.copy()
        for col in self.columns:
            mean = df[col].mean()
            std = df[col].std()
            upper_limit = mean + self.threshold * std
            lower_limit = mean - self.threshold * std
            df[col] = np.where(df[col] > upper_limit, upper_limit, df[col])
            df[col] = np.where(df[col] < lower_limit, lower_limit, df[col])
        return df