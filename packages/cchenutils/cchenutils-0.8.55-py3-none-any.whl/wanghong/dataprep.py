# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/21/20
# @File  : [wanghong] table.py


import os
from os.path import join as pjoin

from table import *

if __name__ == '__main__':
    data_dir = os.getcwd().replace('Dropbox/projects', 'data')

    taobao_shops(pjoin(data_dir, '_taobao_shops.csv'), pjoin(data_dir, 'taobao_shops.csv'))
    taobao_items(pjoin(data_dir, '_taobao_items.csv'), pjoin(data_dir, 'taobao_items.csv'))
    taobao_rates(pjoin(data_dir, '_taobao_rates.csv'), pjoin(data_dir, 'taobao_rates.csv'))

    yizhibo_video(pjoin(data_dir, '_yizhibo_video.csv'), pjoin(data_dir, 'yizhibo_video.csv'))
    yizhibo_first(pjoin(data_dir, 'yizhibo_video.csv'), pjoin(data_dir, 'yizhibo_first.csv'))
    yizhibo_damnu(pjoin(data_dir, '_yizhibo_danmu.csv'), pjoin(data_dir, 'yizhibo_danmu.csv'))

    weibo_user(pjoin(data_dir, '_weibo_users.csv'), pjoin(data_dir, 'weibo_users.csv'))

    id_map(pjoin(data_dir, 'taobao_shops.csv'),pjoin(data_dir, 'weibo_users.csv'), pjoin(data_dir, 'uids.csv'))

    taobao_rates_(pjoin(data_dir, 'taobao_rates.csv'), pjoin(data_dir, 'taobao_rates_.csv'),
                  fp_uids=pjoin(data_dir, 'uids.csv'),
                  fp_tbids=pjoin(data_dir, 'taobao_items.csv'),
                  fp_first=pjoin(data_dir, 'yizhibo_first.csv'))
