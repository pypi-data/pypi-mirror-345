# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/19/20
# @File  : [wanghong] taobao_comments_btm.py


import os
import re

import jieba
import numpy as np
import pandas as pd
from wanghong.utils import DATA_DIR


def punct_translate(s):
    d = {
        '。': '.',
        '！': '!',
        '？': '?',
        '！': '!',
        '，': ',',
        '“': '"',
        '”': '"'
    }
    pattern = re.compile(r'(' + '|'.join(d.keys()) + r')')
    return pattern.sub(lambda x: d[x.group()], s)


def load_stopwords():
    stopwords = []
    for fp in {'百度停用词表.txt', '四川大学机器智能实验室停用词库.txt', '哈工大停用词表.txt', '中文停用词表.txt'}:
        with open('../stopwords/' + fp, 'r') as i:
            stopwords += [line.strip() for line in i if re.sub('[a-zA-Z0-9]', '', line.strip())]
    return set(stopwords)


def jieba_cut(s):
    return ' '.join(jieba.cut(s, cut_all=False))


def cut_sent(para):
    para = re.sub(r'([。！？?])([^”’])', r"\1\n\2", para)
    para = re.sub(r'(\.{6})([^”’])', r"\1\n\2", para)
    para = re.sub(r'(…{2})([^”’])', r"\1\n\2", para)
    para = re.sub(r'([。！？?][”’])([^，。！？?])', r'\1\n\2', para)
    para = para.rstrip()
    return para.split("\n")


def index(content):
    stopwords = load_stopwords()
    wid = dict()
    out = []
    for sent in content:
        words = sent.strip().split()
        sentid = []
        for word in words:
            if word in stopwords:
                continue
            if word not in wid:
                this_id = len(wid)
                wid[word] = this_id
            else:
                this_id = wid[word]
            sentid.append(this_id)
        out.append(' '.join(str(_id) for _id in sentid))
    return out, wid


##
if __name__ == '__main__':
    K = 20  # number of topics
    beta = 0.005
    niter = 100
    save_step = 501
    dp_model = os.getcwd() + os.path.sep
    fp_doc_wids = os.path.join(dp_model, 'btm_doc_wids.txt')
    fp_vocab = os.path.join(dp_model, 'btm_vocab.txt')

    df_items = pd.read_csv('/home/cchen/Dropbox/projects/wanghong/analysis/df_items_clothes.csv')

    df_rates = pd.read_csv(os.path.join(DATA_DIR, 'taobao_rates_.csv'), usecols=['Taobao_IID', 'content'])
    df_rates = df_rates.loc[df_rates['Taobao_IID'].isin(df_items['Taobao_IID'])]
    df_rates = df_rates.loc[~df_rates['content'].isnull()]
    df_rates = df_rates.loc[df_rates['content'].apply(lambda x: x != '系统默认评论' and len(x) >= 5)]
    df_rates['content'] = df_rates['content'].apply(punct_translate)
    df_rates['words'] = df_rates['content'].apply(jieba_cut)
    df_rates['words_id'], vocab = index(df_rates['words'].tolist())
    df_rates = df_rates.loc[df_rates['words_id'] != '']

    df_rates['words_id'].to_csv(fp_doc_wids, index=False, header=False)
    df_rates[['Taobao_IID', 'words_id']].to_csv(os.path.join(DATA_DIR, 'taobao_rates_wordids.csv'), index=False)
    df_vocab = pd.DataFrame(sorted(vocab.items(), key=lambda d: d[1]))
    df_vocab[[1, 0]].to_csv(fp_vocab, index=False, header=False, sep='\t', encoding='utf-8')

    input('Press any after running scriptbelow in Terminal\n{} est {} {} {} {} {} {} {} {}'.format(
        os.path.join('/home/cchen/pylibs/BTM/', 'src', 'btm'),
        K,
        len(vocab),
        round(50. / K, 3),
        beta,
        niter,
        save_step,
        fp_doc_wids,
        dp_model
    ))

    input('Press any after running scriptbelow in Terminal\n{} inf sum_b {} {} {}'.format(
        os.path.join('/home/cchen/pylibs/BTM/', 'src', 'btm'),
        K,
        fp_doc_wids,
        dp_model
    ))

    print('python3 {} {} {} {}'.format(
        os.path.join('/home/cchen/pylibs/BTM/', 'script', 'topicDisplay.py'),
        dp_model,
        K,
        fp_vocab
    ))

    doc_scores = np.loadtxt(os.path.join(dp_model, 'k{}.pz_d'.format(K)))
    # topics = np.array(list('2212'))  # 1: seller  2: product  0: neither
    # doc_topics = doc_scores > (1./K)
    #
    # # df_rates = pd.read_csv(os.path.join(DATA_DIR, 'taobao_rates_wordids.csv'))
    # df_comments_btm = df_rates[['Taobao_SID', 'Taobao_IID']]
    # df_comments_btm['comment_s'] = (np.sum(doc_topics[:, np.argwhere(topics == '1').flatten()], axis=1) > 0).astype(int)
    # df_comments_btm['comment_p'] = (np.sum(doc_topics[:, np.argwhere(topics == '2').flatten()], axis=1) > 0).astype(int)
    # df_comments_btm.to_csv(os.path.join(DATA_DIR, 'taobao_comments_btm.csv'), index=False)
    #
    # df_comments_btm_agg = df_comments_btm \
    #     .groupby('Taobao_IID').agg({'comment_s': 'sum', 'comment_p': 'sum', 'Taobao_SID': 'first'}).reset_index()
    # if LEVEL.endswith('SID'):
    #     df_comments_btm_agg = df_comments_btm_agg \
    #         .groupby('Taobao_SID').agg({'comment_s': 'mean', 'comment_p': 'mean'}).reset_index()
    #
    # fp_agg = os.path.join('../analysis', 'df_panel_{}_comments_sp_btm.csv'.format(
    #     'users' if LEVEL.endswith('SID') else 'items'))
    # df_comments_btm_agg.to_csv(fp_agg, index=False)
    spam = [18, 17, 16, ]
