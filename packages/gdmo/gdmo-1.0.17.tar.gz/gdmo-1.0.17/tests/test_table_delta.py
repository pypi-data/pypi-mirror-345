import unittest
from unittest.mock import MagicMock
from pyspark.sql import SparkSession
from gdmo import Delta

class test_table_delta(unittest.TestCase):

    def setUp(self):
        # Mocking SparkSession
        self.spark = MagicMock(spec=SparkSession)
        self.spark.catalog.listDatabases.return_value = [MagicMock(name='default'), MagicMock(name='test_db')]

        # Creating an instance of DeltaTable
        self.delta_table = Delta(
            db_name='pytest',
            table_name='test_table',
            spark=self.spark,
            catalog='test_catalog'
        )

    def test_set_columns(self):
        columns = [
            {'name': 'id', 'data_type': 'int', 'comment': 'primary key'},
            {'name': 'name', 'data_type': 'string', 'comment': 'name of the person'}
        ]
        self.delta_table.set_columns(columns)
        self.assertEqual(self.delta_table.get_columns(), columns)

    def test_set_comment(self):
        comment = "This is a test table comment."
        self.delta_table.set_comment(comment)
        self.assertEqual(self.delta_table.get_comment(), comment)

    def test_set_options(self):
        options = {'mergeSchema': 'true', 'overwriteSchema': 'true'}
        self.delta_table.set_options(options)
        self.assertEqual(self.delta_table.get_options(), options)

    def test_set_location(self):
        location = "/path/to/table/location"
        self.delta_table.set_location(location)
        self.assertEqual(self.delta_table.get_location(), location)

    def test_set_partitioning(self):
        partitioning = "date"
        self.delta_table.set_partitioning(partitioning)
        self.assertEqual(self.delta_table.get_partitioning(), partitioning)

    def test_set_identity(self):
        identity_column = 'id'
        self.delta_table.set_identity(identity_column)
        self.assertEqual(self.delta_table.get_identity(), identity_column)



if __name__ == '__main__':
    unittest.main()