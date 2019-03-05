#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/3/4 18:51
# @Author  : zsj
# @File    : a.py
# @Description:
import time


class Datas:
    def __init__(self, name):
        print('init data')
        self.name = name
        self.data = name + "'s datas"
        self.time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def get_name(self):
        return self.name

    def get_data(self):
        return self.data

