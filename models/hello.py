#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/24 18:05
# @Author  : zsj
# @File    : hello.py
# @Description:


class Hello:
    def __init__(self):
        self.name = "zsj"
        self.age = 18

    def get_name(self):
        return self.name

    def get_str(self, string):
        return self.name + str(self.age) + string

