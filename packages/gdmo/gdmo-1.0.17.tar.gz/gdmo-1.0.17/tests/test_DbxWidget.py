import unittest
from unittest.mock import MagicMock
from gdmo import DbxWidget

class TestDbxWidget(unittest.TestCase):

    def test_widget_creation_invalid_type(self):
        dbutils = MagicMock()
        with self.assertRaises(ValueError):
            DbxWidget(dbutils, "invalid_widget", type='invalid_type')

    def test_widget_creation_invalid_return_type(self):
        dbutils = MagicMock()
        with self.assertRaises(ValueError):
            DbxWidget(dbutils, "invalid_widget", returntype='invalid_return_type')

if __name__ == '__main__':
    unittest.main()