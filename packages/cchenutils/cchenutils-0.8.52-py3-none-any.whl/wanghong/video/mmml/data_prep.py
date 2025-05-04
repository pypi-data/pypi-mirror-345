# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 4/7/20
# @File  : [wanghong] data_prep.py

import os
import random
from glob import iglob
from gensim.models import word2vec
import numpy as np
import pandas as pd
from keras.preprocessing.sequence import pad_sequences


def contains(x, keywords):
    for keyword in keywords:
        if keyword in x:
            return True
    return False


def load_npz(fp):
    npz = np.load(fp)
    sorted_keys = sorted([k for k in npz.keys() if '.' not in k], key=lambda x: int(x))
    return np.array([npz[key] for key in sorted_keys])


def generate_data(uid_vid, dp_emb, pad_size, sample_size=5, clips=None):
    if clips is None:
        clips = [fname for fname in os.listdir(os.path.join(dp_emb, uid_vid)) if fname.endswith('.npz')]
        clips = random.sample(clips, sample_size)
        clips = sorted(clips, key=lambda x: float(x.split('_')[0]))
    clips_emb = [load_npz(os.path.join(dp_emb, uid_vid, clip)) for clip in clips]
    clips_emb = pad_sequences(clips_emb, maxlen=pad_size, padding='post', truncating='post', dtype='float32')
    return clips, clips_emb


def generate_uvs(dp_emb, category, total_size, train_ratio, sample_size, pad_size):
    train_size = int(total_size * train_ratio)
    test_size = total_size - train_size

    map = pd.read_csv('/home/cchen/data/wanghong/uids.csv')
    yids = map['Yizhibo_UID'].to_list()
    sids = map['Taobao_SID'].to_list()
    map = dict(zip(sids, yids))
    df_shops = pd.read_csv('/home/cchen/data/wanghong/taobao_shops.csv', dtype=str)
    df_shops = df_shops.loc[df_shops['category_manual'].isin({category})]
    candidates = {map[sid] for sid in df_shops['Taobao_SID'].tolist() if sid in map}

    complete = {os.path.relpath(dp, dp_emb)
                for dp in iglob(os.path.join(dp_emb, '*', '*'))
                if len([fp for fp in os.listdir(dp) if fp.endswith('.npz')]) >= sample_size}

    df_transcript = pd.read_csv('/home/cchen/data/wanghong/yizhibo_transcript.csv', dtype=str)
    df_transcript = df_transcript.loc[df_transcript['Yizhibo_UID'].isin(candidates)]
    df_transcript['path'] = df_transcript.apply(lambda x: f'{x["Yizhibo_UID"][2:]}/{x["Yizhibo_VID"][2:]}', axis=1)
    df_data1 = df_transcript.loc[df_transcript['transcript'].apply(lambda x: contains(x, ['这款', '号链接']))]
    uvs1 = set(df_data1['path']) & complete

    extra = df_transcript.loc[df_transcript['transcript'].apply(lambda x: contains(x, ['淘宝']))]
    df_data0 = df_transcript.loc[~df_transcript['path'].isin(uvs1 | set(extra['path']))]
    uvs0 = set(df_data0['path']) & complete

    random.seed(1)
    uvs1 = random.sample(uvs1, total_size)
    uvs0 = random.sample(uvs0, total_size)

    # with open('/home/cchen/Dropbox/projects/wanghong/video/mmml/v1/uv_train.txt') as i:
    #     uvtn = [line.strip() for line in i]
    # with open('/home/cchen/Dropbox/projects/wanghong/video/mmml/v1/uv_test.txt') as i:
    #     uvtt = [line.strip() for line in i]
    # uvs = uvtn + uvtt
    # uvs1, uvs0 = zip(*[(uvs[i * 2], uvs[i * 2 + 1]) for i in range(len(uvs) // 2)])

    X_train = []
    y_train = [1, 0] * train_size
    uvse_train = []
    for uvt, uvf in zip(uvs1[:train_size], uvs0[:train_size]):
        clipst, embt = generate_data(uvt, dp_emb, pad_size, sample_size)
        clipsf, embf = generate_data(uvf, dp_emb, pad_size, sample_size)
        X_train += [embt, embf]
        uvse_train += [uvt + '\t' + '|'.join(clipst), uvf + '\t' + '|'.join(clipsf)]

    X_test = []
    y_test = [1, 0] * test_size
    uvse_test = []
    for uvt, uvf in zip(uvs1[-test_size:], uvs0[-test_size:]):
        clipst, embt = generate_data(uvt, dp_emb, pad_size, sample_size)
        clipsf, embf = generate_data(uvf, dp_emb, pad_size, sample_size)
        X_test += [embt, embf]
        uvse_test += [uvt + '\t' + '|'.join(clipst), uvf + '\t' + '|'.join(clipsf)]

    return X_train, X_test, y_train, y_test, uvse_train, uvse_test


def load_train_test(dp_emb, name_train, name_test, pad_size):
    X_train = [generate_data(uv, dp_emb, pad_size, clips=clips.split('|'))[1]
               for uv, clips in (line.split('\t') for line in name_train)]
    X_test = [generate_data(uv, dp_emb, pad_size, clips=clips.split('|'))[1]
              for uv, clips in (line.split('\t') for line in name_test)]
    return X_train, X_test


def load_train_test_text(fp_text, name_train, name_test, pad_size):
    df_transcript = pd.read_csv(fp_text, dtype=str)
    df_transcript['path'] = df_transcript.apply(
        lambda x: os.path.join(x['Yizhibo_UID'][2:], x['Yizhibo_VID'][2:], x['start'] + '_' + x['end']), axis=1)
    map = dict(zip(df_transcript['path'], df_transcript['tokens'].apply(eval)))
    model = word2vec.Word2Vec.load('/home/cchen/data/wanghong/w2c_pretrained.model')

    X_train = [load_data_text(uv, clips, pad_size, map, model)
               for uv, clips in (line.split('\t') for line in name_train)]
    X_test = [load_data_text(uv, clips, pad_size, map, model)
              for uv, clips in (line.split('\t') for line in name_test)]
    return X_train, X_test

    #fp_tokens, [], names, pad_size = 40

def load_data_text(uv, clips, pad_size, map, model):
    zeros = np.zeros(100, dtype='float32')
    emb = []
    for clip in clips.split('|'):
        path = os.path.join(uv, os.path.splitext(clip)[0])
        if path not in map:
            emb.append([zeros.copy()])
        else:
            emb.append([model[token] for token in map[path] if token in model and token not in {'淘宝', '淘', '这款', '号链接'}])
    return pad_sequences(emb, maxlen=pad_size, padding='post', truncating='post', dtype='float32')


def load_name(fp):
    with open(fp, 'r') as i:
        return [line.strip() for line in i]


def generate_broader(category, name_train, sample_size, pad_size):
    map = pd.read_csv('/home/cchen/data/wanghong/uids.csv')
    yids = map['Yizhibo_UID'].to_list()
    sids = map['Taobao_SID'].to_list()
    map = dict(zip(sids, yids))
    df_shops = pd.read_csv('/home/cchen/data/wanghong/taobao_shops.csv', dtype=str)
    df_shops = df_shops.loc[df_shops['category_manual'].isin({category})]
    in_catogry = {map[sid][2:] for sid in df_shops['Taobao_SID'].tolist() if sid in map}

    dp_irv2 = '/mnt/nvme/yizhibo/nosilence_20to30s/inception_resnet_v2'
    dp_trn = '/mnt/nvme/yizhibo/nosilence_20to30s/trn'

    X_irv2 = []
    X_trn = []
    name = []
    for fp in iglob(os.path.join(dp_trn, '*', '*')):
        uid_vid = os.path.relpath(fp, dp_trn)
        uid, vid = uid_vid.split(os.path.sep)
        if uid_vid in name_train or uid not in in_catogry:
            continue

        candidates = {fname for fname in os.listdir(os.path.join(dp_trn, uid_vid)) if fname.endswith('.npz')} \
                     & {fname for fname in os.listdir(os.path.join(dp_irv2, uid_vid)) if fname.endswith('.npz')}
        if len(candidates) < sample_size:
            continue

        clips = random.sample(candidates, sample_size)
        clips = sorted(clips, key=lambda x: float(x.split('_')[0]))
        _, X_irv2_test = generate_data(uid_vid, dp_irv2, pad_size, sample_size=5, clips=clips)
        _, X_trn_test = generate_data(uid_vid, dp_trn, pad_size, sample_size=5, clips=clips)

        X_irv2.append(X_irv2_test)
        X_trn.append(X_trn_test)
        name.append(uid_vid + '\t' + '|'.join(clips))

    return name, X_irv2, X_trn


if __name__ == '__main__':
    from wanghong.utils import DATA_DIR

    category = 'clothes'
    pad_size = 50
    sample_size = 5
    total_size = 150
    train_ratio = 0.8

    # name, X_irv2, X_trn = generate_broader(category, sample_size, pad_size)

    # ## initialize with trn
    # dp_emb = '/mnt/nvme/yizhibo/nosilence_20to30s/trn'
    # X_train, X_test, y_train, y_test, name_train, name_test = \
    #     generate_uvs(dp_emb=dp_emb, category=category, total_size=total_size, train_ratio=train_ratio,
    #              sample_size=sample_size, pad_size=pad_size)
    # np.save('X_trn.npy', X_train + X_test)
    # np.save('y.npy', y_train + y_test)
    # with open('uvse_train.txt', 'w') as o:
    #     for name in name_train:
    #         o.write(name + '\n')
    # with open('uvse_valid.txt', 'w') as o:
    #     for name in name_test:
    #         o.write(name + '\n')
    #
    # ## load for inception_resnet_v2
    # name_train = load_name('uvse_train.txt')
    # name_test = load_name('uvse_valid.txt')
    # dp_emb = '/mnt/nvme/yizhibo/nosilence_20to30s/inception_resnet_v2'
    # X_train, X_test = load_train_test(dp_emb=dp_emb, name_train=name_train, name_test=name_test, pad_size=pad_size)
    # np.save('X_irv2.npy', X_train + X_test)
    #
    # ## load text
    name_train = load_name('uvse_train.txt')
    name_test = load_name('uvse_valid.txt')
    fp_tokens = '/home/cchen/data/wanghong/yizhibo_transcript_tokens.csv'
    X_train, X_test = load_train_test_text(fp_tokens, name_train, name_test, pad_size=40)
    np.save('X_w2v.npy', X_train + X_test)


    ## load for massive test
    # fp_tokens = '/home/cchen/data/wanghong/yizhibo_transcript_tokens.csv'
    # dp_data = '/home/cchen/data/wanghong/data_300'
    # name_train = {line.split('\t')[0] for line in load_name('uvse_train.txt') + load_name('uvse_valid.txt')}
    # names, X_irv2, X_trn = generate_broader(category, name_train, sample_size, pad_size)
    # _, X_txt = load_train_test_text(fp_tokens, [], names, pad_size=40)
    # np.save(os.path.join(DATA_DIR, 'data_300', 'X_irv2_test.npy'), X_irv2)
    # np.save(os.path.join(DATA_DIR, 'data_300', 'X_trn_test.npy'), X_trn)
    # np.save(os.path.join(DATA_DIR, 'data_300', 'X_w2v_test.npy'), X_txt)
    # with open('uvse_test.txt', 'w') as o:
    #     for name in names:
    #         o.write(name + '\n')