# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/12/20
# @File  : [wanghong] yizhibo_danmu.py


import pandas as pd

from utils import DATA_DIR


def main():
    print(__name__)

    df_danmu = pd.read_csv(f'{DATA_DIR}/_yizhibo_danmu.csv', dtype={'_id': str, 'memberid': str}) \
        .rename(columns={'_id': 'Yizhibo_DID', 'memberid': 'Yizhibo_UID', 'replayid': 'Yizhibo_VID'})
    df_danmu['Yizhibo_DID'] = 'YD' + df_danmu['Yizhibo_DID']
    df_danmu['Yizhibo_UID'] = 'YU' + df_danmu['Yizhibo_UID']
    df_danmu['Yizhibo_VID'] = 'YV' + df_danmu['Yizhibo_VID']
    df_danmu.to_csv(f'{DATA_DIR}/yizhibo_danmu.csv', index=False)


if __name__ == '__main__':
    main()
