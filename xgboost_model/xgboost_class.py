#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/12/28 16:35
# @Author  : zsj
# @File    : xgboost_class.py
# @Description:
import time
import numpy as np
import xgboost as xgb

from db.mysql_operation import insert_xgboost_model, update_xgboost_model
from isolate_model.base_function import load_data_for_xgboost_from_mysql, save_xgboost_class

class XGBoost:
    def __init__(self, file_name, model_name):
        print("xgboost init --------------------------------------")
        self.file_name = file_name
        self.name = model_name
        self.param = {
            'booster': 'gbtree',  # 助推器，默认为gbtree，可不写
            'verbosity': 0,  # verbosity：1警告信息
            'objective': 'binary:logistic',  # objective：binary：logistic 二分类逻辑回归，输出概率
            'max_depth': 10,  # 最大深度，默认为6
            'eta': 0.7,  # eta 步长同learning_rate，步长，越小算法越保守，默认0.3
            'subsample': 0.7,  # 每次取一定比例的样本进行训练，防止过拟合，默认为1
            'evals': ['error', 'auc', 'rmse']  # 验证数据的评估指标，将根据目标分配默认指标

        }
        # 决策树的颗数
        self.num_round = 10
        # 精确率
        self.precision = 0.
        # 召回率
        self.recall = 0.
        # F1值
        self.f1 = 0.
        # 测试集总数量，训练总数量
        self.trained_number = 0
        # 是否训练完成,0未完成，1完成
        self.finished = 0
        # 模型最近是否发生了改变,0未改变，1已改变，需要重新训练
        self.changed = 0
        # 模型初始化时间
        self.create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # 模型最后更新时间
        self.lasted_update = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # 插入数据库
        self.insert_database_model()
        # 初始化模型
        self.model = self.init_model()

    def init_model(self):
        # 从数据库获取数据，model_name就是表名
        datas = load_data_for_xgboost_from_mysql(self.name)
        # 按行打乱顺序，然后从中选择训练集，测试集, 验证集
        np.random.shuffle(datas)
        # 训练集和测试集取9:1，用于取准备率和召回率
        rate = [7, 3]
        # 训练集总数量
        self.trained_number = len(datas)
        # 总比例，用于取出训练集和测试集
        total_rate = sum(rate)
        rate_num1 = int(self.trained_number * rate[0] / total_rate)
        # 训练集
        dtrain = xgb.DMatrix(datas[0:rate_num1, 0:-1].astype(float),
                             label = datas[0: rate_num1, -1].astype(int))
        # 验证集
        dtest = xgb.DMatrix(datas[rate_num1 + 1: -1, 0:-1].astype(float),
                            label = datas[rate_num1 + 1: -1, -1].astype(int))
        # 显示训练过程
        watchlist = [(dtrain, 'train'), (dtest, 'test')]
        # 训练模型并使用验证集验证
        bst = xgb.train(self.param, dtrain, self.num_round, watchlist)
        # 预测测试集数据
        preds = bst.predict(dtest)
        # 原本测试集的label
        labels = dtest.get_label()
        # 真实为1，预测为1
        TP = 0
        # 真实为1，预测为0
        FN = 0
        # 真实为0，预测为1
        FP = 0
        # 真实为0，预测为0
        TN = 0
        p = []
        for i, label in enumerate(labels):
            p.append(int(preds[i] + 0.5))
            if preds[i] >= 0.5:
                if label == 1:
                    TP += 1
                else:
                    FP += 1
            else:
                if label == 1:
                    FN += 1
                else:
                    TN += 1
        print("TP", TP)
        print("FN", FN)
        print("FP", FP)
        print("TN", TN)
        # 得出精确率、召回率和F1
        if TP + FP == 0:
            self.precision = 1
        else:
            self.precision = TP / float(TP + FP)
        if TP + FN == 0:
            self.recall = 1
        else:
            self.recall = TP / float(TP + FN)
        self.f1 = self.precision * self.recall * 2 / float(self.precision + self.recall)
        self.lasted_update = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # 更新模型
        self.model = bst
        # 更新数据库
        self.update_database_model()
        # 返回模型
        time.sleep(10)
        return bst

    def predict(self, data):
        """
        对格式化后的数据进行预测，如果判断为异常则返回1，判断正常则返回0
        :param data: 格式化后的数据，即时间已转换成星期，小时，分钟，没有label，
        :return: 异常1， 正常0
        """
        return int(self.model.predict(xgb.DMatrix(data)) + 0.5)

    def insert_database_model(self):
        """
        插入数据到model表中，初始化的时候会插入数据，后续都是update
        :return:插入成功，返回True,失败返回False
        """
        if insert_xgboost_model(self.file_name, self.name, self.precision, self.recall,
                                self.f1, self.trained_number, self.finished,
                                self.changed, self.create_time, self.lasted_update):
            print("插入成功")
            return True
        return False

    def update_database_model(self):
        """
        重新训练数据后会更新，只更新数据
        :return:
        """
        if update_xgboost_model(self.name, self.precision, self.recall,
                                self.f1, self.trained_number, self.finished,
                                self.changed, self.lasted_update):
            print("更新成功")
            return True
        return False




