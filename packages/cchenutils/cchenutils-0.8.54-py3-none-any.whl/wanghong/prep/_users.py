# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/12/20
# @File  : [wanghong] _users.py


import pandas as pd

from utils import DATA_DIR


def adj_rate(rate, adj):
    rate -= adj
    return rate if rate >= 0 else 0


def gen_lvl_cutoff():
    lvls = [-1, 3, 10, 40, 90, 150, 250, 500]
    for x in range(3, 7):
        lvls.extend([10**x, 2*10**x, 5*10**x])
    lvls.extend([10**7, float('inf')])
    return lvls


LVLs = gen_lvl_cutoff()


def get_lvl(x):
    if not x:
        return 0
    for i, lvl in enumerate(LVLs):
        if lvl < x <= LVLs[i + 1]:
            return i


def main():
    print(__name__)

    df_users = pd.read_csv(f'{DATA_DIR}/uids.csv')
    df_shops = pd.read_csv(f'{DATA_DIR}/taobao_shops.csv') \
        .rename(columns={'seller_rate.overall': '_seller_rate.overall'})

    # Adjust user level from ratings
    df_rates_ = pd.read_csv(f'{DATA_DIR}/taobao_rates_.csv')
    df_rates_['adj'] = df_rates_['rate'] * df_rates_['after']
    df_rates_adj = df_rates_.groupby('Taobao_SID').agg({'adj': sum}).reset_index()
    df_rates_['valid_b4'] = df_rates_['valid'] * ((df_rates_['after'] - 1) * -1)
    df_rates_comments = df_rates_.groupby('Taobao_IID').agg({'Taobao_SID': 'first', 'valid_b4': 'sum'}).reset_index() \
        .groupby('Taobao_SID').agg({'valid_b4': 'mean'}).reset_index().rename(columns={'valid_b4': 'valid_mean'})

    # Taobao items
    df_items = pd.read_csv(f'{DATA_DIR}/taobao_items.csv'
                           , usecols=['Taobao_SID', 'Taobao_IID', 'n_desc_images', 'list_price'])
    df_items_price = df_items.groupby('Taobao_SID').agg({'n_desc_images': 'mean', 'list_price': 'mean'}).reset_index() \
        .rename(columns={'n_desc_images': 'images_mean', 'list_price': 'price_mean'})

    # Yizhibo first
    df_first = pd.read_csv(f'{DATA_DIR}/yizhibo_first.csv', usecols=['Yizhibo_UID', 'first'])
    df_first = df_first.loc[df_first['first'] >= 0]

    # Yizhibo_video_cate
    df_video = pd.read_csv(f'{DATA_DIR}/yizhibo_video_clothes.csv') \
        .groupby('Taobao_SID') \
        .agg({'Yizhibo_VID': 'count', 'sell': 'mean'}) \
        .rename(columns={'Yizhibo_VID': 'stream_count'}) \
        .reset_index()

    # User level
    df_users = df_shops[['Taobao_SID', 'ifashion', 'category', 'category_manual', '_seller_rate.overall',
                         'dsr.logistics.score', 'dsr.match.score', 'dsr.service.score']] \
        .merge(df_items_price, on='Taobao_SID', how='inner') \
        .merge(df_rates_comments, on='Taobao_SID', how='inner') \
        .merge(df_rates_adj, on='Taobao_SID', how='inner') \
        .merge(df_users[['Taobao_SID', 'Yizhibo_UID']], on='Taobao_SID', how='inner') \
        .merge(df_first, on='Yizhibo_UID', how='inner') \
        .merge(df_video, on='Taobao_SID', how='left') \
        .drop(columns=['Yizhibo_UID'])

    df_users['seller_rate.overall'] = df_users.apply(lambda x: adj_rate(x['_seller_rate.overall'], x['adj']), axis=1)
    df_users['seller_rate.lvl'] = df_users['seller_rate.overall'].apply(get_lvl)

    # running seller rate
    df_sellerrate = df_rates_.groupby('Taobao_SID').agg({'rate': 'sum'}).reset_index().rename(columns={'rate': 'rate0'})
    df_users = df_users.merge(df_sellerrate, on='Taobao_SID', how='inner')
    df_users['rate0'] = df_users.apply(lambda x: x['_seller_rate.overall'] - x['rate0'], axis=1)

    # export
    df_users.to_csv('../analysis/df_users.csv', index=False)


if __name__ == '__main__':
    main()
