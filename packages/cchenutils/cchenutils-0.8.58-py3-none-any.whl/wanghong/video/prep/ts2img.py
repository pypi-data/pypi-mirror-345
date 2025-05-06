# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/21/20
# @File  : [wanghong] ts2img.py


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
    # df_read = pd.read_csv('/home/cchen/Dropbox/streaming/video_types2.csv', header=None, dtype=str)
    # read = set((df_read[0]).to_list())
    # df_read = pd.read_csv('/home/cchen/data/wanghong/yizhibo_transcript.csv')\
    #     .groupby('Yizhibo_VID').agg({'transcript': ''.join}).reset_index()
    # df_read = df_read.loc[df_read['transcript'].apply(lambda x: '淘宝' in x or '号链接' in x)]
    # read = set(df_read['Yizhibo_VID'].apply(lambda x: x[2:]).to_list())
    map = pd.read_csv('/home/cchen/data/wanghong/uids.csv')
    yids = map['Yizhibo_UID'].to_list()
    sids = map['Taobao_SID'].to_list()
    map = dict(zip(sids, yids))
    df_read = pd.read_csv('/home/cchen/data/wanghong/taobao_shops.csv', dtype=str)
    df_read = df_read.loc[df_read['category_manual'].isin({'clothes'})]
    #, 'accessories', 'bag', 'tea', 'food', 'cosmetics', 'shoe', 'jewelry', 'trinket', 'gift'
    read = {map[sid][2:] for sid in df_read['Taobao_SID'].tolist() if sid in map}

    for fp in tqdm(iglob(os.path.join(dp_src, '*', '*'))):
        uid_vid, _ = os.path.splitext(os.path.relpath(fp, dp_src))
        uid, vid = os.path.split(uid_vid)
        if vid not in read:
            continue
        os.makedirs(os.path.join(dp_dst, uid_vid), exist_ok=True)
        ses_src = {os.path.splitext(sefile)[0] for sefile in os.listdir(os.path.join(dp_src, uid_vid))}
        ses_dst = {os.path.splitext(sefile)[0] for sefile in os.listdir(os.path.join(dp_dst, uid_vid))
                   if sefile.endswith('.zip') and
                   not os.path.exists(os.path.join(dp_dst, uid_vid, os.path.splitext(sefile)[0] + '.run'))}
        ses = random.sample(ses_src - ses_dst, max(0, min(len(ses_src), 5) - len(ses_dst)))
        for se in ses:
            yield os.path.join(uid_vid, se)


def ts2img(uid_vid_se, dp_src, dp_dst):
    fp_src = os.path.join(dp_src, uid_vid_se + '.ts')
    fp_dst = os.path.join(dp_dst, uid_vid_se + '.zip')
    fp_run = os.path.join(dp_dst, uid_vid_se + '.run')
    fp_err = os.path.join(dp_dst, uid_vid_se + '.err')
    dp_tmp = os.path.join(dp_dst, uid_vid_se + '_tmp')

    # cmd = f'mkdir -p {dp_tmp} ' \
    #       f'&& ffmpeg -i {fp_src} -vsync 2 -q:v 2 -filter:v scale=299:-1 {dp_tmp}/%05d.jpg ' \
    #       f'&& zip -{ZIP_DEFLATED} -qq -j {fp_dst} {dp_tmp}/* ' \
    #       f'&& rm -r {dp_tmp}'
    cmd = f'mkdir -p {dp_tmp} ' \
          f'&& ffmpeg -i {fp_src} -vsync 2 {dp_tmp}/%05d.jpg ' \
          f'&& zip -{ZIP_DEFLATED} -qq -j {fp_dst} {dp_tmp}/* ' \
          f'&& rm -r {dp_tmp}'
    try:
        touch(fp_run, cmd)
        call(cmd, print_cmd=False, )
        os.remove(fp_run)
        return uid_vid_se, True
    except Exception as e:
        touch(fp_err, str(e.args))
        os.remove(fp_run)
        return uid_vid_se + ' err', False


def cleanup(dp_dst):
    for fp in iglob(os.path.join(dp_dst, '*', '*', '*_tmp')):
        shutil.rmtree(fp)


if __name__ == '__main__':

    dp_tssegs = '/media/cchen/exec/yizhibo/nosilence_20to30s/ts'
    dp_imgs = '/mnt/sdb/nosilence_20to30s/img'

    target_list = list(setup(dp_tssegs, dp_imgs))
    target_list = random.sample(target_list, len(target_list))
    target_func = partial(ts2img, dp_src=dp_tssegs, dp_dst=dp_imgs)

    mmap(target_func, target_list, n=12)
    cleanup(dp_imgs)
