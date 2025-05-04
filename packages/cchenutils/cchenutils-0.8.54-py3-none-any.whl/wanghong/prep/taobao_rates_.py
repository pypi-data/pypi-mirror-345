# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/12/20
# @File  : [wanghong] taobao_rates_.py


import pandas as pd
from tqdm.auto import tqdm
from prep.utils import DATA_DIR, calc_time


def main():
    print(__name__)

    (pd.read_csv(f'{DATA_DIR}/taobao_rates.csv')
     .merge(pd.read_csv(f'{DATA_DIR}/taobao_items.csv', usecols=['Taobao_IID', 'Taobao_SID']), on=['Taobao_IID'], how='left')
     .merge(pd.read_csv(f'{DATA_DIR}/taobao_rates_discounts.csv'), on=['Taobao_RID'], how='left')
     .merge(pd.read_csv(f'{DATA_DIR}/taobao_rates_dates.csv'), on=['Taobao_RID'], how='left')
     .to_csv(f'{DATA_DIR}/taobao_rates_.csv', index=False))


if __name__ == '__main__':
    main()
    # pass
