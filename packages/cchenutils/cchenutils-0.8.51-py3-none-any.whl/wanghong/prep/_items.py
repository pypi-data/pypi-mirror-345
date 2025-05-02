# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 4/5/20
# @File  : [wanghong] _items.py


import os

import pandas as pd
from utils import DATA_DIR


def main():
    print(__name__)
    category = 'clothes'

    df_users = pd.read_csv(f'{DATA_DIR}/uids.csv')
    df_shops = pd.read_csv(f'{DATA_DIR}/taobao_shops.csv')
    df_items = pd.read_csv(f'{DATA_DIR}/taobao_items_.csv'
                           , usecols=['Taobao_SID', 'Taobao_IID', 'n_attributes', 'n_desc_images', 'list_price',
                                      'gender', 'clothing'])
    df_items_embedding = pd.read_csv(os.path.join(DATA_DIR, f'taobao_items_{category}_emb.csv'), usecols=['Taobao_IID'])
    df_items = df_items.loc[df_items['Taobao_IID'].isin(df_items_embedding['Taobao_IID'])]
    df_panel = pd.read_csv('../analysis/df_panel_items_.csv')

    df_panel['total_sales'] = df_panel.apply(lambda x: (x['after'] - 1) * x['n_ratings'] * -1, axis=1)
    df_panel['total_valid'] = df_panel.apply(lambda x: (x['after'] - 1) * x['n_valid'] * -1, axis=1)
    df_comments = df_panel.groupby('Taobao_IID') \
        .agg({'total_sales': 'sum', 'total_valid': 'sum', 'first': 'first'}) \
        .reset_index()

    df_items_sku = pd.read_csv(f'{DATA_DIR}/taobao_items_sku.csv')
    # df_avgcomments = df_panel.loc[df_panel['after'] == 0].groupby('Taobao_IID') \
    #     .agg({'total_sales': 'mean', 'total_valid': 'mean'})\
    #     .rename(columns={'total_sales': 'avg_sales', 'total_valid': 'avg_valid'}).reset_index()

    df_out = df_shops[['Taobao_SID', 'category_manual']] \
        .merge(df_items, on='Taobao_SID', how='inner') \
        .merge(df_comments, on='Taobao_IID', how='inner') \
        .merge(df_items_sku, on='Taobao_IID', how='left')

    df_out.to_csv(f'../analysis/df_items_{category}.csv', index=False)


if __name__ == '__main__':
    main()
