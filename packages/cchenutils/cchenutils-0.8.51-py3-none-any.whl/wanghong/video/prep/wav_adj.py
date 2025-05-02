# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/21/20
# @File  : [wanghong] wav_adj.py


import os
from functools import partial
from glob import iglob

import pandas as pd
from wanghong.utils import DATA_DIR
from wanghong.utils import qmap, write_csv_1d
from wanghong.video.audio import get_duration


def setup(dp_src, fp_dst):
    uid_vids = set(os.path.relpath(fp, dp_src).rsplit('.', 1)[0] for fp in iglob(os.path.join(dp_src, '*', '*.wav')))
    if os.path.exists(fp_dst):
        df_wavadj = pd.read_csv(fp_dst, dtype=str,
                                names=['Yizhibo_UID', 'Yizhibo_VID', 'duration', 'duration_'])
        uid_vids -= set((df_wavadj['Yizhibo_UID'].apply(lambda x: x[2:]) + os.path.sep
                    + df_wavadj['Yizhibo_VID'].apply(lambda x: x[2:])).to_list())
    return uid_vids


def wav_adjust(uid_vid, dp_src, dp_full):
    uid, vid = os.path.split(uid_vid)
    duration = get_duration(os.path.join(dp_full, uid_vid + '.ts'))
    duration_ = get_duration(os.path.join(dp_src, uid_vid + '.wav'))
    return uid_vid, ['YU' + uid, 'YV' + vid, duration, duration_]


if __name__ == '__main__':
    dp_wav = '/media/cchen/exec/yizhibo/pcm_s16le'
    dp_wav_full = '/media/cchen/data/yizhibo/pcm_s16le'
    fp_dst = os.path.join(DATA_DIR, 'wav_adj.csv')

    target_list = setup(dp_wav, fp_dst)
    target_func = partial(wav_adjust, dp_src=dp_wav, dp_full=dp_wav_full)
    listen_func = partial(write_csv_1d, fp=fp_dst)
    qmap(target_func, target_list, listen_func, n=32)
