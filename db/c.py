#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/3/4 18:51
# @Author  : zsj
# @File    : c.py
# @Description:
from AIOps_pro.static_value import sv


class C:
    def __init__(self):
        print("C init")
        self.name = "c"
        self.age = 21
        self.label = 1
        print(sv.lstm_name)

def init():
    c = C()
