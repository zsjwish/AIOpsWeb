#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/3/4 18:54
# @Author  : zsj
# @File    : d.py
# @Description:
from AIOps_pro.static_value import StaticValue
from db.b import print_b
from db.a import print_a

from db.c import init

def test():
    init()
    print_a()
    print_b()

test()

sv1 = StaticValue()
sv2 = StaticValue()
print(sv1 == sv2)