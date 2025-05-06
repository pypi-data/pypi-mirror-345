# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : chench@uwm.edu
# @Time  : 3/23/21
# @File  : [prep] weibo_timeline.py
import pandas as pd
import requests
from requests.exceptions import ConnectionError
from tqdm import tqdm

from utils import DATA_DIR


def contains(string, words):
    for word in words:
        if word in string:
            return True
    return False


def get_redirect_url(url):
    try:
        res = requests.get(url, allow_redirects=True)
        return res.url
    except ConnectionError as e:
        return e.request.url


def main():
    print(__name__)

    df_videos = pd.read_csv('../analysis/yizhibo_video_clothes_discount.csv').dropna(subset=['sell'])
    data = pd.read_csv(f'{DATA_DIR}/_weibo_timeline.csv', dtype=str) \
        .rename(columns={'uid': 'Weibo_UID', '_id': 'Weibo_MID', 'mid62': 'Weibo_MID62'}) \
        .fillna({'text': '', 'sent_from': '', 'reweibo': '', 'media.urls': '[]', 'urls': '[]'})

    data['Weibo_UID'] = 'WU' + data['Weibo_UID']
    data['Weibo_MID'] = 'WM' + data['Weibo_MID']
    data = data[data['Weibo_UID'].isin(df_videos['Weibo_UID'])]
    data = data.merge(pd.read_csv(f'{DATA_DIR}/weibo_users.csv', usecols=['Weibo_UID', 'nick']),
                      on='Weibo_UID', how='left')
    data.loc[data['media.urls'] == '[null]', 'media.urls'] = '[]'
    data['media.urls'] = data['media.urls'].apply(eval)
    data['urls'] = data['urls'].apply(eval)

    data['contains_streaming'] = data.apply(
        lambda x: ('直播' in x['text'])
                  and (x['media.type'] != 'video')
                  and (len(x['media.urls']) <= 1)
                  and (len([(t, u) for t, u in x['urls'] if t == '网页链接']) <= 1)
                  and (x['reweibo'] == '')
        , axis=1)
    data['redirect_urls'] = ''
    tqdm.pandas()
    data.loc[(data['contains_streaming']) & (data['streaming_from'] == ''), 'redirect_urls'] = \
        data.loc[(data['contains_streaming']) & (data['streaming_from'] == ''), 'urls'].progress_apply(
            lambda x: [get_redirect_url(u) for t, u in x if t == '网页链接' and len(x) == 1])

    data.to_csv(f'{DATA_DIR}/weibo_timeline.csv', index=False)


if __name__ == '__main__':
    main()
