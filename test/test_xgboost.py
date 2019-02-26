import unittest

import numpy as np

from db.mysql_operation import connectdb, query_datas
from isolate_model.base_function import load_data_for_xgboost_from_mysql


class XgboostCase(unittest.TestCase):
    def test_load_data_from_mysql(self):
        table_name = "20bc4dbb-f7f8-4521-9187-7dc31cac76e"
        np_array = load_data_for_xgboost_from_mysql(table_name)
        print(np_array)

if __name__ == '__main__':
    unittest.main()
