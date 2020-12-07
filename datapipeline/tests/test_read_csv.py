import unittest
from os.path import dirname, join, realpath

from datapipeline.handlers.csv import CSVReader

FIXTURES_DIR = join(dirname(realpath(__file__)), "../fixtures")


class CSVReaderTest(unittest.TestCase):

    def test_read_csv(self):
        drugs_filepath = join(FIXTURES_DIR, "drugs.csv")
        df = CSVReader.read(drugs_filepath).df
        self.assertEqual(len(df.index), 7)
