import unittest
from unittest.mock import MagicMock
from pyspark.sql import SparkSession
from gdmo import Landing

# FILE: gdmo/tables/test_landing.py


class test_table_landing(unittest.TestCase):
    def setUp(self):
        # Mocking dbutils and SparkSession
        self.dbutils = MagicMock()
        self.spark = MagicMock(spec=SparkSession)
        self.test_landing = Landing(self.spark, self.dbutils, 'pytest', 'test_table', target_folder = 'abfss://target_folder', filename = 'filename', catalog = 'catalog', container = 'container')

    def test_set_config(self):
        config = {
            'loadtype': 'merge',          
            'join': ['col1','col2']
        }
        self.test_landing.set_config(config)
        self.assertEqual(self.test_landing.get_config()['loadtype'], 'merge')
        self.assertEqual(self.test_landing.get_config()['join'], ['col1','col2'])


if __name__ == '__main__':
    unittest.main()