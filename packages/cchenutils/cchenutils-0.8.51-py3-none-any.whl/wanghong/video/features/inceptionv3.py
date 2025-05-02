# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/22/20
# @File  : [wanghong] inceptionv3.py


import multiprocessing
import os
from functools import partial
from glob import iglob
from zipfile import ZipFile, BadZipFile

import numpy as np
import pandas as pd
from PIL import Image
from keras.applications import inception_v3
from keras.preprocessing.image import img_to_array

from tqdm import tqdm
import cv2
from wanghong.utils import touch, tmap


def setup(dp_src, dp_dst, model):
    df_read = pd.read_csv('/home/cchen/Dropbox/streaming/video_types2.csv', header=None, dtype=str)
    read = set((df_read[0] + os.path.sep + df_read[1]).to_list())
    for fp in tqdm(iglob(os.path.join(dp_src, '*', '*', '*.zip'))):
        uid_vid_se, _ = os.path.splitext(os.path.relpath(fp, start=dp_src))
        uid_vid, start_end = os.path.split(uid_vid_se)
        if uid_vid not in read:
            continue
        if os.path.exists(os.path.join(dp_dst, uid_vid_se + '_' + model + '.run')) \
                or not os.path.exists(os.path.join(dp_dst, uid_vid_se + '_' + model + '.npz')):
            os.makedirs(os.path.join(dp_dst, uid_vid), exist_ok=True)
            yield uid_vid_se


def build_model(model):
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    global net
    if model.startswith('inceptionv3'):
        net = inception_v3.InceptionV3(weights='imagenet')
    else:
        raise LookupError('Current supported model {inceptionv3, }')


def img2inceptionv3_chunk(uid_vid_ses, dp_src, dp_dst, model):
    def worker(uid_vid_se):
        fp_src = os.path.join(os.path.join(dp_src, uid_vid_se + '.zip'))
        images = load_images(fp_src)
        if len(images) == 0:
            return None, None, None
        keys, imgs = zip(*images.items())
        return [uid_vid_se] * len(keys), keys, imgs

    key_ses = []
    key_imgs = []
    val_imgs = []
    pool = multiprocessing.Pool(len(uid_vid_ses))
    for key_se, key_img, val_img in pool.map(worker, uid_vid_ses):
        if key_se:
            key_ses += key_se
            key_imgs += key_img
            val_imgs += val_img

    batch = inception_v3.preprocess_input(np.array(val_imgs))
    pred = net.predict(batch)
    scores = {}
    for uid_vid_se, key_img, score in zip(key_ses, key_imgs, pred):
        scores.setdefault(uid_vid_se, []).append((key_img, score))

    for uid_vid_se, this_scores in scores.items():
        this_scores = dict(this_scores)
        fp_dst = os.path.join(dp_dst, '{}_{}.npz'.format(uid_vid_se, model))
        np.savez(fp_dst, **this_scores)
    return uid_vid_se, True


def img2inceptionv3(uid_vid_se, dp_src, dp_dst, model):
    import time

    fp_src = os.path.join(os.path.join(dp_src, uid_vid_se + '.zip'))
    fp_dst = os.path.join(dp_dst, '{}_{}.npz'.format(uid_vid_se, model))
    fp_run = os.path.join(dp_dst, '{}_{}.run'.format(uid_vid_se, model))

    touch(fp_run)
    a = time.time()
    images = load_images(fp_src)
    if len(images) == 0:
        return uid_vid_se + '\tno score', False
    b = time.time()
    keys, imgs = zip(*images.items())
    c = time.time()
    batch = inception_v3.preprocess_input(np.array(imgs))
    d = time.time()
    pred = net.predict(batch)
    e = time.time()
    scores = dict(zip(keys, pred))
    f = time.time()
    np.savez(fp_dst, **scores)
    os.remove(fp_run)
    return uid_vid_se + '  {:.2f} {:.2f} {:.2f} {:.2f} {:.2f}'.format(b-a,c-b,d-c,e-d,f-e), True


def load_images(filepath, modality='inceptionv3'):
    size = (299, 299) if modality.startswith('inceptionv3') else (224, 224)
    out = {}
    try:
        with ZipFile(filepath) as zipi:
            zipnames = zipi.namelist()
            for iname in zipnames:
                start_end, _ = os.path.splitext(iname)
                img = Image.open(zipi.open(iname))
                img = np.array(img)
                img_resize = cv2.resize(img, size)
                img_center = cv2.resize(center_crop(img), size)
                img_mirror = cv2.flip(img_resize, 1)
                img_centermirror = cv2.flip(img_center, 1)
                out.update({
                    start_end: np.asarray(img_resize, dtype=np.float32),
                    start_end + '.c': np.asarray(img_center, dtype=np.float32),
                    start_end + '.m': np.asarray(img_mirror, dtype=np.float32),
                    start_end + '.cm': np.asarray(img_centermirror, dtype=np.float32)
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

# def center_crop(img):
#     size = img.size
#     if size[0] < size[1]:
#         offset = (size[1] - size[0]) // 2
#         return img.crop((0, offset, size[0], offset + size[0]))
#     else:
#         offset = (size[0] - size[1]) // 2
#         return img.crop((offset, 0, offset + size[1], size[1]))


def chunk(iter, n):
    is_continue = True
    while is_continue:
        out = []
        for _ in range(n):
            try:
                it = next(iter)
                out.append(it)
            except StopIteration:
                is_continue = False
        yield out


if __name__ == '__main__':
    import random

    dp_img = '/home/cchen/data/nosilence_20to30s/img'
    dp_emb = '/mnt/sdb/nosilence_20to30s/embeddings'
    model = 'inceptionv3'
    build_model(model)

    target_list = list(setup(dp_img, dp_emb, model=model))
    target_list = random.sample(target_list, len(target_list))
    target_func = partial(img2inceptionv3, dp_src=dp_img, dp_dst=dp_emb, model=model)
    tmap(target_func, target_list)
