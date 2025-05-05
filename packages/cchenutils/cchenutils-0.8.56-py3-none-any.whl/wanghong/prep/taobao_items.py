#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/7/20
# @File  : [wanghong] taobao_items.py


'''
1. Add prefix to IDs
2. Remove items with NA title
3. Remove 补运费/差价 items
4. [REMOVED] Create `list_price` 取中间价
'''


import pandas as pd

from prep.utils import DATA_DIR, MIN_PRICE


def mean_price(price):
    if '-' not in str(price):
        return float(price) if str(price).strip() else None
    p1, p2 = price.split('-')
    return (float(p1) + float(p2)) / 2


def contains_either(content, keywords_must, keywords_include, keywords_exclude):
    for km in keywords_must:
        if km in content:
            return True
    for ke in keywords_exclude:
        if ke in content:
            return False
    for ki in keywords_include:
        if ki in content:
            return True
    return False


def main():
    print(__name__)

    df_items = pd.read_csv(f'{DATA_DIR}/_taobao_items.csv', dtype={'_id': str, 'shopid': str}) \
        .rename(columns={'_id': 'Taobao_IID', 'shopid': 'Taobao_SID'})

    df_items = df_items.dropna(subset=['title'])
    df_items = df_items.loc[df_items['title'].apply(lambda x: not contains_either(
        x, {'异常', '专用链接'}, {'补', '邮费', '差价', '运费'}, {'免运', '包运', '包邮', '免邮', '不补'}))]

    df_items['Taobao_IID'] = 'TI' + df_items['Taobao_IID']
    df_items['Taobao_SID'] = 'TS' + df_items['Taobao_SID']
    # df_items['list_price'] = df_items['price'].apply(mean_price)

    # attributes_kv = df_items['attributes'].fillna('[]').progress_apply(eval).progress_apply(dict)
    # df_items['attributes'] = attributes_kv.apply(lambda x: ' '.join(x.values()))
    #
    # attributes_count = Counter(itertools.chain(*attributes_kv.apply(lambda x: x.keys())))
    # attributes_count = sorted(attributes_count.items(), key=lambda x: -x[1])
    # selected_keys = {k for k, v in attributes_count[:top_attributes]}
    # attributes_kv = attributes_kv.apply(lambda x: {k: v for k, v in x.items() if k in selected_keys})
    # df_items = pd.concat([df_items, attributes_kv.progress_apply(pd.Series)], axis=1)

    # del df_items['price']
    # del df_items['listprice']

    df_items.loc[df_items['list_price'].apply(lambda x: float(x) > MIN_PRICE)] \
        .to_csv(f'{DATA_DIR}/taobao_items.csv', index=False)


if __name__ == '__main__':
    main()
