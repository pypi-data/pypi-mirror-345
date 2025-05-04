# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 4/7/20
# @File  : [wanghong] transcript_embedding.py

import re
import string
import os
import jieba
import pandas as pd
from gensim.models import word2vec
from zhon import hanzi


def load_stopwords():
    stopwords = set()
    for fp in {'百度停用词表.txt', '四川大学机器智能实验室停用词库.txt', '哈工大停用词表.txt', '中文停用词表.txt'}:
        with open('stopwords/' + fp, 'r') as i:
            stopwords |= {line.strip() for line in i}# if not line[0].isalpha()}
    return stopwords


def remove_punct(x):
    return re.sub('[' + hanzi.punctuation + string.punctuation + ']', '', x)


def jieba_tokenize(x):
    return [it for it in jieba.cut(remove_punct(x), cut_all=False) if it != '']


def jieba_cut(x):
    return ' '.join([it for it in jieba.cut(remove_punct(x), cut_all=False) if it != '']) + ' '

#
# import sys
# args = sys.argv[1:]
# workers = int(args[0])
from wanghong.utils import DATA_DIR
stopwords = load_stopwords()
df_transcript = pd.read_csv(DATA_DIR + '/yizhibo_transcript.csv', dtype=str)
df_transcript['tokens'] = df_transcript['transcript'].apply(
    lambda x: [token for token in jieba_tokenize(x) if token not in stopwords and remove_punct(token)])
df_transcript = df_transcript.loc[df_transcript['tokens'].apply(lambda x: True if len(x) >= 5 else False)]
del df_transcript['transcript']
df_transcript.to_csv(DATA_DIR + '/yizhibo_transcript_tokens.csv', index=False)
sentences = df_transcript['tokens'].to_list()
print('start trainning')
# model = word2vec.Word2Vec(sentences, sg=1, hs=1, min_count=3, window=5, size=100, iter=100, workers=workers)
