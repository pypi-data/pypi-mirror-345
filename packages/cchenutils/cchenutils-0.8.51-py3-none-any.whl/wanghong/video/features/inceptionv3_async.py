# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/24/20
# @File  : [wanghong] inceptionv3_async.py


# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/22/20
# @File  : [wanghong] inceptionv3.py


import multiprocessing
import os
import pickle
import struct
from glob import iglob
from zipfile import ZipFile, BadZipFile

import cv2
import numpy as np
import pandas as pd
from PIL import Image
from keras.applications import inception_v3
from tqdm import tqdm, trange
from wanghong.utils import touch
import time

def pickle_writer(fp, obj):
    with open(fp, 'wb') as o:
        pickle.dump(obj, o)


def pickle_reader(fp):
    with open(fp, 'rb') as i:
        return pickle.load(i)


def setup(dp_src, dp_dst, model):
    df_read = pd.read_csv('/home/cchen/Dropbox/streaming/video_types2.csv', header=None, dtype=str)
    read_u1 = set(df_read[0].to_list())
    # read_uv1 = set((df_read[0] + os.path.sep + df_read[1]).to_list())
    df_read = pd.read_csv('/home/cchen/data/wanghong/yizhibo_transcript.csv') \
        .groupby('Yizhibo_UID').agg({'transcript': ''.join}).reset_index()
    df_read = df_read.loc[df_read['transcript'].apply(lambda x: '淘宝' in x)]
    read_u2 = set(df_read['Yizhibo_UID'].apply(lambda x: x[2:]).to_list())
    read_u = read_u1 | read_u2
    # for fp in tqdm(iglob(os.path.join(dp_src, '*', '*', '*.zip'))):
    #     uid_vid_se, _ = os.path.splitext(os.path.relpath(fp, start=dp_src))
    #     uid_vid, start_end = os.path.split(uid_vid_se)
    #     if uid_vid not in read:
    #         continue
    #     if os.path.exists(os.path.join(dp_dst, uid_vid_se + '_' + model + '.run')) \
    #             or not os.path.exists(os.path.join(dp_dst, uid_vid_se + '_' + model + '.npz')):
    #         os.makedirs(os.path.join(dp_dst, uid_vid), exist_ok=True)
    #         yield uid_vid_se
    sizes = []
    for fp in tqdm(iglob(os.path.join(dp_src, '*', '*'))):
        uid_vid, _ = os.path.splitext(os.path.relpath(fp, dp_src))
        uid, _ = os.path.split(uid_vid)
        if uid not in read_u:
            continue
        os.makedirs(os.path.join(dp_dst, uid_vid), exist_ok=True)
        ses_src = {os.path.splitext(sefile)[0] for sefile in os.listdir(os.path.join(dp_src, uid_vid))}
        ses_dst = {sefile.replace(f'_{model}.npz', '') for sefile in os.listdir(os.path.join(dp_dst, uid_vid))
                   if sefile.endswith(f'_{model}.npz') and
                   not os.path.exists(os.path.join(dp_dst, uid_vid, sefile.replace('.npz', '.run')))}
        size = max(0, min(len(ses_src), 10) - len(ses_dst))
        sizes.append(size)
        ses = random.sample(ses_src - ses_dst, size)
        for se in ses:
            yield os.path.join(uid_vid, se)
    print(sum(sizes) / len(sizes))
    time.sleep(5)

# def load_images(filepath, modality='inceptionv3'):
#     size = (299, 299) if modality.startswith('inceptionv3') else (224, 224)
#     out = {}
#     with ZipFile(filepath) as zipi:
#         zipnames = zipi.namelist()
#         for iname in zipnames:
#             start_end, _ = os.path.splitext(iname)
#             img = Image.open(zipi.open(iname))
#             img_resize = img.resize(size)
#             img_center = center_crop(img).resize(size)
#             img_mirror = img_resize.transpose(Image.FLIP_LEFT_RIGHT)
#             img_centermirror = img_mirror.transpose(Image.FLIP_LEFT_RIGHT)
#             out.update({
#                 start_end: np.asarray(img_resize, dtype=np.float32),
#                 start_end + '.c': np.asarray(img_center, dtype=np.float32),
#                 start_end + '.m': np.asarray(img_mirror, dtype=np.float32),
#                 start_end + '.cm': np.asarray(img_centermirror, dtype=np.float32)
#             })
#     return out
#
#
# def center_crop(img):
#     size = img.size
#     if size[0] < size[1]:
#         offset = (size[1] - size[0]) // 2
#         return img.crop((0, offset, size[0], offset + size[0]))
#     else:
#         offset = (size[0] - size[1]) // 2
#         return img.crop((offset, 0, offset + size[1], size[1]))
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


def reader(qr):
    while True:
        signal = qr.get()
        if signal == 'done':
            qe.put('done')
            break
        try:
            uid_vid_se = signal
            fp_src = os.path.join(dp_src, uid_vid_se + '.zip')
            fp_run = os.path.join(dp_dst, '{}_{}.run'.format(uid_vid_se, model))
            touch(fp_run)
            images = load_images(fp_src)
            keys, imgs = zip(*images.items())
            if images:
                try:
                    qe.put((uid_vid_se, keys, imgs))
                except struct.error:
                    pickle_writer(os.path.join(dp_dst, '{}_{}.tmp'.format(uid_vid_se, model)), (uid_vid_se, keys, imgs))
                    qe.put(uid_vid_se)
                except Exception as e:
                    print('r ' + uid_vid_se + str(e.args))
                    qn.put(True)
            else:
                qn.put(True)
        except Exception:
            qn.put(True)


def executor(qe):
    while True:
        signal = qe.get()
        if signal == 'done':
            qw.put('done')
            break
        try:
            if isinstance(signal, str):
                fp_tmp = os.path.join(dp_dst, '{}_{}.tmp'.format(signal, model))
                signal = pickle_reader(fp_tmp)
                os.remove(fp_tmp)
            uid_vid_se, keys, imgs = signal
            batch = inception_v3.preprocess_input(np.array(imgs))
            pred = net.predict(batch)
            qw.put((uid_vid_se, keys, pred))
        except Exception as e:
            print('e '+str(e.args))
            qn.put(True)


def writer(qw):
    while True:
        signal = qw.get()
        if signal == 'done':
            break
        try:
            uid_vid_se, keys, pred = signal
            scores = dict(zip(keys, pred))
            fp_dst = os.path.join(dp_dst, '{}_{}.npz'.format(uid_vid_se, model))
            fp_run = os.path.join(dp_dst, '{}_{}.run'.format(uid_vid_se, model))
            np.savez(fp_dst, **scores)
            os.remove(fp_run)
            qn.put(True)
        except Exception as e:
            print('w '+str(e.args))
            qn.put(True)


def main(qm):
    with trange(total, ncols=160) as bar:
        for _ in bar:
            uid_vid_se = qm.get()
            qr.put(uid_vid_se)
            qn.get()
            bar.set_description(uid_vid_se)


if __name__ == '__main__':
    import random

    dp_img = '/home/cchen/data/nosilence_20to30s/img'
    dp_emb = '/mnt/nvme/yizhibo/nosilence_20to30s/embeddings'
    model = 'inceptionv3'
    # tf.autograph.set_verbosity(1)

    uid_vid_ses = list(setup(dp_img, dp_emb, model=model))
    uid_vid_ses = random.sample(uid_vid_ses, len(uid_vid_ses))
    total = len(uid_vid_ses)
    # target_func = partial(img2inceptionv3, dp_src=dp_img, dp_dst=dp_emb, model=model)
    # tmap(target_func, target_list)

    dp_src = dp_img
    dp_dst = dp_emb
    model = model

    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    net = inception_v3.InceptionV3(weights='imagenet')

    manager = multiprocessing.Manager()
    qr = manager.Queue()
    qe = manager.Queue()
    qw = manager.Queue()
    qn = manager.Queue()
    qm = manager.Queue()

    for it in uid_vid_ses[1:] + ['done']:
        qm.put(it)

    pool = multiprocessing.Pool(3)
    pool.imap_unordered(main, iter([qm, ]))
    pool.imap_unordered(reader, iter([qr, ]))
    pool.imap_unordered(writer, iter([qw, ]))

    qr.put(uid_vid_ses[0])
    executor(qe)
##