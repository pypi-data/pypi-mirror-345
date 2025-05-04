# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/12/20
# @File  : [wanghong] yizhibo_first.py


from datetime import datetime

import pandas as pd

from utils import DATA_DIR, calc_time


def main():
    print(__name__)

    df_video = pd.read_csv(f'{DATA_DIR}/yizhibo_video.csv', usecols=['Yizhibo_UID', 'date']
                           , parse_dates=['date'], date_parser=lambda x: datetime.strptime(x, '%Y-%m-%d'))
    df_first = df_video.groupby('Yizhibo_UID').agg({'date': 'min'}) \
        .rename(columns={'date': 'first_stream_date'}).reset_index()
    df_first['first'] = df_first['first_stream_date'].apply(calc_time)
    df_first = df_first.loc[df_first['first'] >= 0]
    df_first.to_csv(f'{DATA_DIR}/yizhibo_first.csv', index=False)


if __name__ == '__main__':
    main()
