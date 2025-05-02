# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/26/20
# @File  : [wanghong] retrieve.py


from __future__ import division
import argparse

import torch
from mmcv import Config
from mmcv.runner import load_checkpoint

from mmfashion.core import ClothesRetriever
from mmfashion.datasets import build_dataloader, build_dataset
from mmfashion.models import build_retriever
from mmfashion.utils import get_img_tensor


def parse_args():
    parser = argparse.ArgumentParser(
        description='MMFashion In-shop Clothes Retriever Demo')
    parser.add_argument(
        '--input',
        type=str,
        help='input image path',
        # default='/home/cchen/data/taobao/taobao_images/34175967/566935700989.jpg')
        default='/home/cchen/data/taobao/taobao_images/35699175/558269853581.jpg')
    parser.add_argument(
        '--topk', type=int, default=5, help='retrieve topk items')
    parser.add_argument(
        '--config',
        help='train config file path',
        default='/home/cchen/pylibs/mmfashion/configs/retriever_in_shop/global_retriever_vgg_loss_id.py')
    parser.add_argument(
        '--checkpoint',
        type=str,
        default='/home/cchen/pylibs/mmfashion/checkpoint/InShopClothesRetrieval_vgg16_global.pth',
        help='the checkpoint file to resume from')
    parser.add_argument(
        '--use_cuda', type=bool, default=True, help='use gpu or not')
    args = parser.parse_args()
    return args


def _process_embeds(dataset, model, cfg, use_cuda=True):
    data_loader = build_dataloader(
        dataset,
        cfg.data.imgs_per_gpu,
        cfg.data.workers_per_gpu,
        len(cfg.gpus.test),
        dist=False,
        shuffle=False)

    embeds = []
    with torch.no_grad():
        for data in data_loader:
            if use_cuda:
                img = data['img'].cuda()
            embed = model(img, landmark=data['landmark'], return_loss=False)
            embeds.append(embed)

    embeds = torch.cat(embeds)
    embeds = embeds.data.cpu().numpy()
    return embeds


if __name__ == '__main__':
    seed = 0
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    args = parse_args()
    args.config = '/home/cchen/pylibs/mmfashion/configs/retriever_consumer_to_shop/roi_retriever_vgg.py'
    #'/home/cchen/pylibs/mmfashion/configs/retriever_in_shop/global_retriever_vgg_loss_id_triplet.py'
    args.checkpoint = '/home/cchen/pylibs/mmfashion/checkpoint/Consumer2ShopClothesRetrieval_vgg16_global.pth'
    cfg = Config.fromfile(args.config)
    cfg.model.pretrained = args.checkpoint
    #'/home/cchen/pylibs/mmfashion/checkpoint/InShopClothesRetrieval_vgg16_global.pth'
    model = build_retriever(cfg.model)
    load_checkpoint(model, args.checkpoint)
    if args.use_cuda:
        model.cuda()
    model.eval()
    dp = '/home/cchen/data/taobao/taobao_images/65350170'
    from glob import glob
    import os
    fps = glob(os.path.join(dp, '*.jpg'))
    img_tensor = torch.cat([get_img_tensor(fp, True) for fp in fps], 0)

    query_feat = model(img_tensor, landmark=None, return_loss=False)
    lst = [x.cpu().data.numpy() for x in query_feat]
    import numpy as np

    def cos_mat(lst):
        sims = []
        for cnt, it in enumerate(lst[: -1]):
            print(' ' * cnt * 8, end='')
            for it2 in lst[cnt+1:]:
                sim = cos_sim(it, it2)
                sims.append(sim)
                print('{:8.2f}'.format(sim), end='')
            print()
        return sims

    def cos_sim(a, b):
        """Takes 2 vectors a, b and returns the cosine similarity according
        to the definition of the dot product
        """
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        return dot_product / (norm_a * norm_b)


    a = cos_mat(lst)

    import sys
    sys.path.append('/home/cchen/pylibs/mmfashion')
    gallery_set = build_dataset(cfg.data.gallery)
#     gallery_embeds = _process_embeds(gallery_set, model, cfg)
#
#     retriever = ClothesRetriever(cfg.data.gallery.img_file, cfg.data_root,
#                                  cfg.data.gallery.img_path)
#     retriever.show_retrieved_images(query_feat, gallery_embeds)
