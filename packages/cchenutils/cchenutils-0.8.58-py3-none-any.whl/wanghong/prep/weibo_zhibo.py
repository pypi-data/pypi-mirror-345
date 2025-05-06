# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : chench@uwm.edu
# @Time  : 3/23/21
# @File  : [prep] weibo_zhibo.py

import pandas as pd

from utils import DATA_DIR

print(__name__)


def main():
    data = pd.read_csv(f'{DATA_DIR}/weibo_timeline.csv', dtype=str)
    data = data[data['text'].fillna('').apply(lambda x: '淘宝直播' in x or '一直播' in x)]


if __name__ == '__main__':
    main()