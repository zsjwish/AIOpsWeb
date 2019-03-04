#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/3/4 19:02
# @Author  : zsj
# @File    : model_persistence.py
# @Description:
import os
import pickle

from AIOps_pro.static_value import sv


def save_xgboost_class(model):
    """
    xgboost 模型持久化，存储在models目录下，使用model.name作为文件名,同时持久化模型名称
    :param model:
    :return:
    """
    # 存储模型
    print("sava_xgboost_path", os.getcwd())
    file_name = "./models_file/xgboost/%s" % model.name
    with open(file_name, 'wb') as file_obj:
        pickle.dump(model, file_obj)
    # 存储名称
    file_model_name = "./models_file/xgboost_name"
    with open(file_model_name, 'a+') as name_obj:
        name_obj.write(model.name + "\n")


def load_xgboost_class(model_name):
    """
    根据模型名称加载模型，返回model
    :param model_name:模型名
    :return: 返回模型
    """
    file_name = "./models_file/xgboost/%s" % model_name
    # return pickle.load(open(file_name, "rb"))
    print(os.getcwd())
    print(file_name)
    with open(file_name, 'rb') as f:
        xgboost_class = pickle.load(f)
        return xgboost_class


def save_lstm_class(LSTM_model):
    """
    lstm 模型持久化，存储在models目录下，使用model.name作为文件名,同时持久化模型名称
    :param model:
    :return:
    """
    # 存储模型
    file_name = "./models_file/lstm/%s" % LSTM_model.name
    print("save lstm path", file_name)
    with open(file_name, 'wb') as file_obj:
        pickle.dump(LSTM_model, file_obj)
    # 存储名称
    file_model_name = "./models_file/lstm_name"
    with open(file_model_name, 'a+') as name_obj:
        name_obj.write(LSTM_model.name + "\n")


def load_lstm_class(model_name):
    """
    根据模型名称加载模型，返回model
    :param model_name:模型名
    :return: 返回模型
    """
    print(os.getcwd())
    file_name = "./models_file/lstm/%s" % model_name
    print(file_name)
    with open(file_name, 'rb') as f:
        lstm_class = pickle.load(f)
        return lstm_class


def load_datas_from_disk_to_memory():
    load_dataset_name_to_list()
    load_xgboost_name_to_list()
    load_lstm_name_to_list()
    # load_xgboost_name_to_dict()
    # load_lstm_name_to_dict()


def save_dataset_name_to_file(file_name):
    """
    将文件名存储到磁盘中，断电重启时能够保证继续运行
    :param file_name: 文件名称
    :return:
    """
    print(os.getcwd())
    file_path = "./models_file/data_set_name"
    with open(file_path, 'a+') as file:
        file.write(file_name + "\n")


def load_dataset_name_to_list():
    """
    加载磁盘文件中数据集名到内存中，data_set
    :return:
    """
    file_path = "./models_file/data_set_name"
    with open(file_path, 'r') as file:
        lines = file.read().splitlines()
        for line in lines:
            if line is None or line == "":
                continue
            elif line not in sv.data_set:
                sv.data_set.append(line)
    print(sv.data_set)


def load_xgboost_name_to_list():
    """
    加载磁盘文件中XGBoost模型名到内存中，xgboost_name
    :return:
    """
    file_path = "./models_file/xgboost_name"
    with open(file_path, 'r') as file:
        lines = file.read().splitlines()
        for line in lines:
            if line is None or line == "":
                continue
            elif line not in sv.xgboost_name:
                sv.xgboost_name.append(line)
    print(sv.xgboost_name)


def load_lstm_name_to_list():
    """
    加载磁盘文件中LSTM模型名到内存中，lstm_name
    :return:
    """
    file_path = "./models_file/lstm_name"
    with open(file_path, 'r') as file:
        lines = file.read().splitlines()
        for line in lines:
            if line is None or line == "":
                continue
            elif line not in sv.lstm_name:
                sv.lstm_name.append(line)
    print(sv.lstm_name)


def load_lstm_name_to_dict():
    """
    加载磁盘文件中LSTM模型到内存中，lstm_name
    :return:
    """
    file_path = "./models_file/lstm_name"
    with open(file_path, 'r') as file:
        lines = file.read().splitlines()
        for line in lines:
            if line is None or line == "":
                continue
            elif line not in sv.lstm_model_dict.keys():
                sv.lstm_model_dict[line] = load_lstm_class(line)
    print("lstm---------------------", sv.lstm_model_dict)


def load_xgboost_name_to_dict():
    """
    加载磁盘文件中LSTM模型到内存中，lstm_name
    :return:
    """
    file_path = "./models_file/xgboost_name"
    with open(file_path, 'r') as file:
        lines = file.read().splitlines()
        for line in lines:
            if line is None or line == "":
                continue
            elif line not in sv.xgboost_model_dict.keys():
                sv.xgboost_model_dict[line] = load_xgboost_class(line)
    print("xgboost-------------------", sv.xgboost_model_dict)
