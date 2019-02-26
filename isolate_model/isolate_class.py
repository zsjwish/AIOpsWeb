#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/12/16 17:19
# @Author  : zsj
# @File    : isolate_class.py
# @Description:
import numpy as np
from sklearn.ensemble import IsolationForest


class Isolate:
    def __init__(self, name, test_cases, cases_size=256, rate=0.1):
        """
        初始化孤立森林
        :param test_cases: 测试集
        :param cases_size: 测试集大小，默认为256
        :param rate: 异常比例，默认为0.1
        """
        # 模型的标志，每个模型名字独一无二
        self.name = name
        self.test_cases = test_cases
        # 数据集第一列，host_id
        self.host_id = test_cases[:, 0]
        # print("host_id:", self.host)
        # 数据集第一行，返回的时候对应返回
        self.title = test_cases[0, 1:]
        # print("title:", self.title)
        # 数据集真实数据,第一行是title,第一列是时间
        self.cases = test_cases[1:, 2:].astype(np.float32)
        # print("cases:", self.cases)
        # 定义测试集大小，默认为256
        self.cases_size = cases_size
        # 定义测试集异常比例，默认为0.1
        self.rate = rate
        # 随机因子，以时间戳为随机因子
        self.rng = np.random.RandomState()
        # label初始化并都置位0，后续判断为1后再更新
        self.label_list = np.zeros((len(self.cases), 1), dtype = int)
        # 初始化模型，如果模型要更改就直接在该函数中修改
        self.clf = IsolationForest(behaviour = 'new', max_samples = self.cases_size,
                                   random_state = self.rng, contamination = self.rate)
        self.init_model()

    def init_model(self):
        # 初始化模型、训练及大小，异常数据比例
        # 训练数据,如果数据量大则采用分段训练，因为最终采用xgboost判断，这里只生成标签
        self.clf.fit(self.cases)
        i = 0
        while i * 256 < len(self.cases):
            self.init_fit(self.cases, i * 256, min(len(self.cases), (i + 1) * 256))
            i += 1
        print("length", len(self.label_list))
        print('-------训练完成--------')
        print("result:", self.merge_arrays())

    def merge_arrays(self):
        """
        重新拼接数据，包括title, label，数据集，host_id等
        :return:
        """
        print(self.title)
        print(type(self.title))
        array_label = np.array(["label"])
        title = np.concatenate((self.title, array_label))
        print(self.test_cases[1:, 1])
        # 拼接数据集和label
        cases_label = np.c_[self.test_cases[1:, 1], self.cases, self.label_list]
        # 拼接title，数据集，label
        title_cases_label = np.concatenate((title.reshape(1, len(title)), cases_label), axis = 0)
        # 拼接title，数据集,label,host_id
        res = np.concatenate((self.host_id.reshape(len(self.host_id), 1), title_cases_label), axis = 1)
        return res

    def init_fit(self, datas, start_row, end_row):
        """
        批量训练并判断是否异常
        :param datas:
        :param start_row:
        :param end_row:
        :return:
        """
        self.clf.fit(datas[start_row:end_row])
        self.judge_multy(datas, start_row, end_row)

    def judge_multy(self, datas, start_row, end_row):
        """
        判断批量数据是否是异常数据，返回异常数据集合，如果没有异常返回true
        :param datas: 数据集合
        :param start_row: 开始行数
        :param end_row:  结束行数
        :return:
        """
        # 获取异常检测结果，结果放在label_list中
        multy_res = self.clf.predict(datas[start_row:end_row].astype(np.float32))
        for i in range(0, len(multy_res)):
            if multy_res[i] == -1:
                self.label_list[start_row + i] = 1

