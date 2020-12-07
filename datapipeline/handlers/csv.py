"""
This module should contain all common csv based operations
"""
import logging
from os.path import basename

import pandas as pd

logger = logging.getLogger(__name__)

# The use of this class is not mandatory
class CSVReader:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    @classmethod
    def read(cls, filepath: str, **read_kwargs) -> "CSVReader":
        """
        Read a csv file into Dataframe
        :param filepath: string path of the file to read
        :param read_kwargs: Pandas read_csv keyword arguments
        :return: Dataframe representation of the csv file
        """
        df: pd.DataFrame = pd.read_csv(filepath, **read_kwargs).pipe(cls._sanitize)
        # OR for more clarity
        # df: pd.DataFrame = pd.read_csv(filepath, **read_kwargs)
        # sanitized_df = cls._sanitize(raw_df)
        logger.info("%d rows fetched from file %s", len(df.index), basename(filepath))
        return cls(df)

    @staticmethod
    def _sanitize(df: pd.DataFrame) -> pd.DataFrame:
        """
        Method used to sanitize the dataframe. It should normalize the dataframe data
        In this example I just normalize the date format (It's true that I can do this in the read method)
        but we can imagine an index validation/transformation or invalid characters handling.
        All those manipulation depends on the need.
        :param df: Data frame to sanitize
        :return: Sanitized Dataframe
        """
        if "date" in df.columns:
            df.date = pd.to_datetime(
                df.date, infer_datetime_format=True, cache=True
            ).dt.strftime("%Y-%m-%d")
        return df
