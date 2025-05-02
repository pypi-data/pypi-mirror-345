# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/20/20
# @File  : [wanghong] ts_split.py

import os
import pandas as pd
from functools import partial
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from tqdm import tqdm
from wanghong.utils import touch, mmap
from wanghong.utils import DATA_DIR


def setup(fp_segs, dp_dst):
    df_segs = pd.read_csv(fp_segs, dtype=str)
    df_segs['uid'] = df_segs['Yizhibo_UID'].apply(lambda x: x[2:])
    df_segs['vid'] = df_segs['Yizhibo_VID'].apply(lambda x: x[2:])
    df_segs = df_segs.loc[df_segs['end'].apply(float) - df_segs['start'].apply(float) > 5]
    paths = df_segs['uid'] + os.path.sep + df_segs['vid'] + os.path.sep + df_segs['start'] + '_' + df_segs['end']
    with tqdm(paths.to_list(), desc='setup') as bar:
        for uid_vid_se in bar:
            uid_vid, _ = os.path.split(uid_vid_se)
            if os.path.exists(os.path.join(dp_dst, uid_vid_se + '.ts')) \
                    and not os.path.exists(os.path.join(dp_dst, uid_vid_se + '.run')):
                continue
            os.makedirs(os.path.join(dp_dst, uid_vid), exist_ok=True)
            if os.path.exists(os.path.join(dp_dst, uid_vid_se + '.ts')):
                os.remove(os.path.join(dp_dst, uid_vid_se + '.ts'))
            yield uid_vid_se


def ts_split(uid_vid_se, dp_src, dp_dst):
    uid_vid, start_end = os.path.split(uid_vid_se)
    uid, vid = uid_vid.split(os.path.sep)
    start, end = start_end.split('_')
    start = float(start)
    end = float(end)

    fp_src = os.path.join(dp_src, uid_vid + '.ts')
    fp_dst = os.path.join(dp_dst, uid_vid, start_end + '.ts')
    fp_run = os.path.join(dp_dst, uid_vid, start_end + '.run')
    fp_err = os.path.join(dp_dst, uid_vid, start_end + '.err')

    ratio = vid_ratio['YV' + vid]
    if ratio > 1:
        ratio = 1
        if end > vid_duration['YV' + vid]:
            return uid_vid, False
    elif ratio < 0.9:
        return uid_vid, False

    touch(fp_run)
    try:
        ffmpeg_extract_subclip(fp_src, start * ratio, end * ratio, fp_dst, logger=None)
        os.remove(fp_run)
        return uid_vid_se, True
    except Exception as e:
        touch(fp_err, str(e.args))
        return uid_vid + ' err', False


##
if __name__ == '__main__':
    fp_segs = os.path.join(DATA_DIR, 'yizhibo_transcript.csv')
    dp_ts = '/media/cchen/data/yizhibo/ts/'
    dp_tssegs = '/media/cchen/exec/yizhibo/nosilence_20to30s/ts/'

    df_wavadj = pd.read_csv(os.path.join(DATA_DIR, 'wav_adj.csv'))
    df_wavadj['ratio'] = df_wavadj.apply(lambda x: x['duration_'] / x['duration'], axis=1)
    vid_ratio = dict(zip(df_wavadj['Yizhibo_VID'].to_list(), df_wavadj['ratio'].to_list()))
    vid_duration = dict(zip(df_wavadj['Yizhibo_VID'].to_list(), df_wavadj['duration'].to_list()))

    target_list = list(setup(fp_segs, dp_tssegs))
    # target_list = random.sample(target_list, len(target_list))
    target_func = partial(ts_split, dp_src=dp_ts, dp_dst=dp_tssegs)

    mmap(target_func, target_list, n=32)

    #'/media/cchen/data/yizhibo/ts/31385947/QFpUQoWz-WfD_b1K.ts'
##

