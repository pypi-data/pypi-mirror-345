# !/usr/bin/env python37
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/26/20
# @File  : [wanghong] wav_split.py

import os
import time
from functools import partial
from io import BytesIO
from typing import List, Tuple
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

import numpy as np
from tqdm import tqdm

from utils import mmap, touch
from video.audio import Audio


def write_segments_zip(filepath: str, segments: List[Tuple[float, float, Audio]]):
    if not segments:
        return False
    with ZipFile(filepath, 'w') as zipo:
        for start, end, audio in segments:
            buffered = BytesIO()
            audio.export(buffered, format='wav')
            info = ZipInfo(f'{start:.2f}_{end:.2f}.wav', date_time=time.localtime(time.time()))
            info.compress_type = ZIP_DEFLATED
            info.create_system = 0
            zipo.writestr(info, buffered.getvalue())
        return True


def read_segments_zip(filepath: str):
    with ZipFile(filepath, 'r') as zipi:
        filenames = zipi.namelist()
        return {filename: zipi.open(filename).read() for filename in filenames}


def setup(dp_src, dp_dst):
    print('Building structure for wav_split...')
    for uid in tqdm(os.listdir(dp_src)):
        for vfile in os.listdir(os.path.join(dp_src, uid)):
            vid, ext = os.path.splitext(vfile)
            if ext != '.wav':
                continue
            os.makedirs(os.path.join(dp_dst, uid), exist_ok=True)
            if os.path.exists(os.path.join(dp_dst, uid, vid + '.run')) \
                    or not os.path.exists(os.path.join(dp_dst, uid, vid + '.zip')):
                if os.path.exists(os.path.join(dp_dst, uid, vid + '.nsg')) \
                        or os.path.exists(os.path.join(dp_dst, uid, vid + '.err')):
                    continue
                if not os.path.exists(os.path.join(dp_src, uid, vid + '.run')):
                    yield os.path.join(uid, vid)


def split_wav(uid_vid, dp_src, dp_dst):
    fp_src = os.path.join(dp_src, uid_vid + '.wav')
    fp_dst = os.path.join(dp_dst, uid_vid + '.zip')
    fp_run = os.path.join(dp_dst, uid_vid + '.run')
    fp_err = os.path.join(dp_dst, uid_vid + '.err')
    fp_nsg = os.path.join(dp_dst, uid_vid + '.nsg')
    touch(fp_run)
    try:
        segs = Audio.from_file(fp_src).remove_silence(0.020, 0.020, smooth_window=1, weight=0.3)
        if write_segments_zip(fp_dst, segs):
            os.remove(fp_run)
            return uid_vid, True
        else:
            touch(fp_nsg)
            return uid_vid + ' no seg', False
    except FloatingPointError:
        touch(fp_nsg)
        return uid_vid + ' err', False
    except Exception as e:
        touch(fp_err, str(e.args))
        return uid_vid + ' err', False


if __name__ == '__main__':
    import random

    np.seterr(all='raise')

    dp_wav = '/media/cchen/exec/yizhibo/pcm_s16le/'
    dp_noslience = '/media/cchen/exec/yizhibo/pcm_s16le_nosilence_20to30s/'

    target_list = list(setup(dp_wav, dp_noslience))
    target_list = random.sample(target_list, len(target_list))
    target_func = partial(split_wav, dp_src=dp_wav, dp_dst=dp_noslience)
    mmap(target_func, target_list, n=4)

    # uid_vid = '219586045/MP3ZjAvNZMV6tDvq'
    # uid_vid='303166714/sz1HXKSNNMxmZfw4'
