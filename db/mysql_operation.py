#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/5 17:25
# @Author  : zsj
# @File    : mysql_operation.py
# @Description: 对数据库的操作，用于存储、查询、更改打标后的数据

import pymysql


def connectdb():
    """
    打开数据库连接
    :return:
    """
    db = pymysql.connect("localhost", "root", "123", "aiops")
    print('已连接数据库')
    return db


def query_table(db, table_name):
    """
    检查数据库中是否存在表table_name
    :param db: 已经连接的数据库
    :param table_name: 要查询的表的名字
    :return:如果表存在则返回True，否则返回False
    """
    cursor = db.cursor()
    sql = "select distinct t.table_name, n.SCHEMA_NAME " \
          "from " \
          "information_schema.TABLES t, information_schema.SCHEMATA n " \
          "where " \
          "t.table_name = '%s' and n.SCHEMA_NAME = 'aiops';" % (table_name)
    res = cursor.execute(sql)
    return res == 1


def create_table(db, np_array_field, table_name):
    """
    创建数据库表，
    :param db:
    :param np_array_field: 表字段名
    :param table_name: 表名
    :return: True或者False，代表是否创建成功
    """
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    length = len(np_array_field)
    # 创建kpi和label的字段名,kpi都是float类型，label是int类型，且从第三列开始，前两列为host_id,timestamp
    kpi_sql = ""
    for i in range(2, length - 1):
        kpi_sql += "`%s` float," % (np_array_field[i])
    kpi_sql += "`label` int"

    # 创建表sql语句，加入一个id自增，因为一分钟内可能有多条数据
    sql = "create table `%s`(`id` int auto_increment primary key, `time` timestamp not null DEFAULT CURRENT_TIMESTAMP," % (
        table_name) + kpi_sql + ");"
    print(sql)
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        return True
    except:
        # 如果失败则回滚
        print('创建数据表失败')
        db.rollback()
        return False


def insert_train_datas(db, table_name, np_array):
    """
    训练时批量插入数据到表中
    :param table_name: 表名
    :param db:
    :param np_array: 要插入的数据集，不包括第一样，因为在实时检测中不会带第一行
    :return:True 或者 False代表插入成功与否
    """
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # 待插入的数据，格式为(time,kpi_1...kpi_n, label),(time,kpi_1...kpi_n, label)...(time,kpi_1...kpi_n, label)
    datas_sql = ""
    for data in np_array[:]:
        datas_sql += "(0, '%s', " % (data[1])
        for i in range(2, len(data) - 1):
            datas_sql += "%f" % (float(data[i])) + ","
        datas_sql += "%d" % (int(data[-1])) + "),"
    datas_sql = datas_sql[:-1]

    # sql 插入语句,确定表名，字段名（有自增字段）,和插入内容
    sql = "INSERT INTO `%s` VALUES %s" % (table_name, datas_sql)
    # print(sql)

    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        return True
    except:
        # 如果失败则回滚
        print('插入数据失败')
        db.rollback()
        return False


def query_datas(db, table_name, label=(0, 1), start_time=0, end_time=0, number=0):
    """
    按条件查询数据库
    :param db:
    :param table_name:表名
    :param label: 标签
    :param start_time: 开始时间
    :param end_time: 结束时间  时间区间限制
    :param number: 查询最后多少条数据
    :return: 返回查询到的数据或者None
    """
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    condition = ""
    if label == 0 or label == 1:
        condition += "and `label` = %d" % label
    if number != 0:
        sql = "SELECT * FROM `%s`where 1=1 %s order by id desc limit %d " % (table_name, condition, number)
    else:
        if start_time != 0 and end_time != 0:
            condition = "and `time` between '%s' and '%s'" % (start_time, end_time)
        elif start_time != 0:
            condition = "and `time` >= '%s'" % start_time
        elif end_time != 0:
            condition = "and `time` <= '%s'" % end_time
        if label == 0 or label == 1:
            condition += "and `label` = %d" % label
        # SQL 查询语句
        sql = "SELECT * FROM `%s` where 1=1 %s" % (table_name, condition)
    print(sql)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        return results
    except:
        print("获取数据失败")
        return None


def update_datas(db, table_name, label, start_time=0, end_time=0):
    """
    更新数据库表数据label
    :param db:
    :param table_name: 表名
    :param start_time: 开始时间
    :param end_time: 截止时间
    :param label: 要更改成的label
    :return: True 或者 False代表数据更新成功与否
    """
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    condition = ""
    if start_time != 0 and end_time != 0:
        condition = "and `time` between '%s' and '%s'" % (start_time, end_time)
    elif start_time != 0:
        condition = "and `time` >= '%s'" % start_time
    elif end_time != 0:
        condition = "and `time` <= '%s'" % end_time

    # SQL 更新语句
    sql = "UPDATE `%s` SET `label` = %d where 1 = 1  %s" % (table_name, label, condition)
    print(sql)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        return True
    except:
        print('更新数据失败')
        # 发生错误时回滚
        db.rollback()
        return False


def drop_table(db, table_name):
    """
    删除某表
    :param db:
    :param table_name:要删除的表名
    :return: True 或者 False代表删除表格成功与否
    """
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # SQL 删除语句
    sql = "drop table `%s`" % (table_name)
    print(sql)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 提交修改
        db.commit()
        return True
    except:
        print('删除数据库表失败!')
        # 发生错误时回滚
        db.rollback()
        return False


def delete_datas(db, table_name, start_time=0, end_time=0):
    """
    按时间区间删除数据
    :param db: 数据库
    :param table_name: 表名
    :param start_time: 开始时间
    :param end_time: 结束时间
    :return:True 或者 False代表删除数据成功与否
    """
    cursor = db.cursor()
    condition = ""
    if start_time != 0 and end_time != 0:
        condition = "and `time` between '%s' and '%s'" % (start_time, end_time)
    elif start_time != 0:
        condition = "and `time` >= '%s'" % start_time
    elif end_time != 0:
        condition = "and `time` <= '%s'" % end_time

    sql = "delete from `%s` where 1=1  %s" % (table_name, condition)
    print(sql)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        return True
    except:
        print('删除数据失败!')
        # 发生错误时回滚
        db.rollback()
        return False


def insert_xgboost_model(file_name, model_name, precision=0., recall=0., f1=0., trained=0, finished=0, changed=0, created_time=0,
                         lasted_update=0):
    """
    插入xgboost训练数据到数据库表中
    :param file_name:文件名，数据来源
    :param db:
    :param model_name: 模型名称
    :param precision: 精确率
    :param recall: 召回率
    :param f1: f1值
    :param trained: 已经训练多少数据
    :param finished: 是否训练完成
    :param changed: 模型数据是否重新更改，如更改则需要重新训练数据
    :param created_time: 创建模型时间
    :param lasted_update: 最后更新模型时间
    :return: true插入成功，false插入失败
    """
    db = connectdb()
    cursor = db.cursor()
    # sql 插入语句,确定表名，字段名（有自增字段）,和插入内容
    sql = "INSERT INTO `model`(`file_name`, `model_name`, `precision`, `recall`, `f1`, `trained`, `finished`, `changed`, `created_time`, `lasted_update`) " \
          "VALUES('%s','%s',%f,%f,%f,%d,%d,%d,'%s','%s')" % (
              file_name, model_name, precision, recall, f1, trained, finished, changed, created_time, lasted_update)
    print(sql)
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        return True
    except:
        # 如果失败则回滚
        print('插入数据失败')
        db.rollback()
        return False


def update_xgboost_model(model_name, precision=0., recall=0., f1=0., trained=0, finished=0, changed=0, lasted_update=0):
    """
    插入xgboost训练数据到数据库表中
    :param db:
    :param model_name: 模型名称
    :param precision: 精确率
    :param recall: 召回率
    :param f1: f1值
    :param trained: 已经训练多少数据
    :param finished: 是否训练完成
    :param changed: 模型数据是否重新更改，如更改则需要重新训练数据
    :param lasted_update: 最后更新模型时间
    :return: true插入成功，false插入失败
    """
    # update 条件
    condition = ""
    if precision != 0:
        condition += "`precision` = %f," % precision
    if recall != 0:
        condition += "`recall` = %f," % recall
    if f1 != 0:
        condition += "`f1` = %f," % f1
    if trained != 0:
        condition += "`trained` = %d," % trained
    if finished != 0:
        condition += "`finished` = %d," % finished
    if changed != 0:
        condition += "`changed` = %d," % changed
    if lasted_update != 0:
        condition += "`lasted_update` = '%s'" % lasted_update
    print(condition)

    db = connectdb()
    cursor = db.cursor()
    # sql 插入语句,确定表名，字段名（有自增字段）,和插入内容
    sql = "UPDATE `model` set %s where `model_name` = '%s'" % (condition, model_name)
    print(sql)
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        return True
    except:
        # 如果失败则回滚
        print('更新xgboost数据失败')
        db.rollback()
        return False


def insert_lstm_model(file_name, model_name, rmse=0., lasted_predict=0, predict_value=0., created_time=0, lasted_update=0):
    """
    插入lstm训练数据到数据库表中
    :param model_name: 模型名称
    :param rmse: 模型的均方根误差，用来衡量模型预测的效果
    :param lasted_predict: 最后预测时间
    :param predict_value: 预测的值，字符串的形式存储
    :param created_time: 创建模型时间
    :param lasted_update: 最后更新模型时间
    :return: true插入成功，false插入失败
    """
    db = connectdb()
    cursor = db.cursor()
    # sql 插入语句,确定表名，字段名（有自增字段）,和插入内容
    sql = "INSERT INTO `lstm_model`(`file_name`, `model_name`, `rmse`, `lasted_predict`, `predict_value`, `created_time`, `lasted_update`) " \
          "VALUES('%s','%s',%f,'%s','%s','%s','%s')" % \
          (file_name, model_name, rmse, lasted_predict, predict_value, created_time, lasted_update)
    print(sql)
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        return True
    except:
        # 如果失败则回滚
        print('插入数据失败')
        db.rollback()
        return False


def update_lstm_model(model_name, rmse=0., lasted_predict=0, predict_value=0, lasted_update=0):
    """
    更新lstm模型后更新数据库表信息
    :param model_name:
    :param rmse:
    :param lasted_predict:
    :param predict_value:
    :param lasted_update:
    :return:
    """
    # update 条件
    condition = ""
    if rmse != 0:
        condition += "`rmse` = %f," % rmse
    if lasted_predict != 0:
        condition += "`lasted_predict` = '%s'," % lasted_predict
    if predict_value != 0:
        condition += "`predict_value` = '%s'," % predict_value
    if lasted_update != 0:
        condition += "`lasted_update` = '%s'" % lasted_update
    print(condition)

    db = connectdb()
    cursor = db.cursor()
    # sql 插入语句,确定表名，字段名（有自增字段）,和插入内容
    sql = "UPDATE `lstm_model` set %s where `model_name` = '%s'" % (condition, model_name)
    print(sql)
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        return True
    except:
        # 如果失败则回滚
        print('更新lstm数据失败')
        db.rollback()
        return False


def query_lstm_predict_30(table_name):
    """
    预测表名为table_name的监控指标未来30个时间点的值
    :param table_name: 使用哪个模型
    :return:
    """
    db = connectdb()
    cursor = db.cursor()
    sql = "select `lasted_predict`,`predict_value` from `lstm_model` where `model_name`='%s'" % table_name
    print(sql)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        return results
    except:
        # 如果失败则回滚
        print('更新lstm数据失败')
        db.rollback()
        return False


def query_model_info(kind):
    """
    根据类型查询模型信息
    :param kind:
    :return:
    """
    db = connectdb()
    cursor = db.cursor()
    if kind == 'XGBoost':
        sql = "select * from `model`"
    elif kind == "LSTM":
        sql = "select * from `lstm_model`"
    print(sql)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        return results
    except:
        # 如果失败则回滚
        print('更新lstm数据失败')
        db.rollback()
        return False


def query_abnormal_list(start_time = '', end_time = ''):
    """
    根据时间区间查询异常信息列表
    :param start_time: 开始时间
    :param end_time: 结束时间
    :return: 查询列表
    """
    db = connectdb()
    cursor = db.cursor()
    condition = ""
    if start_time != '' and end_time != '':
        condition = "and `time` between '%s' and '%s'" % (start_time, end_time)
    elif start_time != '':
        condition = "and `time` >= '%s'" % start_time
    elif end_time != '':
        condition = "and `time` <= '%s'" % end_time
    sql = "select * from `abnormal_list` where 1=1 %s"%condition
    print(sql)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        return results
    except:
        # 如果失败则回滚
        print('查询异常列表失败')
        db.rollback()
        return False


def insert_abnormal_list(model_name, time, value):
    """
    将异常信息插入abnormal_list表中
    :param model_name: uuid,将其转为file_name 后存储
    :param time: 时间戳
    :param value: kpi值
    :return: bool
    """
    db = connectdb()
    cursor = db.cursor()
    # sql 插入语句,确定表名，字段名（有自增字段）,和插入内容
    file_name = query_filename_from_file2uuid_by_uuid(model_name)
    sql = "INSERT INTO `abnormal_list`(`model_name`, `time`, `value`) VALUES('%s','%s',%f)" % (file_name, time, value)
    print(sql)
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        return True
    except:
        # 如果失败则回滚
        print('插入异常数据失败')
        db.rollback()
        return False


def insert_file2uuid(file_name, uuid):
    """
    将file_name和uuid对应关系插入file2uuid表中
    :param file_name:
    :param uuid:
    :return: bool
    """
    db = connectdb()
    cursor = db.cursor()
    sql = "insert into `file2uuid` values ('%s','%s')" % (file_name, uuid)
    print(sql)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        db.commit()
        return True
    except:
        # 如果失败则回滚
        print('插入file2uuid失败')
        db.rollback()
        return False


def query_uuid_from_file2uuid_by_filename(file_name):
    """
    在file2uuid表中通过file_name查询对应的uuid
    :param file_name:
    :return: uuid str
    """
    db = connectdb()
    cursor = db.cursor()
    sql = "select `uuid` from `file2uuid` where file_name='%s'" % file_name
    print(sql)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表,返回是二维数组，每个一维数组是一个结果，每个结果中有多条属性，第一个属性是uuid
        results = cursor.fetchall()
        return results[0][0]
    except:
        # 如果失败则回滚
        print('获取文件uuid失败')
        db.rollback()
        return False


def query_filename_from_file2uuid_by_uuid(uuid):
    """
    在file2uuid表中通过uuid查询对应的file_name
    :param uuid:
    :return: file_name str
    """
    db = connectdb()
    cursor = db.cursor()
    sql = "select `file_name` from `file2uuid` where uuid='%s'" % uuid
    print(sql)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        return results[0][0]
    except:
        # 如果失败则回滚
        print('获取文件uuid失败')
        db.rollback()
        return False

def closedb(db):
    """
    关闭数据库连接
    :param db:
    :return:
    """
    db.close()

