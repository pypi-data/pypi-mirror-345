# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/12/20
# @File  : [wanghong] weibo_users.py


import pandas as pd

from utils import DATA_DIR


def main():
    print(__name__)

    df = pd.read_csv(f'{DATA_DIR}/_weibo_users.csv', dtype={'_id': str, 'yizhibo_id': str}) \
        .rename(columns={'_id': 'Weibo_UID', 'yizhibo_id': 'Yizhibo_UID'})
    df['Weibo_UID'] = 'WU' + df['Weibo_UID']
    df['Yizhibo_UID'] = 'YU' + df['Yizhibo_UID']
    df.to_csv(f'{DATA_DIR}/weibo_users.csv', index=False)


if __name__ == '__main__':
    main()
