# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/27/20
# @File  : [wanghong] taobao_items_category.py


import itertools
import re
import string
from collections import Counter

import jieba
import pandas as pd
from zhon import hanzi


def remove_punct(x):
    return re.sub('[' + hanzi.punctuation + string.punctuation + ']', '', x)


def jieba_cut(x):
    return list(jieba.cut(x, cut_all=False))


def contains(x, keywords):
    cnt = 0
    out = []
    for k, v in keywords.items():
        if k in x:
            cnt += 1
            out.append(v.split('/')[0])
    return out


def taobao_items_category(fp_src, fp_dst, keywords):
    df_shops = pd.read_csv(fp_src.replace('items', 'shops'), usecols=['Taobao_SID', 'category']).dropna(subset=['category'])
    df_items = pd.read_csv(fp_src, usecols=['Taobao_IID', 'Taobao_SID', 'title']).dropna(subset=['title'])
    df_items['title_tokens'] = df_items['title'].fillna('').apply(jieba_cut)

    category_keywords = {
        'male': ['男'],
        'female': ['女'],
        'clothes': ['衣', '服'],
        'clothes/upper': ['袖', '恤', '衫'],
        'clothes/cape': ['披肩', '丝巾'],
        'clothes/jacket': ['大衣', '棉服', '羽绒服', '外套', '夹克'],
        'clothes/pants': ['裤'],
        'clothes/dress': ['裙'],
        'clothes/under': ['内衣', '内裤', '背心', '吊带'],
        'hat': ['帽'],
        'shoe': ['鞋'],
        'shoe/female': ['高跟', '靴'],
        # 'bag': ['包'],
        'luggage': ['箱'],
        'maternity': ['妈妈'],
        'kid': ['童', '益智', '幼儿'],
        'baby': ['婴儿', '宝宝'],
        'trinket': ['耳环', '坠', '925', '饰品', '链', '戒指', '胸针', '镯', '手串', '纯银', '耳钉'],
        'jewelry': ['玉', '翡翠', '珠宝'],
        'food': ['零食', '食品', '酱', '面食', '糕点'],
        'cosmetics': ['化妆', '美妆', '乳液', '唇', '爽肤', '霜', '精华', 'ml', '洗面', '膏', '面膜', '眉', '眼',
                      '粉饼', '粉底', '腮红', '口红', '毛孔', '洗发'],
        'sports': ['运动'],
        'plant': ['多肉', '绿植', '植物', '盆栽'],
        'senior': ['老年'],
        'health': ['克', '阿胶', '药'],
        'decorator': ['灯', '贴纸', '贴画', '墙', '漆', '室内'],
        'farm': ['农家', '农夫', '肥', '种子'],
        'kitchen': ['厨房'],
        'tea': ['茶'],
        'fruit': ['果'],
        'instrumental': ['谱'],
        'instruments': ['吉他'],
        'electronics': ['电脑', '手机', '科技', '台式', '蓝牙'],
        'logistics': ['快递', '物流', '速递'],
        'daigou': ['代购', '免税'],
        'used': ['二手'],
        'car': ['汽车'],
        'tools': ['铝合金'],
        'cosplay': ['cosplay'],
        'no': ['妙针', 'led', '门铃', '伞', '公仔']
    }
    keyword_category = {k: c for c, ks in category_keywords.items() for k in ks}

    df_items['contain'] = df_items['title'].apply(lambda x: contains(x.lower(), keyword_category))
    df_items.groupby('Taobao_SID').agg({'contain': lambda x: {it for l in x for it in l if it},
                                        'title': '\n'.join})
    a = df_items['title'].loc[df_items['contain'] == 0].to_list()

    len(set(df_items['Taobao_SID'].loc[df_items['contain'] == 0].to_list()))


    attributes_count = Counter(itertools.chain(*df_items['title_tokens'].to_list()))
    attributes_count = sorted(attributes_count.items(), key=lambda x: -x[1])


if __name__ == '__main__':
    fp_src = '/home/cchen/data/wanghong/taobao_items.csv'