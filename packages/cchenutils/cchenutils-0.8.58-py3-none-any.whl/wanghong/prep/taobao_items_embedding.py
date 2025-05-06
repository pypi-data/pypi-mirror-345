# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 4/4/20
# @File  : [wanghong] taobao_items_embedding.py


import os
import re
import string

import jieba
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm
from zhon import hanzi

from utils import DATA_DIR
category = 'clothes'


def remove_punct(x):
    return re.sub('[' + hanzi.punctuation + string.punctuation + ']', '', x)


def jieba_tokenize(x):
    return [it for it in jieba.cut(remove_punct(x), cut_all=False) if it != '']


def jieba_cut(x):
    return ' '.join([it for it in jieba.cut(remove_punct(x), cut_all=False) if it != '']) + ' '


def pca(X, cutoff=0.95):
    row, col = np.asarray(X).shape
    pca = PCA(n_components=col, svd_solver='full')
    pca.fit(X)
    lambdas = pca.singular_values_
    total = (lambdas ** 2).sum()
    this_total = 0.
    for i in range(len(lambdas)):
        this_total += lambdas[i] ** 2
        if this_total / total >= cutoff ** 2:
            break
    pca = PCA(n_components=i + 1, svd_solver='full')
    new = pca.fit_transform(X)
    # log(lambda1/lambda2) or lambda1 / sqrt(sum(lambda_i))
    return new.squeeze().round(3).tolist()


def main():
    print(__name__)
    category = 'clothes'
    tqdm.pandas()

    df_shops = pd.read_csv(f'{DATA_DIR}/taobao_shops.csv')

    df_items = pd.read_csv(f'{DATA_DIR}/taobao_items.csv')
    df_items = df_items.loc[df_items['Taobao_SID'].isin(
        df_shops['Taobao_SID'].loc[df_shops['category_manual'].isin({category}).to_list()])]

    emb = np.load('/mnt/nvme/yizhibo/fashionnet_inshop.npz')
    df_items['image_embedding'] = df_items.progress_apply(
        lambda x: emb.get(os.path.join(x['Taobao_SID'][2:], x['Taobao_IID'][2:])), axis=1)
    df_items = df_items.dropna(subset=['image_embedding']).reset_index(drop=True)

    # df_image_pca = pd.DataFrame(pca(df_items['image_embedding'].to_list(), cutoff=0.95))
    # df_image_pca.columns = [f'image_pca_{col + 1}' for col in df_image_pca.columns]
    #
    # df_items['title_tokens'] = df_items['title'].apply(jieba_cut)
    # df_items_s = df_items.groupby(['Taobao_SID']).agg({'title_tokens': 'sum'}).reset_index()
    # shop_counter = CountVectorizer(min_df=0.1, max_df=0.9)
    # shop_counter.fit_transform(df_items_s['title_tokens'].to_list())
    # vocab = shop_counter.vocabulary_.keys()
    # tfidf = TfidfVectorizer(vocabulary=vocab).fit_transform(df_items['title_tokens'].tolist())
    # df_title_pca = pd.DataFrame(pca(tfidf.todense(), cutoff=0.95))
    # df_title_pca.columns = [f'title_pca_{col + 1}' for col in df_title_pca.columns]
    #
    # df_items = df_items.drop(columns=['image_embedding', 'title_tokens'])
    #
    # df_pca = pd.concat([df_items[['Taobao_SID', 'Taobao_IID']], df_image_pca], axis=1)

    df_embedding = pd.DataFrame(np.asarray(df_items['image_embedding'].tolist()))
    df_embedding.columns = [f'embedding_{col + 1}' for col in df_embedding.columns]
    df_embedding['Taobao_IID'] = df_items['Taobao_IID']
    df_embedding.to_csv(f'../analysis/taobao_items_{category}_emb.csv', index=False, header=True)


if __name__ == '__main__':
    # main()

    # seller level
    df_embedding = pd.read_csv(f'../analysis/taobao_items_{category}_emb.csv')
    df_items = pd.read_csv('../analysis/df_items_clothes.csv', usecols=['Taobao_SID', 'Taobao_IID'])
    df_embedding_s = df_embedding.merge(df_items, on='Taobao_IID', how='left').drop(columns=['Taobao_IID'])
    df_embedding_s = df_embedding_s.groupby(['Taobao_SID'], as_index=False).agg('mean')
    df_embedding_s.to_csv(f'../analysis/taobao_sellers_{category}_emb.csv', index=False)
