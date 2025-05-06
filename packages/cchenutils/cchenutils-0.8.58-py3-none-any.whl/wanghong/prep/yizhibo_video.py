# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/11/20
# @File  : [wanghong] yizhibo_video.py


import re

import pandas as pd

from utils import DATA_DIR


def main():
    print(__name__)

    df_video = pd.read_csv(f'{DATA_DIR}/_yizhibo_video.csv', dtype={'_id': str, 'uid': str}) \
        .rename(columns={'_id': 'Yizhibo_VID', 'uid': 'Yizhibo_UID'})

    df_video['Yizhibo_VID'] = 'YV' + df_video['Yizhibo_VID']
    df_video['Yizhibo_UID'] = 'YU' + df_video['Yizhibo_UID']
    df_video['title'] = df_video['title'].fillna('').apply(lambda x: re.sub(r'[\n\r]', ' ', x))

    df_video.to_csv(f'{DATA_DIR}/yizhibo_video.csv', index=False)


if __name__ == '__main__':
    main()
