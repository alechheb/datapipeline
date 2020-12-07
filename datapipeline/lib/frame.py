"""
This module should contain all pandas frames based operations
"""
__all__ = ["merge", "group_by", "combine_dict"]
from typing import Callable, List, Union

import pandas as pd

from datapipeline.lib.measurement import log_duration


@log_duration
def merge(
    pivot: pd.DataFrame, other: pd.DataFrame, check_func: Callable[[pd.Series], bool]
) -> pd.DataFrame:
    """
    Merge 2 dataframes without using columns nor indexes and apply check_func to filter matched rows
    :param pivot: Pivot dataframe (Left)
    :param other: Dataframe to merge with (Right)
    :param check_func: Function used to check correspondence
    :return: A DataFrame of the two merged dataframes
    """
    pivot["join"] = other["join"] = 1
    merged_df = pivot.merge(other, on="join").drop("join", axis=1)
    other.drop("join", axis=1, inplace=True)
    merged_df["match"] = merged_df.apply(check_func, axis=1)
    return merged_df.loc[merged_df.match].reset_index(drop=True).drop("match", axis=1)


@log_duration
def group_by(df, by: List, grouped_cols) -> pd.DataFrame:
    """
    Group DataFrame using a list of columns (by) and combine them into one row.
    :param df: Dataframe to group
    :param by: lis tof columns to use as group key
    :param grouped_cols: columns to be combined
    :return: Grouped Dataframe
    """
    return df.groupby(by)[grouped_cols].apply(lambda x: x.to_dict(orient="records"))


def combine_dict(trial: Union[List, float], pubmed: Union[List, float]):
    return {
        "trial": trial if isinstance(trial, list) else [],
        "pubmed": pubmed if isinstance(pubmed, list) else [],
    }
