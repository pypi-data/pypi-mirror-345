# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/19/20
# @File  : [wanghong] taobao_items_.py

import json
import re
import string
from functools import partial

import jieba
import pandas as pd
from jellyfish import levenshtein_distance
from tqdm import tqdm
from zhon import hanzi

from utils import DATA_DIR


clothing_keywords = {
    '内衣': 'underwear',
    '吊带': 'underwear',
    '文胸': 'underwear',
    '抹胸': 'underwear',
    '裙': 'skirt',
    '短裤': 'shorts',
    '裤': 'pants',
    't恤': 't-shirt',
    't': 't-shirt',
    'tee': 't-shirt',
    '短袖': 't-shirt',
    '卫衣': 'hoodie',
    '上衣': 'tops',
    '鞋': 'shoes',
    '靴': 'shoes',
    '袜': 'socks',
    '大衣': 'jackets',
    '外套': 'jackets',
    '羽绒服': 'jackets',
    '棉衣': 'jackets',
    '毛衣': 'sweaters',
    '衫': 'tops',
    '衬衣': 'tops',
    '长袖': 'tops',
    '背心': 'tops',
    '运动': 'activewear',
    '耳': 'jewelry',
    '项': 'jewelry',
    '包': 'bag',
    '帽': 'hats',
    '围巾': 'scarf',
    '围脖': 'scarf',
    '腰带': 'belts',
    '皮带': 'belts',
    '钱包': 'wallet',
    '牛仔': 'jeans',
    '婚礼': 'wedding',
    '婚纱': 'wedding',
    '新郎': 'wedding',
    '新娘': 'wedding',
    '比基尼': 'swimsuites',
    '泳': 'swimsuites'
}


def remove_punct(x):
    return re.sub('[' + hanzi.punctuation + string.punctuation + ']', '', x)


def levenshtein_ratio(long, short):
    len_l = len(long)
    len_s = len(short)
    if len_l >= len_s:
        lens = [levenshtein_distance(long[idx: idx + len_s], short) for idx in range(len_l - len_s + 1)]
        return 1 - min(lens) / len(short)
    else:
        return 0.


# def match(uid, title):
#     df_this = df_speech.loc[df_speech['Taobao_SID'] == uid].reset_index()
#     df_this['sim'] = df_this['transcript'].apply(partial(levenshtein_ratio, short=title))
#     nrow, _ = df_this.shape
#     if nrow:
#         sims = zip(df_this['Yizhibo_VID'].to_list(), df_this['sim'].to_list())
#         return max(sims, key=lambda x: x[1])
#     else:
#         return '', 0.
    

def jieba_cut(x):
    return list(jieba.cut(x, cut_all=False))


def token_match(tokens, transcript_tokens):
    count = 0
    for token in tokens:
        if token in transcript_tokens:
            count += 1
    return count


def match(uid, tokens, df_speech):
    df_this = df_speech.loc[df_speech['Taobao_SID'] == uid].reset_index()
    df_this['count'] = df_this['tokens'].apply(partial(token_match, tokens))
    nrow, _ = df_this.shape
    if nrow:
        sims = zip(df_this['Yizhibo_VID'].to_list(), df_this['count'].to_list())
        return max(sims, key=lambda x: x[1])
    else:
        return '', 0


def genderize_title(title):
    title = title.lower()
    kv = {
        '男女': 'u',
        '童': 'k',
        '女': 'f',
        '男': 'm'
    }
    for k, v in kv.items():
        if k in title:
            return v


def categorize_title(title):
    title = re.sub('包邮', '', title.lower())
    for k, v in sorted(clothing_keywords.items(), key=lambda x: -len(x[0])):
        if k in title:
            return v
    return ''


def main():
    print(__name__)
    tqdm.pandas()

    df_ids = pd.read_csv(f'{DATA_DIR}/uids.csv')

    df_transcript = pd.read_csv(f'{DATA_DIR}/yizhibo_transcript.csv')
    df_transcript = df_ids[['Taobao_SID', 'Yizhibo_UID']].merge(df_transcript, on='Yizhibo_UID', how='inner')
    df_transcript['tokens'] = df_transcript['transcript'].progress_apply(jieba_cut)
    df_speech = df_transcript.groupby(['Taobao_SID', 'Yizhibo_VID']).agg({'tokens': 'sum'}).reset_index()

    df_items = pd.read_csv(f'{DATA_DIR}/taobao_items.csv', dtype=str)
    df_items = df_items.loc[df_items['Taobao_SID'].isin(set(df_transcript['Taobao_SID'].to_list()))]
    df_clothes = pd.read_csv('../analysis/yizhibo_video_clothes.csv')
    df_items = df_items.loc[df_items['Taobao_SID'].isin(set(df_clothes['Taobao_SID'].to_list()))].reset_index(drop=True)

    df_items['title_tokens'] = df_items['title'].fillna('').progress_apply(jieba_cut)
    df_items[['Yizhibo_VID_title', 'title_matches']] = df_items.progress_apply(
        lambda x: match(x['Taobao_SID'], x['title_tokens'], df_speech), axis=1, result_type='expand')

    # df_items['attributes'] = df_items['attributes'].fillna('[]').apply(json.loads)
    df_items['gender'] = df_items['title'].apply(genderize_title)
    df_items['clothing'] = df_items['title'].apply(categorize_title)

    df_items['attribute_tokens'] = df_items['attributes'].fillna('').progress_apply(lambda x: x.split(' '))
    df_items[['Yizhibo_VID_attribute', 'attribute_matches']] = df_items.progress_apply(
        lambda x: match(x['Taobao_SID'], x['attribute_tokens'], df_speech), axis=1, result_type='expand')

    df_items.to_csv(f'{DATA_DIR}/taobao_items_.csv', index=False)


if __name__ == '__main__':
    main()

##

