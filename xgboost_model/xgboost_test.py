#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/12/28 16:38
# @Author  : zsj
# @File    : xgboost_test.py
# @Description:

import numpy as np
import xgboost as xgb

from isolate_model.base_function import load_csv, translate_to_xgboost_datas
from isolate_model.isolate_class import Isolate

# cases = load_csv("../file/predict.csv")
# # isolate1 = Isolate('2_7', cases)
# # np_array = isolate1.merge_arrays()
# np_array = translate_to_xgboost_datas(cases)
#
# # 从文本文件加载文件，也是由xgboost生成的二进制缓冲区，加载能训练的文件，
# np_array = np_array[1:]
# print("nparray", np_array)
# length = len(np_array)
# print(length)
# # 按行打乱顺序，然后从中选择训练集，测试集, 验证集
# np.random.shuffle(np_array)
# rate = [8, 1, 1]
# total_rate = sum(rate)
# rate_num1 = int(length * rate[0] / total_rate)
# rate_num2 = int(length * (rate[0] + rate[1]) / total_rate)
# print(rate_num1)
# print(rate_num2 - rate_num1)
# dtrain = xgb.DMatrix(np_array[0:rate_num1, 1:-1].astype(float),
#                      label = np_array[0: rate_num1, -1].astype(int))
# dtest = xgb.DMatrix(np_array[rate_num1 + 1: rate_num2, 1:-1].astype(float),
#                     label = np_array[rate_num1 + 1: rate_num2, -1].astype(int))
# verify = xgb.DMatrix(np_array[rate_num2 + 1: -1, 1:-1].astype(float),
#                      label = np_array[rate_num2 + 1: -1, -1].astype(int))
# # 通过map指定参数，max_depth：树的最大深度，太大容易过拟合
# # xgboost参数
# param = {
#     'booster': 'gbtree',  # 助推器，默认为gbtree，可不写
#     'verbosity': 0,  # verbosity：1警告信息
#     'objective': 'binary:logistic',  # objective：binary：logistic 二分类逻辑回归，输出概率
#     'max_depth': 10,  # 最大深度，默认为6
#     'eta': 0.05,  # eta 步长
#     'subsample': 0.9,  # 使用0.9训练，0.1样本测试
#     'evals': 'auc'
# }
#
# # specify validations set to watch performance
# watchlist = [(dtrain, 'train1'), (dtest, 'test1'), (verify, 'verify1')]
# # num_round 提升的轮次数
# num_round = 10
# # 训练数据
# bst = xgb.train(param, dtrain, num_round, watchlist)
#
# # 测试集预测
# preds = bst.predict(dtest)
# print(preds)
# print(len(preds))
# print(sum(preds >= 0.5))
# print(sum(preds < 0.5))
# # 测试预测
# np_test = np.array([[2, 19, 22, 99.3], [3, 10, 10, 6.36]])
# test_matrix = xgb.DMatrix(np_test)
# pre_test = bst.predict(test_matrix)
# print(pre_test)
# # 测试集label，用于计算测试集错误率
# labels = dtest.get_label()
# # 测试集错误率
# print('error=%f' % (sum(1 for i in range(len(preds)) if int(preds[i] > 0.5) != labels[i]) / float(len(preds))))
# # 存储模型
# bst.save_model('0001.model')
# # 模型及其特征映射也可以转储到文本文件中
# bst.dump_model('dump.raw.txt')
#
# bst.load_model('model.bin')
# 存储模型特征xr
# bst.dump_model('dump.nice.txt', 'featmap.txt')

# save dmatrix into binary buffer
# dtest.save_binary('dtest.buffer')
# # save model
# bst.save_model('xgb.model')
# # load model and data in
# bst2 = xgb.Booster(model_file = 'xgb.model')
# dtest2 = xgb.DMatrix('dtest.buffer')
# preds2 = bst2.predict(dtest2)
# # assert they are the same
# assert np.sum(np.abs(preds2 - preds)) == 0
#
# # alternatively, you can pickle the booster
# pks = pickle.dumps(bst2)
# # load model and data in
# bst3 = pickle.loads(pks)
# preds3 = bst3.predict(dtest2)
# # assert they are the same
# assert np.sum(np.abs(preds3 - preds)) == 0
#
# ###
# # build dmatrix from scipy.sparse
# print('start running example of build DMatrix from scipy.sparse CSR Matrix')
# labels = []
# row = []
# col = []
# dat = []
# i = 0
# for l in open('../data/agaricus.txt.train'):
#     np_array = l.split()
#     labels.append(int(np_array[0]))
#     for it in np_array[1:]:
#         k, v = it.split(':')
#         row.append(i);
#         col.append(int(k));
#         dat.append(float(v))
#     i += 1
# csr = scipy.sparse.csr_matrix((dat, (row, col)))
# dtrain = xgb.DMatrix(csr, label = labels)
# watchlist = [(dtest, 'eval'), (dtrain, 'train')]
# bst = xgb.train(param, dtrain, num_round, watchlist)
#
# print('start running example of build DMatrix from scipy.sparse CSC Matrix')
# # we can also construct from csc matrix
# csc = scipy.sparse.csc_matrix((dat, (row, col)))
# dtrain = xgb.DMatrix(csc, label = labels)
# watchlist = [(dtest, 'eval'), (dtrain, 'train')]
# bst = xgb.train(param, dtrain, num_round, watchlist)
#
# print('start running example of build DMatrix from numpy array')
# # NOTE: npymat is numpy array, we will convert it into scipy.sparse.csr_matrix in internal implementation
# # then convert to DMatrix
# npymat = csr.todense()
# dtrain = xgb.DMatrix(npymat, label = labels)
# watchlist = [(dtest, 'eval'), (dtrain, 'train')]
# bst = xgb.train(param, dtrain, num_round, watchlist)



from xgboost_model.xgboost_class import XGBoost

xgb1 = XGBoost("982c78b5-435a-40b3-9a31-9fb5fbf8b16")

