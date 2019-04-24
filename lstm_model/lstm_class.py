#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/16 15:43
# @Author  : zsj
# @File    : lstm_class.py
# @Description:
import math
import time

import numpy as np
from keras import Sequential
from keras.layers import LSTM, Dense, Activation
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from db.model_persistence import save_lstm_class
from db.mysql_operation import insert_lstm_model, update_lstm_model
from isolate_model.base_function import load_data_for_lstm_from_mysql



class LSTMModel:
    def __init__(self, file_name, model_name):
        print("LSTM init`````````````````````````````````````````````````````````")
        self.file_name = file_name
        self.name = model_name
        # 预测需要前面多少值
        self.look_back = 50
        # 想要预测之后多少值
        self.look_forward = 30
        # 最后预测时间
        self.lasted_predict = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # 最后预测的值,str拼接起来
        self.predict_str_value = "0"
        # 训练集测试集比例
        self.rate = [7, 3]
        # 模型初始化时间
        self.create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # 模型最后更新时间
        self.lasted_update = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # 均方根误差，用来判断模型预测效果
        self.rmse = 0
        # 每个模型预测时候不应该每次取数据库，这里设置一个用以存储以往的数据，预测时候直接使用，省去读数据库
        # self.history_data = []
        # 每次向前预测的值，每次预测look_forward个值
        self.predict_data = []
        # 初始化模型，train_x的维度为(n_samples, time_steps, input_dim)
        model = Sequential()
        # 增加LSTM网络层
        model.add(LSTM(50, input_shape = (1, self.look_back), return_sequences = True))
        model.add(LSTM(100, return_sequences = False))
        model.add(Dense(units = 1))
        model.add(Activation('linear'))
        model.compile(loss = 'mse', optimizer = 'rmsprop')
        self.model = model
        self.insert_database_model()
        self.train()

    def train(self, data=None):
        if data is None:
            # 从数据库获取数据，model_name就是表名,获取最后10000条数据作为训练集
            data = load_data_for_lstm_from_mysql(self.name, 10000)
        # 更改data shape为符合训练的size
        data = data.reshape(len(data), 1)
        # 归一化处理
        scaler = MinMaxScaler(feature_range = (0, 1))
        data = scaler.fit_transform(data)
        # 确定训练集和测试集大小
        # train_size = int(sum(self.rate) * self.rate[0])
        # train_size = int(sum(self.rate) * self.rate[0] * 5)
        train_size = int(len(data) * self.rate[0] / sum(self.rate))
        train, test = data[0:train_size, :], data[train_size:len(data), :]
        # 确定特征和Y
        trainX, trainY = create_dataset(train)
        testX, testY = create_dataset(test)
        # 转换成三维输入，sample，time step，feature
        trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
        testX = np.reshape(testX, (testX.shape[0], 1, testX.shape[1]))
        print(trainX.shape)
        print(testX.shape)
        # 模型训练
        print("model type", type(self.model))
        self.model.fit(trainX, trainY, epochs = 100, batch_size = 5, verbose = 2)
        print("model type", type(self.model))
        # 预测训练数据
        print("++++++++++", self.model.summary())
        # try:
        trainPredict = self.model.predict(trainX)
        # except Exception as e:
        #     logger.info(e)
        #     keras.backend.clear_session()
        #     lstm_model = self.model
        #     lstm_model.predict(trainX)
        # 预测测试数据
        testPredict = self.model.predict(testX)
        # 将标准化后是数据转换为原始数据
        trainPredict = scaler.inverse_transform(trainPredict)
        trainY = scaler.inverse_transform([trainY])
        testPredict = scaler.inverse_transform(testPredict)
        testY = scaler.inverse_transform([testY])
        trainScore = math.sqrt(mean_squared_error(trainY[0], trainPredict[:, 0]))
        testScore = math.sqrt(mean_squared_error(testY[0], testPredict[:, 0]))
        # self.rmse = min(trainScore, testScore)
        self.rmse = testScore
        self.lasted_predict = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.update_database_model()
        return self.model

    def create_dataset(self, dataset):
        """
        训练时对从数据库获取的数据进行处理，变成特征x和y的形式
        :param dataset:
        :return:
        """
        look_back = self.look_back
        dataX, dataY = [], []
        for i in range(len(dataset) - look_back):
            a = dataset[i:(i + look_back), 0]
            dataX.append(a)
            dataY.append(dataset[i + look_back, 0])
        return np.array(dataX), np.array(dataY)

    def create_predict_dataset(self, dataset):
        """
        预测时对从数据库获取的数据进行处理，变成特征x和y的形式,dataset是list
        :param dataset:
        :return:
        """
        look_back = self.look_back
        dataX = []
        for i in range(len(dataset) - look_back):
            a = dataset[i:(i + look_back)]
            dataX.append(a)
        return np.array(dataX)

    def predict_values(self):
        """
        预测，循环调用predict_next_value来预测之后的值，使用预测的值再预测
        :return:
        """
        # 获取该表最后50个数据作为预测的输入
        data = load_data_for_lstm_from_mysql(self.name, 50)
        data = np.reshape(data, (len(data), 1))
        data = data[-50:, :].tolist()
        self.predict_data = data
        while len(self.predict_data) < self.look_back + self.look_forward:
            tmp = self.predict_next_value(data = self.predict_data)
            self.predict_data.append(tmp)
        # 二维数据转一维数据
        self.predict_data = sum(self.predict_data, [])
        # 精确到小数点后2位
        self.predict_data = [round(i, 2) for i in self.predict_data]
        # 只取后三十个预测的值存储
        str_value = self.predict_data[(-1 * self.look_forward):]
        # 转换成str,并使用,分割
        self.predict_str_value = ','.join(str(e) for e in str_value)
        self.lasted_predict = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # 更新数据库表
        self.update_database_model()
        return str_value

    def predict_next_value(self, data):
        """
        对数据格式化后预测未来的一个值
        data 的格式是list
        :return: 预测的值
        获取当前时间:time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        """
        # 只取最后多少个作为预测
        data = data[-50:]
        # 改变ndarray的shape
        data = np.array(data).reshape(len(data), 1)
        # print("data", data)
        # 归一化处理
        scaler = MinMaxScaler(feature_range = (0, 1))
        data = scaler.fit_transform(data)
        # print(len(data))
        dataX = np.reshape(data, (data.shape[1], 1, data.shape[0]))
        # print(dataX.shape)
        dataPredict = self.model.predict(dataX)
        # print("dataPredic shape", dataPredict.shape)
        # print(dataPredict)
        Predict = scaler.inverse_transform(dataPredict)
        # print(Predict.tolist()[0])
        return Predict.tolist()[0]

    def insert_database_model(self):
        """
        插入数据到model表中，初始化的时候会插入数据，后续都是update
        :return:插入成功，返回True,失败返回False
        """
        if insert_lstm_model(self.file_name, self.name, self.rmse, self.lasted_predict,
                             self.predict_str_value, self.create_time, self.lasted_update):
            print("插入成功")
            return True
        return False

    def update_database_model(self):
        """
        重新训练数据后会更新，只更新数据
        :return:
        """
        if update_lstm_model(self.name, self.rmse, self.lasted_predict,
                             self.predict_str_value, self.lasted_update):
            print("更新成功")
            return True
        return False


def create_dataset(dataset):
    """
    对从数据库获取的数据进行处理，变成特征x和y的形式
    :param dataset:
    :return:
    """
    look_back = 50
    dataX, dataY = [], []
    for i in range(len(dataset) - look_back):
        a = dataset[i:(i + look_back), 0]
        dataX.append(a)
        dataY.append(dataset[i + look_back, 0])
    # print("dataX", dataX)
    # print("dataY", dataY)
    return np.array(dataX), np.array(dataY)

#
# lstm1 = LSTMModel("982c78b5-435a-40b3-9a31-9fb5fbf8b165")
# lstm1.predict_values()
