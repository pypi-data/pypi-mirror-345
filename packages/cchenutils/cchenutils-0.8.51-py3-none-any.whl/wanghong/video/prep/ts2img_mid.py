# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/28/20
# @File  : [wanghong] ts2img_mid.py



import os
import random
import shutil
from functools import partial
from glob import iglob
from zipfile import ZIP_DEFLATED

import pandas as pd
from tqdm import tqdm
from wanghong.utils import touch, call, mmap


def setup(dp_src, dp_dst):
    # with open('/home/cchen/data/tmp.lst') as i:
    #     lst = {line.strip() for line in i}
    # df_read = pd.read_csv('/home/cchen/Dropbox/streaming/video_types2.csv', header=None, dtype=str)
    # read = set((df_read[0] + os.path.sep + df_read[1]).to_list())
    df_read = pd.read_csv('/home/cchen/data/wanghong/yizhibo_transcript.csv') \
        .groupby('Yizhibo_UID').agg({'transcript': ''.join}).reset_index()
    df_read = df_read.loc[df_read['transcript'].apply(lambda x: '淘宝' in x)]
    read = set(df_read['Yizhibo_UID'].apply(lambda x: x[2:]).to_list())

    for fp in tqdm(iglob(os.path.join(dp_src, '*', '*'))):
        uid_vid, _ = os.path.splitext(os.path.relpath(fp, dp_src))
        uid, _ = os.path.split(uid_vid)
        if uid not in read:
            continue
        os.makedirs(os.path.join(dp_dst, uid_vid), exist_ok=True)
        ses_src = {os.path.splitext(sefile)[0] for sefile in os.listdir(os.path.join(dp_src, uid_vid))}
        ses_dst = {os.path.splitext(sefile)[0] for sefile in os.listdir(os.path.join(dp_dst, uid_vid))
                   if sefile.endswith('.jpg') and
                   not os.path.exists(os.path.join(dp_dst, uid_vid, sefile.replace('.jpg', '.run')))}
        for se in ses_src - ses_dst:
            yield os.path.join(uid_vid, se)


def ts2img_mid(uid_vid_se, dp_src, dp_dst):
    fp_src = os.path.join(dp_src, uid_vid_se + '.ts')
    fp_dst = os.path.join(dp_dst, uid_vid_se + '.jpg')
    fp_run = os.path.join(dp_dst, uid_vid_se + '.run')
    fp_err = os.path.join(dp_dst, uid_vid_se + '.err')

    uid_vid, se = os.path.split(uid_vid_se)
    start, end = se.split('_')
    middle = int((float(end) - float(start)) / 2)
    cmd = f'ffmpeg -ss {middle} -i {fp_src} -vframes 1 {fp_dst} -y'
    try:
        touch(fp_run, cmd)
        call(cmd, print_cmd=False, )
        os.remove(fp_run)
        return uid_vid_se, True
    except Exception as e:
        touch(fp_err, str(e.args))
        return uid_vid_se + ' err', False


def cleanup(dp_dst):
    for fp in iglob(os.path.join(dp_dst, '*', '*', '*.jpg')):
        if os.path.getsize(fp) == 0:
            os.remove(fp)
            print(fp)


if __name__ == '__main__':

    dp_tssegs = '/media/cchen/exec/yizhibo/nosilence_20to30s/ts'
    dp_imgs = '/home/cchen/data/nosilence_20to30s/img_sample'

    target_list = list(setup(dp_tssegs, dp_imgs))
    target_list = random.sample(target_list, len(target_list))
    target_func = partial(ts2img_mid, dp_src=dp_tssegs, dp_dst=dp_imgs)

    mmap(target_func, target_list, n=5)
    cleanup(dp_imgs)