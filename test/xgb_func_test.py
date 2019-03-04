#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/11 17:52
# @Author  : zsj
# @File    : xgb_func_test.py
# @Description:
from db.mysql_operation import insert_train_datas, connectdb, query_table, create_table
from isolate_model.base_function import load_csv, save_xgboost_class, load_xgboost_class
from isolate_model.isolate_class import Isolate
from xgboost_model.xgboost_class import XGBoost

# cases = load_csv("../file/customs_cpu_test.csv")
# isolate1 = Isolate('2_7', cases)
# np_array = isolate1.merge_arrays()
# table_name = np_array[1, 0]
# db = connectdb()
# if not query_table(db, table_name):
#     create_table(db, np_array[0], table_name)
#
# insert_train_datas(db, table_name, np_array[1:])
#
#
# xgb1 = XGBoost(table_name)
# print(xgb1.name)
# save_xgboost_class(xgb1)
# pre = load_xgboost_class("982c78b5-435a-40b3-9a31-9fb5fbf8b16")
# print(pre.precision, pre.recall, pre.lasted_update)


