#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/12/14 15:11
# @Author  : zsj
# @File    : base_function.py
# @Description: 用于提供孤立森林的各种边缘功能
import h5py
import os
import pickle
import re
import time
from datetime import datetime

import keras
import numpy as np
import matplotlib.pyplot as plt

from AIOps_pro.static_value import StaticValue
from db.mysql_operation import connectdb, query_datas, closedb, query_table, create_table, insert_train_datas, \
    update_datas, query_lstm_predict_30, query_model_info
from isolate_model.isolate_class import Isolate

sv = StaticValue()
def load_csv(file_name):
    """
    使用numpy加载csv文件,并把除了host_id的都转换成float类型，因为孤立森林只能判别数值类型
    csv文件的格式是： host_id(主机群和主机标识), timestamp, kpi_1, kpi_2, kpi_3, kpi_4.....
    :param file_name: 要解析的csv文件名
    :return:
    """
    array = np.loadtxt(file_name, dtype = str, delimiter = ",", encoding = 'utf-8')
    print(type(array))
    return array


def show_csv(array, array_x, array_y):
    """
    将读取的csv文件中某两列取出来作为图形展示的x轴和y轴
    :param array:转置后的数组
    :param array_x:数组第x列,一般来说x轴是时间
    :param array_y:同上
    :return:
    """
    # 从第三个值开始取，因为第一个是host_id,第二个是时间戳
    x_value = array[1:, array_x]
    y_value = array[1:, array_y]
    # 获取label标签，知道是那两行作图
    label_x = array[0, array_x]
    label_y = array[0, array_y]
    if "timestamp" in label_x:
        # 一般来说x轴都是时间戳
        # x_value = [format_time(x) for x in x_value]
        x_value = [x for x in x_value]
    else:
        x_value = [float(x) for x in x_value]
    y_value = [float(y) for y in y_value]
    plt.plot(x_value, y_value, c = 'r', ls = '--', marker = 'o', lw = 1.5, label = label_x)
    plt.xticks(range(0, len(x_value), int(len(x_value) / 30)), rotation = 90)
    # plt.figure(dpi=128, figsize=(10, 6))
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.show()


def timestamp_to_time(timestamp):
    """
    单个时间戳转换成时间，格式为2018-12-14 19:00:00
    :param timestamp:
    :return:
    """
    timestamp = int(timestamp)
    time_local = time.localtime(timestamp)
    return time.strftime("%Y-%m-%d: %H:%M:%S", time_local)


def simplify_timestamp(timestamps):
    """
    时间戳批量转换成时间
    :param timestamps: 时间戳list
    :return:
    """
    return [timestamp_to_time(timestamp) for timestamp in timestamps]


def get_uniform_cases(arrays, size=257):
    """
    由于传入的测试集不可能刚好是256个，所以需要均匀取周期内的256个case作为测试集
    仅仅用于训练模型时使用
    :param arrays:测试集数组
    :param size:int, 要求均匀分为的份额，一般为256，用户可以自己设置,第一行为标签
    :return:
    """
    length = len(arrays)
    if length < 200:
        print("测试集大小：", length)
        return "测试集数据小于200，请重新传入大于200条数据的测试集"
    elif length < 256:
        print("测试集大小：", length)
        return arrays
    indexs = np.linspace(0, length - 1, size)
    indexs = np.array(indexs, dtype = int)
    res_arr = arrays[indexs]
    print("测试集大小：", len(indexs) - 1)
    return res_arr


def format_time(time):
    """
    将传入的时间格式化，转换成没有秒的时间格式 yyyy-MM-DD hh-mm
    :param time:
    :return:
    """
    # year, month, day, hour, minute, scend = re.split(r"/| |:", time)
    # print(year, month, day, hour, minute, scend)
    return time[0:-3]


def draw_with_diff_color(np_array):
    """
    根据标签展示散点图，不同的标签具有不同颜色
    :param np_array:
    :return:
    """
    red_arr = []
    green_arr = []
    for arr in np_array:
        if arr[-1] == '0':
            red_arr.append(arr)
        else:
            green_arr.append(arr)
    print(red_arr)
    print(green_arr)


def save_datas_with_labels(file_name, abnormal_rate):
    """
    存储已经由孤立森林学习过的带有标签的数据
    :return:True or False
    """
    cases = load_csv(file_name)
    print("file name", file_name)
    title = file_name.split("/")[-1]
    print(type(title), title)
    isolate1 = Isolate('isolate', cases, rate = abnormal_rate)
    np_array = isolate1.merge_arrays()
    table_name = np_array[1, 0]
    db = connectdb()
    if not query_table(db, table_name):
        create_table(db, np_array[0], table_name)
    if insert_train_datas(db, table_name, np_array[1:]):
        # 数据集列表存储表名（内存存储），断电就清空
        sv.data_set.append(title)
        # 存储数据集表名（磁盘存储），断电可恢复
        save_dataset_name_to_file(title)
        return True
    return False


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
    print("sv1", sv.data_set)


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
    print("sv2", sv.xgboost_name)


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
    print("sv3", sv.lstm_name)


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


def load_datas_from_disk_to_memory():
    load_dataset_name_to_list()
    load_xgboost_name_to_list()
    load_lstm_name_to_list()
    # load_xgboost_name_to_dict()
    # load_lstm_name_to_dict()


def str_to_time_hour_minute(time):
    week = datetime.strptime(re.split(r" ", time)[0], "%Y/%m/%d").weekday()
    year, month, day, hour, minute, secend = re.split(r"[/ :]", time)
    return [hour, minute, week]


def use_XGBoost_predict(json_data):
    """
    使用已训练的XGBoost模型检测异常
    :param json_data:
    :return:
    """
    model_name = json_data["host_id"]
    times = datetime.strptime(json_data["time"], '%Y-%m-%d %H:%M:%S')
    print(times.hour)
    print(type(times))
    predict_list = [model_name, datetime.strptime(json_data["time"], '%Y-%m-%d %H:%M:%S'), json_data["kpi"]]
    print(predict_list)
    predict_array = np.array(predict_list)
    # 转换成XGBoost能使用的数据格式
    tmp = translate_to_xgboost_datas_from_mysql(predict_array.reshape(1, 3))
    # 由于频次较低，每次从磁盘文件中读取模型然后判断
    XGBoost_model = load_xgboost_class(model_name)
    print("load xgboost0000000000000000000000")
    print("model name", XGBoost_model.name)
    return XGBoost_model.predict(tmp)


def translate_to_xgboost_datas_from_realtime():
    pass


def translate_to_xgboost_datas_from_mysql(np_array):
    """
    将数据转换成xgboost能够识别的数据，仅仅在时间格式上转换，其他列不变
    :param np_array:输入的数组
    :return:时间转换后的数组，仅仅在时间上做出改变，其他列不变
    """
    # 删除id列
    np_array = np.delete(np_array, 0, axis = 1)
    # 获取时间列
    time_array = np_array[:, 0]
    # 删除时间列
    np_array = np.delete(np_array, 0, axis = 1)
    hour = []
    minute = []
    week = []
    for time in time_array:
        hour.append(time.hour)
        minute.append(time.minute)
        week.append(time.weekday())
    np_array = np.insert(np_array, 0, values = minute, axis = 1)
    np_array = np.insert(np_array, 0, values = hour, axis = 1)
    np_array = np.insert(np_array, 0, values = week, axis = 1)
    # 此时返回的属性分别是 week, hour, minute, kpi_1... kpi_n,label
    return np_array


def load_data_for_xgboost_from_mysql(table_name, number_data=20000):
    """
    从数据库为xgboost模型读取数据，并进行时间格式转换
    :param number_data: 取最后多少个数据来训练或者预测
    :param table_name: 要读取的表名
    :return:
    """
    db = connectdb()
    np_array = np.array(query_datas(db, table_name = table_name, number = number_data))
    # # 删除id列
    # np_array = np.delete(np_array, 0, axis = 1)
    # # 获取时间列
    # time_array = np_array[:, 0]
    # # 删除时间列
    # np_array = np.delete(np_array, 0, axis = 1)
    # hour = []
    # minute = []
    # week = []
    # for time in time_array:
    #     hour.append(time.hour)
    #     minute.append(time.minute)
    #     week.append(time.weekday())
    # np_array = np.insert(np_array, 0, values = minute, axis = 1)
    # np_array = np.insert(np_array, 0, values = hour, axis = 1)
    # np_array = np.insert(np_array, 0, values = week, axis = 1)
    np_array = translate_to_xgboost_datas_from_mysql(np_array)
    closedb(db)
    # 此时返回的属性分别是 week, hour, minute, kpi_1... kpi_n,label
    return np_array


def load_data_for_lstm_from_mysql(table_name, number_data=20000):
    """
    从数据库为lstm模型读取一天的数据
    :param number_data: 取最后多少个数据来训练或者预测
    :param table_name: 表名
    :param end_time: 最后截止时间，即什么时刻开始预测
    :return:
    """
    db = connectdb()
    np_array = np.array(query_datas(db, table_name = table_name, number = number_data))
    closedb(db)
    return np_array[:, -2]


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


def print_model(model_kind, data_name):
    print("print_modelllllllllllllllllll", model_kind, data_name)


from xgboost_model.xgboost_class import XGBoost
from lstm_model.lstm_class import LSTMModel


def train_model(model_kind, data_name):
    """训练模型"""
    print("类型", type(data_name))
    print(data_name)
    if model_kind == "XGBoost":
        if data_name in sv.xgboost_name:
            return 0
        else:
            XGBoost(data_name)
            return 1

    elif model_kind == 'LSTM':
        if data_name in sv.lstm_name:
            return 0
        else:
            print(data_name)
            print("类型", type(data_name))
            tmp = LSTMModel(data_name)
            # tmp.train()
            return 1


def get_datas_for_tag(table_name, start_time=0, end_time=0, label=(0, 1)):
    """
    按条件查询数据库表信息
    :param table_name:
    :param start_time:
    :param end_time:
    :param label:
    :return:
    """
    result = query_datas(connectdb(), table_name = table_name, label = label, start_time = start_time,
                         end_time = end_time)
    print(type(result))
    print(result)
    return result


def update_datas_for_tag(table_name, label, start_time=0, end_time=0):
    """

    :param table_name:
    :param start_time:
    :param end_time:
    :param label:
    :return:
    """
    if update_datas(connectdb(), table_name = table_name, label = label, start_time = start_time, end_time = end_time):
        return get_datas_for_tag(table_name = table_name, start_time = start_time, end_time = end_time, label = label)


def predict_future_30(table_name):
    # keras.backend.clear_session()
    lstm_model_tmp = load_lstm_class(table_name)
    res = lstm_model_tmp.predict_values()
    print(type(res))
    print(res)
    predict_xAxis = list(range(1, len(res) + 1))
    return predict_xAxis, res


def get_model_info(kind):
    res = query_model_info(kind)
    print(res)
    print(len(res))
    print(type(res))
