#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/3/4 18:54
# @Author  : zsj
# @File    : d.py
# @Description:
import os
import pickle

from django_redis import get_redis_connection

from db.a import Datas

os.environ.update({"DJANGO_SETTINGS_MODULE": "AIOps_pro.settings"})
redis_conn = get_redis_connection("default")
redis_conn.srem("data_set_name", "123123123123123123123123")
redis_conn.srem("data_set_name", "525205205250520520520520")
list = redis_conn.smembers("data_set_name")
data1 = Datas("hello")
print(data1.name)
print(data1.time)
data1_byte = pickle.dumps(data1)
key = data1.name + data1.time
redis_conn.hset('data', key, data1_byte)
value = pickle.loads(redis_conn.hget('data', key))
print(value.name)
print(value.time)
print(redis_conn.hexists('data', key))
connection_pool = redis_conn.connection_pool
print("pool", redis_conn.connection_pool)
print("Created connections so far: %d" % connection_pool._created_connections)
redis_conn.sadd("data_set_name", "123123123123123123123123")
print("Created connections so far: %d" % connection_pool._created_connections)
redis_conn.sadd("data_set_name", "1231231231231231231231231")
print("Created connections so far: %d" % connection_pool._created_connections)
redis_conn.sadd("data_set_name", "1231231231231231231231232")
print("Created connections so far: %d" % connection_pool._created_connections)
redis_conn.sadd("data_set_name", "1231231231231231231231233")
print("Created connections so far: %d" % connection_pool._created_connections)
redis_conn.sadd("data_set_name", "1231231231231231231231234")
print("Created connections so far: %d" % connection_pool._created_connections)

redis_conn = get_redis_connection("default")
print(redis_conn.hexists('testlstm', '1'))

redis_conn.hset("testlstm", '1', 1)
print(redis_conn.hexists('testlstm', '1'))