# # !/usr/bin/env python
# # -*- coding: utf-8 -*-
# # @Author: Cheng Chen
# # @Email : cchen224@uic.edu
# # @Time  : 3/30/20
# # @File  : [wanghong] taobao_shops_category_manual.py
#
#
import itertools
import re
import string
from collections import Counter

import jieba
import pandas as pd
from zhon import hanzi

import os
import time
from pymongo import MongoClient



def remove_punct(x):
    return re.sub('[' + hanzi.punctuation + string.punctuation + ']', '', x)


def jieba_cut(x):
    return list(jieba.cut(x, cut_all=False))


def contains(x, keywords):
    # cnt = 0
    # out = set()
    for k, v in keywords:
        if k in x:
            # cnt += 1
            return v
    return ''
    # out.add(v.split('/')[0])
    # return '|'.join(out) if len(out) == 1 else ''


def contains_lst(lst, keyword):
    cnt = 0
    for it in lst:
        if keyword.lower() in it.lower():
            cnt += 1
    return cnt, cnt / len(lst)


if __name__ == '__main__':
    map = pd.read_csv('/home/cchen/data/wanghong/uids.csv')
    yids = map['Yizhibo_UID'].apply(lambda x: x[2:]).to_list()
    sids = map['Taobao_SID'].apply(lambda x: x[2:]).to_list()
    map = dict(zip(yids, sids))
    uids = set(map[yid] for yid in os.listdir('/media/cchen/exec/yizhibo/nosilence_20to30s/ts/') if yid in map and
               len(os.listdir(f'/media/cchen/exec/yizhibo/nosilence_20to30s/ts/{yid}')))

    items = pd.read_csv('/home/cchen/data/wanghong/taobao_items.csv').groupby('Taobao_SID').agg(
        {'title': '\n'.join}).reset_index()
    items = dict((row[1:] for row in items.itertuples()))
#
#
#     category_keywords = {
#         'clothes': ['女装', '工装', '时装', '服装', '男装', '职业装',
#                     '服饰', '服饰', '汉服', '演出服', '礼服', '羽绒服', '舞服', '鞋服', '私服', '面包服',
#                     'studio', '工作室', 'factory'],
#         'kid': ['童装', '益智', '幼儿'],
#         'baby': ['婴儿', '宝宝', '母婴'],
#         'maternity': ['孕妇装', '孕装'],
#         'bag': ['包包', '包店', '包铺', '女包', '潮包', '美包'],
#         'shoe': ['鞋'],
#         'sports': ['运动', '体育'],
#         'cosmetics': ['美妆', '护肤'],
#         'decorator': ['装饰', '包装'],
#         'service': ['服务'],
#         'trinket': ['首饰', '饰品'],
#         'jewlery': ['珠宝', '翡翠'],
#         'food': ['面包', '小吃', '零食', '食品'],
#         'health': ['健康'],
#         'home': ['家具', '定制家具', '家居'],
#         'electronics': ['数码'],
#         'daigou': ['代购', '免税'],
#     }
#     keyword_category = [(k, c) for c, ks in category_keywords.items() for k in ks]
#     keyword_category = sorted(keyword_category, key=lambda x: -len(x[0]))
#
#     category_keywords_i = {
#         # 'male': ['男'],
#         # 'female': ['女'],
#         'clothes': ['衣', '服'],
#         'clothes/upper': ['袖', '恤', '衫', 'T桖'],
#         'clothes/cape': ['披肩', '丝巾'],
#         'clothes/jacket': ['大衣', '棉服', '羽绒服', '外套', '夹克'],
#         'clothes/pants': ['裤'],
#         'clothes/dress': ['裙'],
#         'clothes/under': ['内衣', '内裤', '背心', '吊带'],
#         'hat': ['帽'],
#         'shoe': ['鞋'],
#         'shoe/female': ['高跟', '靴'],
#         # 'bag': ['包'],
#         'luggage': ['箱'],
#         'maternity': ['妈妈'],
#         'kid': ['童', '益智', '幼儿'],
#         'baby': ['婴儿', '宝宝'],
#         'trinket': ['耳环', '坠', '925', '饰品', '链', '戒指', '胸针', '镯', '手串', '纯银', '耳钉'],
#         'jewelry': ['玉', '翡翠', '珠宝'],
#         'food': ['零食', '食品', '酱', '面食', '糕点'],
#         'cosmetics': ['化妆', '美妆', '乳液', '唇', '爽肤', '霜', '精华', 'ml', '洗面', '膏', '面膜', '眉', '眼',
#                       '粉饼', '粉底', '腮红', '口红', '毛孔', '洗发'],
#         'sports': ['运动'],
#         'plant': ['多肉', '绿植', '植物', '盆栽'],
#         'senior': ['老年'],
#         'health': ['克', '阿胶', '药'],
#         'decorator': ['灯', '贴纸', '贴画', '墙', '漆', '室内'],
#         'farm': ['农家', '农夫', '肥', '种子'],
#         'kitchen': ['厨房'],
#         'tea': ['茶'],
#         'fruit': ['果'],
#         'instrumental': ['谱'],
#         'instruments': ['吉他'],
#         'electronics': ['电脑', '手机', '科技', '台式', '蓝牙'],
#         'logistics': ['快递', '物流', '速递'],
#         'daigou': ['代购', '免税'],
#         'used': ['二手'],
#         'car': ['汽车'],
#         'tools': ['铝合金'],
#         'cosplay': ['cosplay'],
#         'no': ['妙针', 'led', '门铃', '伞', '公仔'],
#     }
#
#     category_keywords_eating = {
#         'farm': ['苹果', '橙', '现摘', '木耳', '核桃', '干果', '馒头', '大米', '面粉', '海', '蜜', '自制'],
#         'herbal': ['冬虫夏草', '花旗参', '枸杞', '燕窝', '药材'],
#         'food': ['零食', '肉干', '小吃', '熟食', '糖'],
#         'health': ['排毒', '健康',  '针灸', '精油']
#     }
#     keyword_category_i = [(k, c) for c, ks in category_keywords_i.items() for k in ks]
#     keyword_category_i = sorted(keyword_category_i, key=lambda x: -len(x[0]))
#
#     client = MongoClient()
#     collection = client['yizhibo']['taobao_shops']
#     shops = [shop for shop in collection.find({'category_manual': {'$in': ['clothes']}}) if 'TS' + shop['_id'] in items]
# #     # if shop['_id'] in uids]
#     start = 0
#     for cnt, shop in enumerate(shops):
#         # if cnt < start:
#         #     continue
#         try:
#             shopid = shop['_id']
#             shopname = shop.get("shopname", "")
#             brand = shop.get('brand', '')
#             print(items.get('TS' + shopid))
#             print(f'{cnt + 1} / {len(shops)} {shopname}:{brand}')
#             # category = shop.get('category_manual', contains(shopname.lower(), keyword_category))
#             # # category = contains(shopname.lower(), keyword_category)
#             # # category = ''
#             # category_i = contains(items.get('TS' + shopid).lower(), keyword_category_i)
#             # if 'category_manual' in shop:
#             #     category_tmp = input(f'{shopid} {shopname} {category} m:')
#             # # elif category:
#             # #     category_tmp = input(f'{shopid} {shopname} {category} s:')
#             # # if category_i:
#             # #     category_tmp = input(f'{shopid} {shopname} {category_i} i:')
#             # #     if not category_tmp:
#             # #         category_tmp = category_i
#             # else:
#             #     category_tmp = input(f'{shopid} {shopname} Category:')
#             # if category_tmp:
#             #     category = category_tmp
#             # if category == 'd':
#             #     collection.update_one({'_id': shopid}, {'$unset': {'category_manual': ''}})
#             #     print('\n\n\n')
#             #     continue
#             # if category:
#             #     collection.update_one({'_id': shopid}, {'$set': {'category_manual': category}})
#
#
#             c, r = contains_lst(items.get('TS' + shopid).split('\n'), shopname) if shopname else (0, 0.)
#             brand = input(f'{shopname} {c} {r}:')
#             if brand == 's':
#                 brand = shopname
#             elif not brand:
#                 print('\n\n\n')
#                 continue
#
#             if brand:
#                 collection.update_one({'_id': shopid}, {'$set': {'brand': brand}})
#             print(f'{shopname} {brand}')
#             print('\n\n\n')
#         except KeyboardInterrupt:
#             break
#
# ['grocery/fruit', 'grocery/herbal', 'grocery/grains', 'grocery/dried', 'health']
#
# ['trinket', 'fashion', 'cosmetics', 'bag', 'shoe', 'farm', 'book', 'jewelry', 'instrumental', 'food', 'sports', 'kids',
#  'cosplay', 'plant', 'health', 'toy', 'skill', 'decorator', 'maternity', 'tea', 'wine', 'accessories', 'pet', 'furniture', 'kitchen', 'gift', 'grocery']
#
# shops = [shop for shop in collection.find({'category_manual': {'$ne': None}}) if 'TS' + shop['_id'] in items]# and shop['_id'] in a]
# categories = [shop['category_manual'] for shop in shops]
# sorted([(k, v) for k, v in Counter(categories).items()], key=lambda x: -x[1])
#
#
# shops = [shop for shop in collection.find({'category_manual': {'$in': ['gift', 'toy']}}) if 'TS' + shop['_id'] in items]
# for shop in shops:
#     shopid = shop['_id']
#     # collection.update_one({'_id': shopid}, {'$unset': {'category_manual': ''}})
#     # collection.update_one({'_id': shopid}, {'$set': {'category_manual': 'jewelry'}})
#
# for shop in shops:
#     if shop['category_manual'].startswith('category_keywords_i = '):
#         print(shop['_id'])
#
# df_transcript = pd.read_csv('/home/cchen/data/wanghong/yizhibo_transcript.csv')
# a = set(df_transcript['Yizhibo_UID'].apply(lambda x: map.get(x[2:])).dropna().to_list())