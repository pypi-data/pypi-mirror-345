# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 5/24/20
# @File  : [wanghong] taobao_items_sku.py


import pandas as pd

from utils import DATA_DIR


def main():
    print(__name__)

    df_rates = pd.read_csv(f'{DATA_DIR}/taobao_rates.csv', dtype={'Taobao_IID': str, 'auction.sku': str}) \
        .dropna(subset=['auction.sku'])
    df_items = df_rates.groupby('Taobao_IID') \
        .agg({'auction.sku': lambda x: len(set(x)),
              'bidPriceMoney.amount': lambda x: round(sum(x) / len(x), 2)}) \
        .reset_index()
    df_items.to_csv(f'{DATA_DIR}/taobao_items_sku.csv', index=False)


if __name__ == '__main__':
    main()
