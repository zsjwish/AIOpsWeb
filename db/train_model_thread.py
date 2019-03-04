#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/3/3 16:21
# @Author  : zsj
# @File    : train_model_thread.py
# @Description:
from concurrent.futures import ThreadPoolExecutor

from models.models import xgboost_name, lstm_name


def print_name(kind, model_name):
    print("kind", kind)
    print("model_name", model_name)


def train_model(model_kind, data_name):
    """训练模型"""
    from xgboost_model.xgboost_class import XGBoost
    from lstm_model.lstm_class import LSTMModel
    print("类型", type(data_name))
    print(data_name)
    if model_kind == "XGBoost":
        if data_name in xgboost_name:
            return 0
        else:
            XGBoost(data_name)
            return 1

    elif model_kind == 'LSTM':
        if data_name in lstm_name:
            return 0
        else:
            print(data_name)
            print("类型", type(data_name))
            tmp = LSTMModel(data_name)
            tmp.train()
            return 1


class TrainModelThreadPool:
    def __init__(self):
        """
        初始化一个有着5个线程的线程池，线程放在thread_queue中
        :param max_size:
        """
        with ThreadPoolExecutor(5) as executor:
            self.executor = executor

    def start_train(self, kind, model_name):
        if kind == "XGBoost":
            future = self.executor.map(fn = train_model(kind, model_name))
            print("train xgboost------------------------")

        elif kind == "LSTM":
            future = self.executor.map(fn = train_model(kind, model_name))
            print("train lstm++++++++++++++++++++++++++++")



