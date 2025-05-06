# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/11/20
# @File  : [wanghong] opts.py


import os
from datetime import datetime

from wanghong.utils import call

DATA_DIR = os.getcwd().replace('Dropbox/projects', 'data')
START_DATE = datetime.strptime('2017-10-01', '%Y-%m-%d')
FREQUENCY = 7

LEVEL = 'Taobao_IID'


def calc_time(t):
    return (t - START_DATE).days // FREQUENCY



if __name__ == '__main__':
    call('python taobao_items.py')
    call('python taobao_shops.py')
    call('python taobao_rates.py')
    call('python yizhibo_video.py')
    call('python yizhibo_first.py')
    call('python yizhibo_danmu.py')
    call('python weibo_users.py')

    call('python id_map.py')

    call('python taobao_rates_.py')
