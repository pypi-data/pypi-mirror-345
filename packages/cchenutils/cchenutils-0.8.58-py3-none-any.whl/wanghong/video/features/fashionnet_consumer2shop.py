# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/30/20
# @File  : [wanghong] fashionnet_consumer2shop.py



from __future__ import division

import os
from functools import partial
from glob import glob

import numpy as np
import torch
from mmcv import Config
from mmcv.runner import load_checkpoint
from mmfashion.models import build_retriever
from mmfashion.utils import get_img_tensor
from tqdm import tqdm
from wanghong.utils import touch, tmap


def setup_zhibo(dp_src, dp_dst, fp_lst=None):
    lst = {line.strip() for line in open(fp_lst)} if fp_lst else os.listdir(dp_src)
    os.makedirs(dp_dst, exist_ok=True)
    for uid in tqdm(lst):
        if uid not in os.listdir(dp_src):
            continue
        vids = os.listdir(os.path.join(dp_src, uid))
        os.makedirs(os.path.join(dp_dst, uid), exist_ok=True)
        for vid in vids:
            if os.path.exists(os.path.join(dp_dst, uid, vid + '.npz')) and \
                    not os.path.exists(os.path.join(dp_dst, uid, vid + '.run')):
                continue
            yield os.path.join(uid, vid)
            # yield glob(os.path.join(dp_src, uid, vid, '*.jpg'))


def setup_shop(dp_src, dp_dst, fp_lst=None):
    lst = {line.strip() for line in open(fp_lst)} if fp_lst else os.listdir(dp_src)
    os.makedirs(dp_dst, exist_ok=True)
    for uid in tqdm(lst):
        if uid not in os.listdir(dp_src):
            continue
        if os.path.exists(os.path.join(dp_dst, uid + '.npz')) and \
                not os.path.exists(os.path.join(dp_dst, uid + '.run')):
            continue
        yield uid


def build(fp_cfg, fp_checkpoint):
    global net
    seed = 0
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    cfg = Config.fromfile(fp_cfg)
    cfg.model.pretrained = fp_checkpoint#'/home/cchen/pylibs/mmfashion/' + cfg.model.pretrained
    net = build_retriever(cfg.model)
    load_checkpoint(net, fp_checkpoint)
    net.cuda()
    net.eval()


def fashionnet_retrieve(uid_vid, dp_src, dp_dst):
    fp_dst = os.path.join(dp_dst, f'{uid_vid}.npz')
    fp_run = os.path.join(dp_dst, f'{uid_vid}.run')

    touch(fp_run)
    fps = glob(os.path.join(dp_src, uid_vid, '*.jpg'))
    if len(fps) < 2:
        return uid_vid, False

    x = 4
    while True:
        if len(fps) % x != 1:
            break
        x += 1

    preds = []
    for cnt in range(len(fps) // x + (len(fps) % x != 0)):
        img_tensor = torch.cat([get_img_tensor(fp, True) for fp in fps[cnt * x: (cnt + 1) * x]], 0)
        pred = net(img_tensor, landmark=None, return_loss=False)
        preds.append(pred.cpu().data.numpy())
        del img_tensor, pred
    torch.cuda.empty_cache()
    np.savez(fp_dst, embedding=np.concatenate(preds, 0),
             name=np.array([os.path.splitext(os.path.relpath(fp, dp_src))[0] for fp in fps]))
    os.remove(fp_run)
    return uid_vid, True


if __name__ == '__main__':
    # dp_src = '/home/cchen/data/nosilence_20to30s/img_sample'
    # dp_dst = '/mnt/nvme/yizhibo/fashionnet_consumer2shop_consumer'
    dp_src = '/home/cchen/data/taobao/taobao_images'
    dp_dst = '/mnt/nvme/yizhibo/fashionnet_inshop'

    # build(fp_cfg='/home/cchen/pylibs/mmfashion/configs/retriever_consumer_to_shop/roi_retriever_vgg.py',
    #       fp_checkpoint='/home/cchen/pylibs/mmfashion/checkpoint/Consumer2ShopClothesRetrieval_vgg16_global.pth')
    build(fp_cfg='/home/cchen/pylibs/mmfashion/configs/retriever_in_shop/global_retriever_vgg_loss_id.py',
          fp_checkpoint='/home/cchen/pylibs/mmfashion/checkpoint/InShopClothesRetrieval_vgg16_global.pth')
    target_list = list(setup_shop(dp_src, dp_dst, fp_lst=None))#'/home/cchen/data/tmp_tb.lst'))
    target_func = partial(fashionnet_retrieve, dp_src=dp_src, dp_dst=dp_dst)
    tmap(target_func, target_list)
