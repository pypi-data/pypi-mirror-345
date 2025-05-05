# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/12/20
# @File  : [wanghong] id_map.py


import pandas as pd

from utils import DATA_DIR


def main():
    print(__name__)

    df_TS_WU = pd.read_csv(f'{DATA_DIR}/taobao_shops.csv', usecols=['Taobao_SID', 'Weibo_UID'])
    df_WU_YU = pd.read_csv(f'{DATA_DIR}/weibo_users.csv', usecols=['Weibo_UID', 'Yizhibo_UID'])
    wb_uid_counts = df_TS_WU['Weibo_UID'].value_counts()
    uids = wb_uid_counts[wb_uid_counts == 1].index
    df_out = df_TS_WU.loc[df_TS_WU['Weibo_UID'].isin(uids)].merge(df_WU_YU, on='Weibo_UID', how='inner')
    df_out.to_csv(f'{DATA_DIR}/uids.csv', index=False)


if __name__ == '__main__':
    main()
