# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : chench@uwm.edu
# @Time  : 3/6/21
# @File  : [wanghong] weibo_miaopai.py

import re

import numpy as np
import pandas as pd

from taobao_items_ import clothing_keywords
from utils import DATA_DIR


def main():
    print(__name__)

    data = pd.read_csv(f'{DATA_DIR}/weibo_timeline.csv', dtype=str)
    data = data[data['text'].apply(lambda x: '秒拍' in x if isinstance(x, str) else False)] \
        .dropna(subset=['media.urls', 'urls'])
    data['media_play_url'] = data.pop('media.urls').apply(lambda x: '|'.join(eval(x)) if x != '[null]' else '')
    data['media_play_title'] = \
        data.apply(lambda x: tu[0] if (tu := [t for t, u in eval(x['urls']) if u == x['media_play_url']]) else np.nan,
                   axis=1)
    data = data.drop(columns=['urls']) \
        .dropna(subset=['media_play_title']) \
        .rename(columns={'mid62': 'Weibo_MID62', 'media.play_count': 'media_play_count'})

    # df_items_clothes = pd.read_csv('../analysis/df_items_clothes.csv')
    df_uids = pd.read_csv(f'{DATA_DIR}/uids.csv')
    # df_uids = df_uids[df_uids['Taobao_SID'].isin(df_items_clothes['Taobao_SID'])]
    data = data[data['Weibo_UID'].isin(df_uids['Weibo_UID'])]

    data['nick_'] = data['nick'].fillna('dsahdk@_@jsahnd')
    data['media_play_count'] = data['media_play_count'].fillna('0') \
        .apply(lambda x: x[:-1] + '0000' if x.endswith('万') else x).astype(int)
    data = data[data.apply(lambda x: not ('分享' in x['text'] and x['nick_'] not in x['text']), axis=1)] \
        .drop(columns=['nick_'])
    data = data[data['text'].apply(lambda x: re.search('|'.join(clothing_keywords.keys()), x) is not None)]
    data.to_csv(f'{DATA_DIR}/weibo_miaopai.csv', index=False)


if __name__ == '__main__':
    main()
