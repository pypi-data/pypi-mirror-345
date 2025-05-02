# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/27/20
# @File  : [wanghong] ts2wav.py


import os
from functools import partial
from glob import glob

import timeout_decorator
from tqdm import tqdm

from utils import call, touch, mmap


def setup(src_dir, dst_dir):
    print('Building structure for ts2wav...')
    for uid in tqdm(os.listdir(src_dir)):
        for vfile in os.listdir(os.path.join(src_dir, uid)):
            vid, _ = os.path.splitext(vfile)
            os.makedirs(os.path.join(dst_dir, uid), exist_ok=True)
            if os.path.exists(os.path.join(dst_dir, uid, vid + '.run')) \
                    or not os.path.exists(os.path.join(dst_dir, uid, vid + '.wav')):
                # if not os.path.exists(os.path.join(dst_dir, uid, vid + '.tmo')):
                yield os.path.join(uid, vid)


@timeout_decorator.timeout(10 * 60)
def ts2wav(uid_vid, src_dir, dst_dir, **kwargs):
    # print(uid_vid, sep = '\t')
    fp_src = os.path.join(src_dir, uid_vid + '.ts')
    fp_dst = os.path.join(dst_dir, uid_vid + '.wav')
    fp_run = os.path.join(dst_dir, uid_vid + '.run')
    fp_tmo = os.path.join(dst_dir, uid_vid + '.tmo')
    touch(fp_run)
    try:
        # with VideoFileClip(fp_src) as clip:
        #     clip.audio.write_audiofile(fp_dst,
        #                                fps=16000, nbytes=2, ffmpeg_params=['-ac', '1'],
        #                                verbose=False, logger=kwargs.get('logger'))  # pcm_s16le
        call('ffmpeg -i {} -acodec pcm_s16le -ac 1 -ar 16000 {} -y'.format(fp_src, fp_dst), print_cmd=False)
        os.remove(fp_run)
        if os.path.exists(fp_tmo):
            os.remove(fp_tmo)
        return uid_vid, True
    except (timeout_decorator.timeout_decorator.TimeoutError, KeyboardInterrupt):
        touch(fp_tmo)
        return uid_vid + ' timeout.', False
    except Exception as e:
        touch(os.path.join(dst_dir, uid_vid + '.err'), str(e.args))
        return uid_vid + ' error.', False


def cleanup(dst_dir):
    print('Cleaning up for ts2wav...')
    for uid in tqdm(os.listdir(dst_dir)):
        for vfile in os.listdir(os.path.join(dst_dir, uid)):
            vid, ext = os.path.splitext(vfile)
            fp_dst = os.path.join(dst_dir, uid, vid + '.wav')
            fp_run = os.path.join(dst_dir, uid, vid + '.run')
            fp_err = os.path.join(dst_dir, uid, vid + '.err')
            fp_tmo = os.path.join(dst_dir, uid, vid + '.tmo')
            if ext == '.run' and (os.path.exists(fp_tmo) or os.path.exists(fp_err)) and os.path.exists(fp_dst):
                os.remove(fp_run)
                os.remove(fp_dst)

def get_duration(fp):
    try:
        out = call('ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {}'.format(fp),
                   print_cmd=False)
        return float(out.strip())
    except ValueError:
        return None


def check_length():
    out = []
    for fp_ts in tqdm(glob('/media/cchen/data/yizhibo/ts/*/*.ts')):
        fp_wav = fp_ts.replace('/ts/', '/pcm_s16le/').replace('.ts', '.wav').replace('/data/', '/exec/')
        if not os.path.exists(fp_wav):
            continue
        ts_len = get_duration(fp_ts)
        wav_len = get_duration(fp_wav)
        if abs(wav_len - ts_len) > 1:
            out.append((wav_len, ts_len, fp_ts))
    return out


if __name__ == '__main__':
    ts_dir = '/media/cchen/data/yizhibo/ts/'
    wav_dir = '/media/cchen/data/yizhibo/pcm_s16le/'
    target_list = list(setup(ts_dir, wav_dir))
    # target_list = random.sample(target_list, len(target_list))
    target_func = partial(ts2wav, src_dir=ts_dir, dst_dir=wav_dir, logger='bar')
    # for it in target_list:
    #     target_func(it)
    mmap(target_func, target_list, n=2)
    # cleanup(wav_dir)
    #
    # out = []
    # dst_dir = wav_dir
    # for uid in os.listdir(dst_dir):
    #     for vfile in os.listdir(os.path.join(dst_dir, uid)):
    #         vid, ext = os.path.splitext(vfile)
    #         fp_dst = os.path.join(dst_dir, uid, vid + '.wav')
    #         fp_run = os.path.join(dst_dir, uid, vid + '.run')
    #         fp_err = os.path.join(dst_dir, uid, vid + '.error')
    #         fp_tmo = os.path.join(dst_dir, uid, vid + '.timeout')
    #         if ext == '.run' and (os.path.exists(fp_tmo) or os.path.exists(fp_err)):
    #             out.append((uid, vid))
    # with open('redown.txt', 'w') as o:
    #     for uid, vid in out:
    #         o.write(uid + '\t' + vid + '\n')

    # uid_vid = '265814325/247HjMwmgdH4j4UR'
    # ts2wav(uid_vid, ts_dir, wav_dir, logger='bar')
    # clip.audio.write_audiofile(os.path.join(wav_dir, uid_vid + '.wav'), fps=16000, nbytes=2, ffmpeg_params=['-ac', '1', '-timeout'])  # pcm_s16le
