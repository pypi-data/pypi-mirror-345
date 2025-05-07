import unittest
from unittest.mock import MagicMock
from pyspark.sql import SparkSession
from gdmo.tables.gold import Gold_Consolidation

class TestGoldConsolidation(unittest.TestCase):

    def setUp(self):
        # Mocking dbutils and SparkSession
        self.dbutils = MagicMock()
        self.spark = MagicMock(spec=SparkSession)
        self.gold_consolidation = Gold_Consolidation(
            dbutils=self.dbutils,
            spark=self.spark,
            database='pytest',
            gold_table='test_gold_table'
        )
        

    def test_set_catalog(self):
        # Creating an instance of Gold_Consolidation
        
        self.gold_consolidation.set_catalog('new_catalog')
        self.assertEqual(self.gold_consolidation.get_catalog(), 'new_catalog')

    def test_set_refresh(self):
        self.gold_consolidation.set_refresh('partial')
        self.assertEqual(self.gold_consolidation.get_refresh(), 'partial')

    def test_set_config(self):
        config = {
            'partitioncolumns': ['firstcol','secondcol'],

            'loadType': 'merge',                            
            'loadmechanism': 'timeseries',                  

            'timeseriesFilterColumn': 'date',          
            'timeseriesFilterValue': 12,          

            'joincolumns': ['id','name','date']
        }
        self.gold_consolidation.set_config(config)
        self.assertEqual(self.gold_consolidation.get_config()['joincolumns'], ['id','name','date'])
        self.assertEqual(self.gold_consolidation.get_config()['loadType'], 'merge')
        self.assertEqual(self.gold_consolidation.get_config()['partitioncolumns'], ['firstcol','secondcol'])
        self.assertEqual(self.gold_consolidation.get_config()['timeseriesFilterColumn'], 'date')
        self.assertEqual(self.gold_consolidation.get_config()['timeseriesFilterValue'], 12)

    def test_set_not_parallel(self):
        self.gold_consolidation.set_not_parallel()
        self.assertFalse(self.gold_consolidation.get_parallel())

    def test_set_verbose(self):
        self.gold_consolidation.set_verbose()
        self.assertTrue(self.gold_consolidation.get_verbose())

if __name__ == '__main__':
    unittest.main()