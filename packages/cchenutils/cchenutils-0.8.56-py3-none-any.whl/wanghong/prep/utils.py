# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : chench@uwm.edu
# @Time  : 3/22/21
# @File  : [prep] utils.py

from datetime import datetime


# DATA_DIR = '/home/cchen/data/wanghong'
DATA_DIR = '../data'
MIN_PRICE = 1.
START_DATE = datetime.strptime('2017-10-01', '%Y-%m-%d')
FREQUENCY = 7
MAX_TIME = 31

LEVEL = 'Taobao_IID'


def calc_time(t):
    return (t - START_DATE).days // FREQUENCY


def print_func_name(func):
    def inner(*args, **kwargs):
        print(func.__name__)
        func(*args, **kwargs)
    return inner
