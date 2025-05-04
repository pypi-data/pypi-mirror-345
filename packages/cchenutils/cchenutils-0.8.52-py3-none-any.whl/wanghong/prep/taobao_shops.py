# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/11/20
# @File  : [wanghong] taobao_shops.py

"""
1. Add prefix to IDs
2. FillNA for ifashion, seller_rate.overall, seller_rate.main
"""

import pandas as pd

from utils import DATA_DIR


def main():
    print(__name__)

    df_shops = pd.read_csv(f'{DATA_DIR}/_taobao_shops.csv', dtype={'_id': str, 'weibo_id': str}) \
        .rename(columns={'_id': 'Taobao_SID', 'weibo_id': 'Weibo_UID'}) \
        .dropna(subset=['category_manual'])
    df_shops['Taobao_SID'] = 'TS' + df_shops['Taobao_SID']
    df_shops['Weibo_UID'] = 'WU' + df_shops['Weibo_UID']
    df_shops['ifashion'] = df_shops['ifashion'].fillna(0).astype(int)

    # FROM = '2018-01-01'
    # df_shops['age'] = df_shops['since'].fillna(FROM).apply(
    #     lambda x: datetime.strptime(FROM, '%Y-%m-%d').year - datetime.strptime(x, '%Y-%m-%d').year)

    df_shops['seller_rate.overall'] = df_shops['seller_rate.overall'].fillna(0)
    df_shops['seller_rate.main'] = df_shops['seller_rate.main'].fillna(0)

    df_shops.to_csv(f'{DATA_DIR}/taobao_shops.csv', index=False)


if __name__ == '__main__':
    main()
