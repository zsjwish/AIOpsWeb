#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/12/14 15:11
# @Author  : zsj
# @File    : base_function.py
# @Description: 用于提供孤立森林的各种边缘功能
import pickle
import re
import time
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt

from db.mysql_operation import connectdb, query_datas, closedb, query_table, create_table, insert_train_datas
from isolate_model.isolate_class import Isolate
from models.models import xgboost_model_dict, data_set


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


def save_datas_with_labels(file_name):
    """
    存储已经由孤立森林学习过的带有标签的数据
    :return:True or False
    """
    cases = load_csv(file_name)
    isolate1 = Isolate('isolate', cases)
    np_array = isolate1.merge_arrays()
    table_name = np_array[1, 0]
    db = connectdb()
    if not query_table(db, table_name):
        create_table(db, np_array[0], table_name)
    if insert_train_datas(db, table_name, np_array[1:]):
        data_set.append(file_name)
        return True
    return False


def str_to_time_hour_minute(time):
    week = datetime.strptime(re.split(r" ", time)[0], "%Y/%m/%d").weekday()
    year, month, day, hour, minute, secend = re.split(r"[/ :]", time)
    return [hour, minute, week]


def use_XGBoost_predict(model_name, data):
    XGBoost_model = xgboost_model_dict[model_name]
    return XGBoost_model.predict(data)

def translate_to_xgboost_datas(np_array):
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
    np_array = translate_to_xgboost_datas(np_array)
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
    xgboost 模型持久化，存储在models目录下，使用model.name作为文件名
    :param model:
    :return:
    """
    file_name = "../models_file/xgboost/%s" % model.name
    with open(file_name, 'wb') as file_obj:
        pickle.dump(model, file_obj)


def load_xgboost_class(model_name):
    """
    根据模型名称加载模型，返回model
    :param model_name:模型名
    :return: 返回模型
    """
    file_name = "../models_file/xgboost/%s" % model_name
    return pickle.load(open(file_name, "rb"))


def save_lstm_class(model):
    """
    lstm 模型持久化，存储在models目录下，使用model.name作为文件名
    :param model:
    :return:
    """
    file_name = "../models_file/lstm/%s" % model.name
    with open(file_name, 'wb') as file_obj:
        pickle.dump(model, file_obj)


def load_lstm_class(model_name):
    """
    根据模型名称加载模型，返回model
    :param model_name:模型名
    :return: 返回模型
    """
    file_name = "../models_file/lstm/%s" % model_name
    return pickle.load(open(file_name, "rb"))

# str = "2018-11-16 21:38:11"
# end_time = datetime.strptime(str, '%Y-%m-%d %H:%M:%S')
# print(end_time)
# res = load_data_for_lstm_from_mysql("20bc4dbb-f7f8-4521-9187-7dc31cac76e", end_time, 1)
# print(type(res))
# print(res)
