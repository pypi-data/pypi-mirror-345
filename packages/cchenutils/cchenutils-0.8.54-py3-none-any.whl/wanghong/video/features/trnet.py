# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/31/20
# @File  : [wanghong] trnet.py


import os
import sys
sys.path.insert(0, '/home/cchen/pylibs/trn')
os.chdir('/home/cchen/pylibs/trn')

from functools import partial
from glob import glob
from zipfile import ZipFile

import numpy as np
import torch.nn.parallel
import torch.optim
import torchvision
import trn
from PIL import Image
from trn import transforms
from trn.models import TSN
from wanghong.utils import tmap, touch
from torch.utils.data import Dataset, DataLoader
import pandas as pd


# os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def setup(dp_ref, dp_dst):
    sample_size = 5
    # df_read = pd.read_csv('/home/cchen/Dropbox/streaming/video_types2.csv', header=None, dtype=str)
    # read = set(df_read[1].to_list())
    # df_read2 = pd.read_csv('/home/cchen/data/wanghong/yizhibo_transcript.csv', dtype=str)
    # df_read2 = df_read2.loc[df_read2['transcript'].apply(lambda x: '淘宝' in x or '号链接' in x or '这款' in x)]
    # df_read2['se'] = df_read2.apply(lambda x: x['start'] + '_' + x['end'], axis=1)
    # df_read2 = df_read2.groupby(['Yizhibo_UID', 'Yizhibo_VID']).agg({'se': set}).reset_index()
    # df_read2['uv'] = df_read2.apply(lambda x: os.path.join(x['Yizhibo_UID'][2:], x['Yizhibo_VID'][2:]), axis=1)
    # read2 = dict(zip(df_read2['uv'], df_read2['se']))

    map = pd.read_csv('/home/cchen/data/wanghong/uids.csv')
    yids = map['Yizhibo_UID'].to_list()
    sids = map['Taobao_SID'].to_list()
    map = dict(zip(sids, yids))
    df_read = pd.read_csv('/home/cchen/data/wanghong/taobao_shops.csv', dtype=str)
    df_read = df_read.loc[df_read['category_manual'].isin({'clothes'})]
    #, 'accessories', 'bag', 'tea', 'food', 'cosmetics', 'shoe', 'jewelry', 'trinket', 'gift'
    read = {map[sid][2:] for sid in df_read['Taobao_SID'].tolist() if sid in map}

    for fp in glob(os.path.join(dp_ref, '*', '*')):
        uid_vid = os.path.relpath(fp, dp_ref)
        uid, vid = uid_vid.split(os.path.sep, 1)
        if uid not in read:
            continue
        ses_src = {os.path.splitext(sefile)[0] for sefile in os.listdir(os.path.join(dp_ref, uid_vid))
                   if sefile.endswith('.npz')}
        if sample_size > len(ses_src):
            continue
        os.makedirs(os.path.join(dp_dst, uid_vid), exist_ok=True)
        ses_dst = {os.path.splitext(sefile)[0] for sefile in os.listdir(os.path.join(dp_dst, uid_vid))
                   if sefile.endswith('.npz') and not os.path.exists(sefile.replace('.npz', '.run'))}
        ses = ses_src #& read2.get(uid_vid, set())
        ses_out = ses - ses_dst
        if len(ses) < sample_size:
            if len(ses_dst - (ses_src - ses)) < sample_size - len(ses):
                ses_out |= set(random.sample(ses_src - ses - ses_dst, max(0, sample_size - len(ses) - len(ses_dst - ses))))
            else:
                continue
        elif len(ses_dst & ses) < sample_size:
            ses_out = set(random.sample(ses_out, sample_size - len(ses_dst & ses)))
        else:
            continue
        for se in ses_out:
            yield os.path.join(uid_vid, se)
    # for fp in glob(os.path.join(dp_ref, '*', '*', '*.npz')):
    #     uid_vid_sefile = os.path.relpath(fp, dp_ref)
    #     uid_vid_se, _ = os.path.splitext(uid_vid_sefile)
    #     uid, vid, _ = uid_vid_se.split(os.path.sep, 2)
    #     if uid_vid_se not in read:
    #
    #         continue
    #     if os.path.exists(os.path.join(dp_dst, uid_vid_se + '.run')) or \
    #             not os.path.exists(os.path.join(dp_dst, uid_vid_se + '.npz')):
    #         os.makedirs(os.path.join(dp_dst, uid, vid), exist_ok=True)
    #         yield uid_vid_se


def build():
    global net
    trn_dir = os.path.dirname(trn.__file__)
    categories_file = os.path.join(trn_dir, 'pretrain/moments_categories.txt')
    categories = [line.rstrip() for line in open(categories_file, 'r').readlines()]
    num_class = len(categories)
    net = TSN(num_class, 8, 'RGB', base_model='InceptionV3', consensus_type='TRNmultiscale',
              img_feature_dim=256, print_spec=False)
    checkpoint = torch.load(os.path.join(trn_dir,
                                         'pretrain/TRN_moments_RGB_InceptionV3_TRNmultiscale_segment8_best.pth.tar'))
    base_dict = {'.'.join(k.split('.')[1:]): v for k, v in list(checkpoint['state_dict'].items())}
    net.load_state_dict(base_dict)
    net.cuda().eval()

    global transform
    input_size, scale_size, input_mean, input_std = net.input_size, net.scale_size, net.input_mean, net.input_std
    transform = torchvision.transforms.Compose([
        transforms.GroupOverSample(input_size, scale_size),
        transforms.Stack(roll=('InceptionV3' in ['BNInception', 'InceptionV3'])),
        transforms.ToTorchFormatTensor(div=('InceptionV3' not in ['BNInception', 'InceptionV3'])),
        transforms.GroupNormalize(input_mean, input_std),
    ])


def load_frames(fp):
    num_frames = 8
    with ZipFile(fp) as zipi:
        zipnames = zipi.namelist()
        return [(f'{idx * num_frames + 4:05d}',
                 [Image.open(zipi.open(iname)).convert('RGB')
                  for iname in zipnames[num_frames * idx: num_frames * (idx + 1)]])
                for idx in range(len(zipnames) // num_frames)]


class ZipDataset(Dataset):

    def __init__(self, fp, transform):
        self.data = load_frames(fp)
        self.transform = transform

    def __getitem__(self, index):
        name, frames = self.data[index]
        data = self.transform(frames)
        input = data.view(-1, 3, data.size(1), data.size(2)).unsqueeze(0)
        return name, input

    def __len__(self):
        return len(self.data)


def imgs2trn(uid_vid_se, dp_src, dp_dst):
    fp_src = os.path.join(dp_src, uid_vid_se + '.zip')
    fp_dst = os.path.join(dp_dst, uid_vid_se + '.npz')
    fp_run = os.path.join(dp_dst, uid_vid_se + '.run')

    touch(fp_run)
    try:
        scores = dict()
        with torch.no_grad():
            dataset = ZipDataset(fp_src, transform=transform)
            dataloader = DataLoader(dataset, batch_size=1, shuffle=False, num_workers=2, pin_memory=True)
            for name, input in dataloader:
                logit = net(input.cuda())
                score = torch.mean(logit, dim=0).data.cpu().numpy()
                scores[name[0]] = score
        np.savez(fp_dst, **scores)
    except Exception:
        return uid_vid_se, False
    os.remove(fp_run)
    return uid_vid_se, True


def cleanup(dp_emb):
    for fp in glob(os.path.join(dp_emb, '*', '*', '*.npz')):
        try:
            npz = np.load(fp)
            if len(npz.keys()) == 0:
                os.remove(fp)
                print(fp)
        except ValueError:
            print(fp)
            os.remove(fp)


if __name__ == '__main__':
    import random

    dp_ref = '/mnt/nvme/yizhibo/nosilence_20to30s/inception_resnet_v2'
    dp_img = '/mnt/sdb/nosilence_20to30s/img'
    dp_trn = '/mnt/nvme/yizhibo/nosilence_20to30s/trn'

    target_list = list(setup(dp_ref, dp_trn))
    target_list = random.sample(target_list, len(target_list))
    target_func = partial(imgs2trn, dp_src=dp_img, dp_dst=dp_trn)
    build()
    tmap(target_func, target_list)
    
    cleanup(dp_trn)