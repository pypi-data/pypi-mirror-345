# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/29/20
# @File  : [wanghong] wav2speech.py


import os
import time
from ctypes import Structure, c_char_p
from functools import partial
from io import BytesIO
from multiprocessing import Array
from typing import Dict
from zipfile import ZipFile

import pandas as pd
import requests
from tqdm import tqdm

from video.audio import Audio
from utils import qmap, write_csv_1d
from aip import AipSpeech
from opts import DATA_DIR


def setup(fp_src, fp_dst, vid_start=None, vid_until=None):
    df_wavinfo = pd.read_csv(fp_src, dtype={'uid': str})
    df_wavinfo = df_wavinfo.loc[df_wavinfo['vad2'] >= 0.5]
    df_wavinfo = df_wavinfo.loc[df_wavinfo['duration'] > 0.5]
    df_wavinfo = df_wavinfo.reset_index()

    if vid_start:
        idx_start = df_wavinfo['vid'].to_list().index(vid_start)
        df_wavinfo = df_wavinfo.loc[idx_start:].reset_index()
    if vid_until:
        idx_until = df_wavinfo['vid'].to_list().index(vid_until)
        df_wavinfo = df_wavinfo.loc[:idx_until-1].reset_index()

    read = read_transcript(fp_dst)
    df_wavinfo['out'] = df_wavinfo['uid'] + '/' + df_wavinfo['vid'] + '/' + \
                        df_wavinfo['start'].apply(lambda x: '{:.2f}'.format(x)) + '_' + \
                        df_wavinfo['end'].apply(lambda x: '{:.2f}'.format(x)) + '.wav'
    return df_wavinfo['out'].loc[~df_wavinfo['out'].isin(read)].tolist()
    # for _, row in df_wavinfo.iterrows():
    #     uid = row['uid']
    #     vid = row['vid']
    #     start = '{:.2f}'.format(row['start'])
    #     end = '{:.2f}'.format(row['end'])
    #     wavfile = start + '_' + end + '.wav'
    #     if '@_@'.join((uid, vid, start, end)) not in read:
    #         yield os.path.join(uid, vid, wavfile)


def read_zip_names(filepath: str):
    with ZipFile(filepath) as zipi:
        return zipi.namelist()


def read_audios_zip(filepath: str) -> Dict[str, Audio]:
    with ZipFile(filepath, 'r') as zipi:
        filenames = zipi.namelist()
        return {filename: Audio.from_file(BytesIO(zipi.open(filename).read())) for filename in filenames}


def read_audio_zip(filepath: str, filename: str) -> Audio or None:
    with ZipFile(filepath, 'r') as zipi:
        filenames = set(zipi.namelist())
        if filename not in filenames:
            return None
        buff = BytesIO(zipi.open(filename).read())
        return Audio.from_file(buff)


def read_transcript(fp):
    try:
        df = pd.read_csv(fp, header=None, dtype=str)
        return set((df[0] + '/' + df[1] + '/' + df[2] + '_' + df[3] + '.wav').to_list())
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return set()


def translate(uid_vid_wavfile, dp_src):
    uid_vid, wavfile = os.path.split(uid_vid_wavfile)
    if not os.path.exists(os.path.join(dp_src, uid_vid + '.zip')):
        return uid_vid_wavfile + ' not found.', []
    wav = read_audio_zip(os.path.join(dp_src, uid_vid + '.zip'), filename=wavfile)

    # APP_ID, API_KEY, SECRET_KEY
    global counter
    global tokens

    ctr = counter.value
    counter.increment()
    # token = tokens.nextappend()
    i_token = ctr % len(tokens)

    uid, vid = os.path.split(uid_vid)
    start_end, _ = os.path.splitext(wavfile)
    start, end = start_end.split('_')

    buff = BytesIO()
    wav.export(buff, format='wav')
    wavbytes = buff.getvalue()


    for _ in range(5):
        try:
            # token_l = tokens.pop(i_token)
            # token_l = tokens[i_token]
            token = tokens[i_token]
            # token = tokens.popappend(i_token)
            # print(token.note)
            APP_ID = token.APP_ID
            API_KEY = token.API_KEY
            SECRET_KEY = token.SECRET_KEY
            client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

            res = client.asr(wavbytes, 'wav', 16000, {'dev_pid': 1537, })
            error = res.get('err_msg', '')
            status = res.get('err_no', 0)
            if status in {3302, 3305}:
                print(token.note, 'deleted.')
                tokens.pop(i_token)
                i_token = ctr % len(tokens)

            if '__json_decode_error' in res and not error:
                time.sleep(1)
                continue

            errcode = res.get('error_code', '')
            if errcode == 'SDK108' or error == 'request qps too much':
                time.sleep(10)
                continue
            content = res.get('result', u'')
            if content:
                content = content[0]
            # tokens.append(token_l)
            return str(ctr) + '\t' + uid_vid_wavfile, [uid, vid, start, end, error, errcode, status, content]
        except requests.exceptions.ConnectionError:
            time.sleep(5)
            continue
        except Exception as e:
            # tokens.append(token_l)
            return str(ctr) + '\t' + uid_vid_wavfile + ' err', [uid, vid, start, end, str(e.args), '224', '', '']
    # tokens.append(token_l)
    return str(ctr) + '\t' + uid_vid_wavfile + ' ConnectionError', []


class BaiduAPIToken(Structure):
    _fields_ = [
        ('APP_ID', c_char_p),
        ('API_KEY', c_char_p),
        ('SECRET_KEY', c_char_p),
        ('note', c_char_p)
    ]


class BaiduAPITokens(object):
    tokens = [
        (b'18647851', b'kbXmV1zz5mfTVSrcXx4Se8QD', b'md4IyCfGd3MqM4aPGP4shoGpnHCkrgch', b'2028475117'),
        # (b'18652651', b'rEZAFWFWAjf0s3WGN2TQjSp7', b'GlIOId4siYAZlNXi8SQZ4CnGL4Uxzkig', b'Keran'),
        (b'18662402', b'wjxUOGDynBWhIQzY25XIRUhD', b'QQ5VatnusUSPQXcwy7lPaBezwhqMdReb', b'2025945117'),
        (b'18693660', b'C1oerSWAcA3j1VKS9DPq2qza', b'M8XuxgGQtaQ9STfwHaSoH52blMsY5o8D', b'Pankhuri'),
        (b'18693675', b'lFWDB1eLKDon03a7w9HjvWe4', b'CS0z9LD1lo2cc4s4mc30Vt0rKkGvP2Ld', b'Afnan'),
        (b'18789611', b'0FxhZfb93pozufwO8kxrtRIp', b'lGz1WdOcs9nNDOvTzYLuS4lwFiqF0BL9', b'ma'),
        # (b'18789928', b'hyQMdNFlDqFz3VyGqQcHIaor', b'eUdsLZLBdG5QMzB1d1GZTw3IoPDDRjo0', b'Zhixin'),
        # (b'18791858', b'GqGvije41GaTkcBhF1CBGwVq', b'LTE2Y6NTsFRaU2jogCTzq9olgGq3ddhG', b'Taozi'),
        (b'18795201', b'GUuncegpuzxSKPEioDIuPTQk', b'6ntq0UpQSih64tyWFPFVdueAi60mUxLM', b'Laona'),
        (b'18805584', b'ISNvG24kFh6Yrx8cPOaO7CQ7', b'vnl4hNMmeU0OVeWXjO2vN8gnqQChjMmQ', b'Zhangchuan'),
        (b'18805823', b'GUeb8blkjNlFsBZi7VfEqtG4', b'DgaGPhuIwdiPPigcBOQKsUakUWDi8C0Y', b'Lizhuowang'),
        (b'18808815', b'iDfjizZG4qHpMMF7bFH6xnX0', b'jeXWcFxGseHZ2EeGrUNQnIO6s9fD7uqB', b'Yanruofan'),
        # (b'14590965', b'0HoOwa6hiW9K776yiEviMPn2', b'lCOlp135b5ccTsm3IxzMNxOG6zP1aq4Q', b'online'),
        # (b'10165997', b'iHXEk2TT7emuvfsoviT9A1V5', b'2e9f3f9d4a6e17e2c5c373eb5f7a0ba7', b'phantom'),
        # (b'18693706', b'jIRh7reXXtlZVieup6UGnseY', b'0DWPZGIMIXrBr0AjfYYZVQOrwqDR4vsI', b'LiKeren'),
        # (b'18693751', b'pP83oZh9ohkh8A8B3ndyRw2D', b'TSq3EAgdeEU2EKBZy7mweXob2yxup8bM', b'Xiaoluobo'),
        # (b'18693889', b'5tBRL2giGuwVlQC4isdT7Xbi', b'TZR56Yp8sGFd9GVDaSCNrQEaPZ4fueKe', b'ZhangYue'),
        # (b'18694105', b'HL715fUYWS0IvxvMOXGW34EE', b'6ITbGAPi0rBsxh2T56s01GkDqYWlytMe', b'Xiaolingzhi'),
        # (b'18694446', b'GGoWTNLuZl32erzkrcyBjEdg', b'OUdMiX55rNP0dsIOe7mI3kn79DymCzz9', b'liangchenzi'),
        # (b'18755305', b'x36ksHvIsPnI0hWzYYsLgAVK', b'xEtMwNZob41jBeEulpRhw3purEd7z975', b'Yingda'),
        # (b'18789781', b'ywxHla8c5Zw8tmvtMghkHdUk', b'n6ccmSLLZ0XKdy7oXDNvSejinHs8gQl1', b'ba'),
    ]

    def __init__(self):
        self._create_shared_array()

    def __len__(self):
        return len(self.tokens)

    def __getitem__(self, item):
        return self.array[item]

    def pop(self, index):
        p = self.tokens.pop(index)
        self._create_shared_array()
        return p
        # return BaiduAPIToken(*p)

    def append(self, l):
        self.tokens.append(l)
        self._create_shared_array()
        return self

    def popappend(self, index):
        _next = self.tokens.pop(index)
        self.tokens.append(_next)
        self._create_shared_array()
        return BaiduAPIToken(*_next)

    def times(self, n):
        self.tokens *= n
        self._create_shared_array()

    def range(self, l, r):
        self.tokens = self.tokens[l:r]
        self._create_shared_array()

    def first(self, n):
        self.tokens = self.tokens[:n]
        self._create_shared_array()

    def last(self, n):
        self.tokens = self.tokens[-n:]
        self._create_shared_array()

    def _create_shared_array(self):
        self.array = Array(BaiduAPIToken, self.tokens)


def translate_test():
    fp = '/home/cchen/Downloads/2086.82_2087.68.wav'
    wav = Audio.from_file(fp)
    buff = BytesIO()
    wav.export(buff, format='wav')
    wavbytes = buff.getvalue()
    tokens = BaiduAPITokens()
    for token in tokens:
        print(token.note, sep=' ')
        APP_ID = token.APP_ID
        API_KEY = token.API_KEY
        SECRET_KEY = token.SECRET_KEY
        client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
        res = client.asr(wavbytes, 'wav', 16000, {'dev_pid': 1537, })
        print(res)


def presetup(fp, dp_src):
    vid_read = set()
    if os.path.exists(os.path.join(DATA_DIR, 'wav_info.csv')):
        df_read = pd.read_csv(os.path.join(DATA_DIR, 'wav_info.csv'), header=None, dtype=str)
        vid_read = set(df_read[1].to_list())

    _, uid, vfile = fp.rsplit(os.path.sep, 2)
    vid, _ = os.path.splitext(vfile)

    if os.path.exists(os.path.join(dp_src, uid, vid + '.run')) or vid in vid_read:
        return vid, None
    out = []
    for wavfile in tqdm(read_zip_names(fp)):
        start_end, _ = os.path.splitext(wavfile)
        start, end = start_end.split('_')
        wav = read_audio_zip(os.path.join(dp_src, uid, vid + '.zip'), filename=wavfile)
        duration = wav.duration_seconds
        vadscore = wav.to_frames(50).vad(2)
        out.append([uid, vid, start, end, duration, vadscore])
    return vid, out


if __name__ == '__main__':
    import random
    from utils import Counter


    counter = Counter()
    tokens = BaiduAPITokens()

    # tokens.range(None, 6)
    # dp_wavsegs = '/home/cchen/data/pcm_s16le_nosilence_20to30s'
    # tokens.range(6, 12)
    # dp_wavsegs = '/home/yuhenghu/data/pcm_s16le_nosilence_20to30s'
    # tokens.range(12, None)
    # dp_wavsegs = '/home/cchen224/data/pcm_s16le_nosilence_20to30s'

    # fp_wavinfo = 'wav_info.csv'
    # fp_dst = 'transcript.csv'

    print(tokens.tokens)
    dp_wavsegs = '/media/cchen/exec/yizhibo/pcm_s16le_nosilence_20to30s/'
    fp_wavinfo = '/home/cchen/data/livestream/wanghong/wav_info.csv'
    fp_dst = os.path.join(DATA_DIR, 'transcript.csv')

    target_list = list(setup(fp_wavinfo, fp_dst))

    # target_list = [it for it in target_list if int(it[0]) in {2}]
    # target_list = [it for it in target_list if int(it[0]) in {5, 6, 7, 8}]
    # target_list = [it for it in target_list if int(it[0]) in {3}]

    print(len(target_list))
    target_list = random.sample(target_list, len(target_list))
    target_func = partial(translate, dp_src=dp_wavsegs)
    listen_func = partial(write_csv_1d, fp=fp_dst)
    qmap(target_func, target_list, listen_func, n=len(tokens.tokens)+1)

    # from glob import glob
    # from _utils import write_csv_2d
    #
    # target_func = partial(presetup, dp_src='/media/cchen/exec/yizhibo/pcm_s16le_nosilence_20to30s/')
    # target_list = glob(os.path.join('/media/cchen/exec/yizhibo/pcm_s16le_nosilence_20to30s/', '*', '*.zip'))
    # listen_func = partial(write_csv_2d, fp=os.path.join(DATA_DIR, 'wav_info.csv'))
    # qmap(target_func, target_list, listen_func, n=16)

    # aa0 = pd.read_csv('/home/cchen/data/livestream/wanghong/transcript0.csv', header=None, dtype=str)
    # aa1 = pd.read_csv('/home/cchen/data/livestream/wanghong/transcript1.csv', header=None, dtype=str)
    # aa2 = pd.read_csv('/home/cchen/data/livestream/wanghong/transcript2.csv', header=None, dtype=str)
    # aa3 = pd.read_csv('/home/cchen/data/livestream/wanghong/transcript3.csv', header=None, dtype=str)
    # cc = pd.read_csv('/home/cchen/data/livestream/wanghong/transcript.csv', header=None, dtype=str)
    # # # # cc = aa1.append(aa2).append(aa3)
    # cc = cc.loc[cc[5] != '224']
    # cc = cc.loc[cc[4] != 'authentication failed.']
    # # cc = cc.loc[cc[4] != 'backend error.']
    # cc = cc.loc[cc[4] != 'request pv too much']
    # cc = cc.loc[cc[4] != 'json speech not found.']
    # dd = cc.drop_duplicates(subset=[0,1,2,3,4])
    # # # ee = dd.loc[~(dd[0] + '/' +dd[1]).isin(b)]
    # dd.to_csv('/home/cchen/data/livestream/wanghong/transcript.csv', header=None, index=None)


##
# import pandas as pd
# df_wavinfo = pd.read_csv('/home/cchen/data/livestream/wanghong/wav_info.csv', header=None)
# data = pd.read_csv(fp_dst, dtype=str, header=None)
# df_out = data.loc[data[6] != '224']
# df_out = df_out.loc[~df_out[5].isna()]
# df_out.to_csv(os.path.join(DATA_DIR, 'transcript.csv'), index=None, header=None)
