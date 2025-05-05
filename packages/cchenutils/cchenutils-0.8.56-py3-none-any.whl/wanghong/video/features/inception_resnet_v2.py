# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/31/20
# @File  : [wanghong] inception_resnet_v2.py


# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/22/20
# @File  : [wanghong] inceptionv3.py


import os
import time
from functools import partial
from glob import iglob
from zipfile import ZipFile, BadZipFile

import cv2
import numpy as np
import pandas as pd
from PIL import Image
from keras.applications import inception_resnet_v2
from tqdm import tqdm
from wanghong.utils import touch, tmap


def setup(dp_src, dp_dst):
    sample_size = 5
    # df_read = pd.read_csv('/home/cchen/Dropbox/streaming/video_types2.csv', header=None, dtype=str)
    # read = set(df_read[1].to_list())
    df_read2 = pd.read_csv('/home/cchen/data/wanghong/yizhibo_transcript.csv', dtype=str)
    df_read2 = df_read2.loc[df_read2['transcript'].apply(lambda x: '淘宝' in x or '号链接' in x)]
    df_read2['se'] = df_read2.apply(lambda x: x['start'] + '_' + x['end'], axis=1)
    df_read2 = df_read2.groupby(['Yizhibo_UID', 'Yizhibo_VID']).agg({'se': set}).reset_index()
    df_read2['uv'] = df_read2.apply(lambda x: os.path.join(x['Yizhibo_UID'][2:], x['Yizhibo_VID'][2:]), axis=1)
    read2 = dict(zip(df_read2['uv'], df_read2['se']))

    map = pd.read_csv('/home/cchen/data/wanghong/uids.csv')
    yids = map['Yizhibo_UID'].to_list()
    sids = map['Taobao_SID'].to_list()
    map = dict(zip(sids, yids))
    df_read = pd.read_csv('/home/cchen/data/wanghong/taobao_shops.csv', dtype=str)
    df_read = df_read.loc[df_read['category_manual'].isin(
        {'clothes', 'cosmetics', 'shoe', 'jewelry', 'trinket', 'gift'})]
    #, 'accessories', 'bag', 'tea', 'food'
    read = {map[sid][2:] for sid in df_read['Taobao_SID'].tolist() if sid in map}

    for fp in iglob(os.path.join(dp_src, '*', '*')):
        uid_vid = os.path.relpath(fp, dp_src)
        uid, vid = uid_vid.split(os.path.sep, 1)
        if uid not in read:
            continue
        ses_src = {os.path.splitext(sefile)[0] for sefile in os.listdir(os.path.join(dp_src, uid_vid))
                   if sefile.endswith('.zip')}
        if sample_size > len(ses_src):
            continue
        os.makedirs(os.path.join(dp_dst, uid_vid), exist_ok=True)
        ses_dst = {os.path.splitext(sefile)[0] for sefile in os.listdir(os.path.join(dp_dst, uid_vid))
                   if sefile.endswith('.npz') and not os.path.exists(sefile.replace('.npz', '.run'))}
        ses = read2.get(uid_vid, set()) & ses_src
        ses_out = ses - ses_dst
        if len(ses) < sample_size:
            if len(ses_dst - (ses_src - ses)) < sample_size - len(ses):
                ses_out |= set(random.sample(ses_src - ses - ses_dst, max(0, sample_size - len(ses) - len(ses_dst - ses))))
            else:
                continue
        elif len(ses_dst & ses) < sample_size:
            ses_out = set(random.sample(ses_out, sample_size - len(ses_dst & ses)))
        else:
            continue
        for se in ses_out:
            yield os.path.join(uid_vid, se)


    # df_read = pd.read_csv('/home/cchen/Dropbox/streaming/video_types2.csv', header=None, dtype=str)
    # read = set((df_read[0] + os.path.sep + df_read[1]).to_list())
    # for fp in tqdm(iglob(os.path.join(dp_src, '*', '*', '*.zip'))):
    #     uid_vid_se, _ = os.path.splitext(os.path.relpath(fp, start=dp_src))
    #     uid, vid, start_end = uid_vid_se.split(os.path.sep, 2)
    #     # if uid not in read:
    #     #     continue
    #
    #     if os.path.exists(os.path.join(dp_dst, uid_vid_se + '.run')) \
    #             or not os.path.exists(os.path.join(dp_dst, uid_vid_se + '.npz')):
    #         os.makedirs(os.path.join(dp_dst, uid, vid), exist_ok=True)
    #         yield uid_vid_se


def build():
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    global net
    net = inception_resnet_v2.InceptionResNetV2(include_top=False, weights='imagenet', pooling='max')


def img2emb(uid_vid_se, dp_src, dp_dst):
    fp_src = os.path.join(dp_src, uid_vid_se + '.zip')
    fp_dst = os.path.join(dp_dst, uid_vid_se + '.npz')
    fp_run = os.path.join(dp_dst, uid_vid_se + '.run')

    touch(fp_run)
    a = time.time()
    images = load_images(fp_src)
    if len(images) == 0:
        return uid_vid_se + '\tno score', False
    b = time.time()
    keys, imgs = zip(*images.items())
    batch = inception_resnet_v2.preprocess_input(np.array(imgs))
    d = time.time()
    pred = net.predict(batch)
    e = time.time()
    scores = dict(zip(keys, pred))
    np.savez(fp_dst, **scores)
    os.remove(fp_run)
    return uid_vid_se + '  {:.2f} {:.2f}'.format(b-a, e-d), True


def load_images(filepath):
    size = (299, 299)
    every_n_frames = 8
    out = {}
    try:
        with ZipFile(filepath) as zipi:
            zipnames = zipi.namelist()
            names = [f'{idx * every_n_frames + 4:05d}.jpg' for idx in range(len(zipnames) // every_n_frames)]
            for iname in names:
                start_end, _ = os.path.splitext(iname)
                img = Image.open(zipi.open(iname))
                img = np.array(img)
                img_resize = cv2.resize(img, size)
                img_center = cv2.resize(center_crop(img), size)
                img_mirror = cv2.flip(img_resize, 1)
                out.update({
                    start_end: np.asarray(img_resize, dtype=np.float32),
                    start_end + '.c': np.asarray(img_center, dtype=np.float32),
                    start_end + '.m': np.asarray(img_mirror, dtype=np.float32),
                })
        return out
    except BadZipFile:
        return {}


def center_crop(img):
    size = img.shape
    if size[0] < size[1]:
        offset = (size[1] - size[0]) // 2
        return img[:, offset: offset + size[0]]
    else:
        offset = (size[0] - size[1]) // 2
        return img[offset: offset + size[1], :]


if __name__ == '__main__':
    import random

    dp_img = '/home/cchen/data/nosilence_20to30s/img'
    dp_emb = '/mnt/nvme/yizhibo/nosilence_20to30s/inception_resnet_v2'
    build()


    def load_name(fp):
        with open(fp, 'r') as i:
            return [line.strip() for line in i]
    names = load_name('/home/cchen/Dropbox/projects/wanghong/video/mmml/uvse_train.txt') \
           + load_name('/home/cchen/Dropbox/projects/wanghong/video/mmml/uvse_test.txt')
    target_list = []
    for line in names:
        uv, clips = line.split('\t')
        for clip in clips.split('|'):
            if os.path.exists(os.path.join(dp_emb, uv, clip)):
                continue
            else:
                target_list.append(os.path.join(uv, os.path.splitext(clip)[0]))

    # target_list = list(setup(dp_img, dp_emb))
    target_list = random.sample(target_list, len(target_list))
    target_func = partial(img2emb, dp_src=dp_img, dp_dst=dp_emb)
    tmap(target_func, target_list)
