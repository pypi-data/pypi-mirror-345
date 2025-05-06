# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 4/14/20
# @File  : [wanghong] yizhibo_firststream.py


import os

import pandas as pd
from wanghong.utils import DATA_DIR

if __name__ == '__main__':
    LEVEL = 'Taobao_IID'

    df_video = pd.read_csv(os.path.join(DATA_DIR, f'yizhibo_video_clothes.csv'))
    df_video_s = df_video.loc[df_video['sell'] == 1]
    df_video_ns = df_video.loc[df_video['sell'] == 0]

    df_video_s.groupby('Taobao_SID').agg({'stream_time': 'min'}) \
        .rename(columns={'stream_time': 'first_stream.s'}).reset_index() \
        .to_csv(os.path.join(DATA_DIR, f'taobao_firsts_clothes.csv'), index=False)
    df_video_ns.groupby('Taobao_SID').agg({'stream_time': 'min'}) \
        .rename(columns={'stream_time': 'first_stream.ns'}).reset_index() \
        .to_csv(os.path.join(DATA_DIR, f'taobao_firstns_clothes.csv'), index=False)



