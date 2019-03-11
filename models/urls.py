#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/23 11:05
# @Author  : zsj
# @File    : urls.py
# @Description:
from django.conf.urls import url

from models import views

app_name = 'models'
urlpatterns = [
    url(r'^index/$', views.index, name = 'index'),
    url(r'^upload/$', views.upload, name = 'upload'),
    url(r'^success/$', views.success, name = 'success'),
    url(r'^menu/$', views.menu, name = 'menu'),
    url(r'^train/$', views.train, name = 'train'),
    url(r'^hello/$', views.hello, name = 'hello'),
    url(r'^submit/$', views.submit, name = 'submit'),
    url(r'^tag/$', views.tag, name = 'tag'),
    url(r'^predict/$', views.predict, name = 'predict'),
    url(r'^model_info/$', views.model_info, name = 'model_info'),
    # 主页
    url(r'^dashboard/$', views.dashboard),
    # xgboost_model信息
    url(r'^xgboost_model_info/$', views.xgboost_model_info),
    # lstm_model信息
    url(r'^lstm_model_info/$', views.lstm_model_info),
    url(r'^test/$', views.test),
    # 主base
    url(r'^fixed/$', views.fixed),
    # 数据标注
    url(r'^data_tag/$', views.data_tag),
    # 训练模型
    url(r'^train_model/$', views.train)

]
