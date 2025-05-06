# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : chench@uwm.edu
# @Time  : 9/16/21
# @File  : [wanghong] _panel_2sellerrate.py

import pandas as pd

from _users import get_lvl
from utils import LEVEL


def main():
    data = pd.read_csv(f'../analysis/df_panel_{"users" if LEVEL.endswith("SID") else "items"}_.csv')
    users = pd.read_csv(f'../analysis/df_users.csv', usecols=['Taobao_SID', 'rate0'])
    data = data.merge(users, on='Taobao_SID', how='inner')

    data = data.drop(columns=['avail_rate']).merge(
        data.groupby(['Taobao_SID', 'time']).agg({'avail_rate': 'sum'}).reset_index()
        , on=['Taobao_SID', 'time'], how='inner')
    data['seller_rate.overall_running'] = data.apply(lambda x: x['rate0'] + x['avail_rate'], axis=1)

    data['seller_rate.overall_running'] = data['seller_rate.overall_running'].apply(lambda x: x if x >=0 else 0)
    data['seller_rate.lvl_running'] = data['seller_rate.overall_running'].apply(get_lvl)
    data.drop(columns=['avail_rate']) \
        .to_csv(f'../analysis/df_panel_{"users" if LEVEL.endswith("SID") else "items"}_sellerrate.csv', index=False)


if __name__ == '__main__':
    main()
