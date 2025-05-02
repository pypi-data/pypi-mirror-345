# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/25/20
# @File  : [wanghong] inceptionv3_cv2.py


# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/22/20
# @File  : [wanghong] inceptionv3.py

import os
from functools import partial
from glob import iglob
from zipfile import ZipFile

import cv2
import numpy as np
import pandas as pd
from keras.applications import inception_v3
from tqdm import tqdm
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
    with ZipFile(filepath) as zipi:
        zipnames = zipi.namelist()
        for iname in zipnames:
            start_end, _ = os.path.splitext(iname)
            img = cv2.imdecode(np.frombuffer(zipi.read(iname), np.uint8), cv2.IMREAD_COLOR)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_resize = cv2.resize(img, size)
            img_center = center_crop(img_resize)
            img_mirror = cv2.flip(img_resize, 1)
            img_centermirror = cv2.flip(img_center, 1)
            out.update({
                start_end: img_resize,
                start_end + '.c': img_center,
                start_end + '.m': img_mirror,
                start_end + '.cm': img_centermirror
            })
    return out


def center_crop(img):
    size = img.shape
    if size[0] < size[1]:
        offset = (size[1] - size[0]) // 2
        return img[:, offset: offset + size[0]]
    else:
        offset = (size[0] - size[1]) // 2
        return img[offset: offset + size[1], :]


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
