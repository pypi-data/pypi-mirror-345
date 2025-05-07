import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime
from gdmo.forecasting.timeseriesforecast import TimeSeriesForecast

from io import StringIO

from pyspark.sql import SparkSession

class test_forecasting_tsf(unittest.TestCase):
    def setUp(self):
        self.spark = MagicMock(spec=SparkSession)
        
        data = """
Category\tTime\tValue
first cat\t1-2-2022\t3
first cat\t1-3-2023\t138
first cat\t1-9-2023\t54
first cat\t1-3-2022\t488
first cat\t1-2-2024\t65
first cat\t1-12-2022\t139
first cat\t1-4-2023\t51
first cat\t1-5-2023\t53
first cat\t1-8-2022\t2496
first cat\t1-10-2022\t147
first cat\t1-7-2023\t65
first cat\t1-11-2022\t134
first cat\t1-10-2023\t54
first cat\t1-1-2023\t140
first cat\t1-6-2023\t67
first cat\t1-6-2024\t65
first cat\t1-1-2024\t56
first cat\t1-7-2022\t5168
first cat\t1-8-2023\t57
first cat\t1-5-2024\t67
first cat\t1-2-2023\t126
first cat\t1-6-2022\t5003
first cat\t1-11-2023\t49
first cat\t1-12-2023\t47
first cat\t1-4-2022\t4171
first cat\t1-3-2024\t69
first cat\t1-4-2024\t69
first cat\t1-9-2022\t498
first cat\t1-5-2022\t4996
cat two\t1-8-2023\t3
cat two\t1-5-2024\t4
cat two\t1-4-2024\t4
cat two\t1-3-2024\t4
cat two\t1-7-2023\t3
cat two\t1-6-2024\t4
cat two\t1-9-2023\t3
cat two\t1-1-2024\t3
cat two\t1-11-2023\t3
cat two\t1-5-2023\t3
cat two\t1-10-2023\t3
cat two\t1-2-2024\t3
cat two\t1-6-2023\t2
cat two\t1-12-2023\t3
cat three\t1-6-2023\t518
cat three\t1-3-2024\t538
cat three\t1-9-2023\t522
cat three\t1-12-2022\t704
cat three\t1-1-2024\t542
cat three\t1-3-2023\t711
cat three\t1-12-2023\t526
cat three\t1-2-2024\t518
cat three\t1-11-2023\t506
cat three\t1-5-2024\t584
cat three\t1-5-2023\t501
cat three\t1-10-2022\t697
cat three\t1-2-2023\t638
cat three\t1-6-2024\t569
cat three\t1-4-2024\t562
cat three\t1-10-2023\t527
cat three\t1-4-2023\t685
cat three\t1-11-2022\t682
cat three\t1-9-2022\t663
cat three\t1-8-2022\t184
cat three\t1-8-2023\t529
cat three\t1-1-2023\t694
cat three\t1-7-2023\t524
cat five\t1-6-2023\t30
cat five\t1-11-2023\t83
cat five\t1-3-2024\t89
cat five\t1-12-2023\t85
cat five\t1-3-2023\t129
cat five\t1-4-2024\t106
cat five\t1-8-2023\t84
cat five\t1-6-2024\t137
cat five\t1-10-2023\t84
cat five\t1-1-2023\t9
cat five\t1-1-2024\t91
cat five\t1-5-2023\t131
cat five\t1-2-2023\t58
cat five\t1-4-2023\t160
cat five\t1-9-2023\t86
cat five\t1-7-2023\t84
cat five\t1-5-2024\t133
cat five\t1-2-2024\t90
cat four\t1-4-2024\t2189
cat four\t1-8-2022\t1788
cat four\t1-7-2021\t1253
cat four\t1-10-2022\t1984
cat four\t1-5-2022\t1534
cat four\t1-11-2022\t2009
cat four\t1-5-2021\t1159
cat four\t1-1-2024\t1961
cat four\t1-7-2023\t1731
cat four\t1-5-2024\t2080
cat four\t1-2-2023\t1878
cat four\t1-4-2022\t1567
cat four\t1-2-2021\t1393
cat four\t1-2-2022\t1437
cat four\t1-6-2023\t1738
cat four\t1-1-2022\t1079
cat four\t1-3-2024\t2163
cat four\t1-2-2024\t2003
cat four\t1-9-2023\t1662
cat four\t1-6-2021\t1189
cat four\t1-12-2022\t2161
cat four\t1-11-2021\t739
cat four\t1-4-2023\t1786
cat four\t1-8-2023\t1606
cat four\t1-9-2022\t1819
cat four\t1-5-2023\t1726
cat four\t1-1-2023\t2036
cat four\t1-7-2022\t1735
cat four\t1-12-2023\t2157
cat four\t1-3-2022\t1509
cat four\t1-6-2024\t2075
cat four\t1-10-2021\t776
cat four\t1-3-2021\t1611
cat four\t1-8-2021\t1126
cat four\t1-11-2023\t1846
cat four\t1-9-2021\t803
cat four\t1-6-2022\t1629
cat four\t1-10-2023\t1876
cat four\t1-4-2021\t1019
cat four\t1-12-2021\t771
cat four\t1-3-2023\t1774
        """
        new_df = pd.read_csv(StringIO(data), sep='\t')
        new_df['Time'] = pd.to_datetime(new_df['Time']).dt.strftime('%Y-%d-%m')

        forecast = TimeSeriesForecast(self.spark, 'testforecast')\
                        .set_columns(time='Time', identifier='Category', value='Value')\
                        .set_forecast_length(3)\
                        .set_last_data_point('2024-06-01')\
                        .set_input(new_df)\
                        .set_track_outcome(False)\
                        .build_forecast()
        
        self.forecast = forecast.get_forecast()

    def test_result(self):
        
        if isinstance(self.forecast, pd.DataFrame):
            print("The forecast is a pandas DataFrame.")
        elif isinstance(self.forecast, self.spark.createDataFrame(pd.DataFrame()).__class__):
            print("The forecast is a Spark DataFrame.")
        elif isinstance(self.forecast, MagicMock):
            print("The forecast is a mock DataFrame.")
        else:
            self.fail("The forecast is of an unknown type.")

if __name__ == '__main__':
    unittest.main()