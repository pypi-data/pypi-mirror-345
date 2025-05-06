# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 4/11/20
# @File  : [wanghong] yizhibo_video_category.py



import os

import numpy as np
import pandas as pd
from wanghong.opts import calc_time


def read_category(fp_names, fp_ys):
    name = []
    for fp_name in fp_names:
        with open(fp_name, 'r') as i:
            name += [line.split('\t')[0] for line in i]
    y = []
    for fp_y in fp_ys:
        if fp_y.endswith('.npy'):
            y += [int(line) for line in np.load(fp_y)]
        else:
            with open(fp_y, 'r') as i:
                y += [int(line.strip()) for line in i]
    return dict(zip(name, y))


if __name__ == '__main__':
    from wanghong.utils import DATA_DIR
    category = 'clothes'

    df_uids = pd.read_csv(os.path.join(DATA_DIR, 'uids.csv'), usecols=['Taobao_SID', 'Yizhibo_UID'])
    df_shops = pd.read_csv(os.path.join(DATA_DIR, 'taobao_shops.csv'))
    df_shops = df_shops.loc[df_shops['category_manual'].isin({category})]

    label = read_category(
        [os.path.join(DATA_DIR, 'data_300', 'uvse_train.txt')
            , os.path.join(DATA_DIR, 'data_300', 'uvse_valid.txt')
            , os.path.join(DATA_DIR, 'data_300', 'uvse_test.txt')],
        [os.path.join(DATA_DIR, 'data_300', 'y.npy')
            , os.path.join(DATA_DIR, 'data_300', 'y_pred.txt')])
    df_vcate = pd.DataFrame([(*k.split('/', 1), v) for k, v in label.items()]
                            , columns=['Yizhibo_UID', 'Yizhibo_VID', 'sell'])
    df_vcate['Yizhibo_UID'] = 'YU' + df_vcate['Yizhibo_UID']
    df_vcate['Yizhibo_VID'] = 'YV' + df_vcate['Yizhibo_VID']
    df_vcate = df_uids.merge(df_vcate, on='Yizhibo_UID', how='inner').drop(columns=['Yizhibo_UID'])

    df_video = pd.read_csv(os.path.join(DATA_DIR, 'yizhibo_video.csv'), parse_dates=['date'])

    df_video = df_video.loc[df_video['Yizhibo_UID'].isin(df_uids.merge(df_shops, on='Taobao_SID', how='inner')['Yizhibo_UID'])]
    df_video['stream_time'] = df_video['date'].apply(calc_time)
    df_video = df_video.loc[df_video['stream_time'] >= 0]
    df_uids.merge(df_video, on='Yizhibo_UID', how='inner') \
        .merge(df_vcate, on=['Taobao_SID', 'Yizhibo_VID'], how='left') \
        .drop(columns=['Yizhibo_UID', 'date', 'title', 'starttime']) \
        .to_csv(os.path.join(DATA_DIR, f'yizhibo_video.csv'), index=False)

    df_video['video_category'] = df_video.apply(
        lambda x: label.get(os.path.join(x['Yizhibo_UID'][2:], x['Yizhibo_VID'][2:])), axis=1)
    df_video['sell'] = df_video['video_category'].apply(lambda x: 1 if x == 1 else 0)
    df_video['nonsell'] = df_video['video_category'].apply(lambda x: 1 if x == 0 else 0)

    df_agg = df_video.groupby(['Yizhibo_UID', 'stream_time']).agg({'play.length': 'sum',
                                                                   'n_likes': 'sum',
                                                                   'n_messages': 'sum',
                                                                   'sell': 'sum',
                                                                   'nonsell': 'sum'}).reset_index() \
        .groupby('Yizhibo_UID').apply(lambda x: x.sort_values(by=['stream_time'])).reset_index(drop=True)

    df_cumsum = df_agg[['Yizhibo_UID', 'sell', 'nonsell']] \
        .groupby(['Yizhibo_UID']).cumsum() \
        .rename(columns={'sell': 'sell.cumsum', 'nonsell': 'nonsell.cumsum'})
    df_agg = pd.concat([df_agg, df_cumsum], axis=1)

    df_agg = df_uids \
        .merge(df_agg, on='Yizhibo_UID', how='inner') \
        .drop(columns=['Yizhibo_UID'])

    df_agg.to_csv(os.path.join(DATA_DIR, f'yizhibo_video_{category}_agg.csv'), index=False)

    ##
    df_shops = pd.read_csv(os.path.join(DATA_DIR, 'taobao_shops.csv'))
    df_video['play.length.s'] = df_video['play.length'] * df_video['sell']
    df_video['play.length.ns'] = df_video['play.length'] * df_video['nonsell']
    df_agg_u = df_video.loc[df_video['stream_time'] <= 30] \
        .groupby('Yizhibo_UID') \
        .agg({'play.length.s': 'mean',
              'play.length.ns': 'mean',
              'sell': 'sum',
              'nonsell': 'sum'}) \
        .rename(columns={'sell': 'total.s', 'nonsell': 'total.ns'}) \
        .reset_index()
    uids_hasvideo = {'YU' + k.split('/')[0] for k in label.keys()}
    df_agg_u['has_video'] = df_agg_u['Yizhibo_UID'].isin(uids_hasvideo).astype(int)

    df_agg_u = df_uids \
        .merge(df_shops, on='Taobao_SID', how='inner') \
        .merge(df_agg_u, on='Yizhibo_UID', how='inner') \
        .drop(columns=['Yizhibo_UID', 'Weibo_UID'])

    df_agg_u.to_csv(os.path.join(DATA_DIR, f'taobao_shops_{category}_agg.csv'), index=False)
