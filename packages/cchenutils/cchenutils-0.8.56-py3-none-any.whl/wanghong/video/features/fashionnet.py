# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/25/20
# @File  : [wanghong] fashionnet.py

import argparse
import os

from mmcv import Config
from mmcv.runner import load_checkpoint
from mmfashion.models import build_predictor
from mmfashion.utils import get_img_tensor


def parse_args():
    parser = argparse.ArgumentParser(
        description='MMFashion Attribute Prediction Demo')
    parser.add_argument(
        '--input',
        type=str,
        help='input image path',
        # default='/home/cchen/data/taobao/taobao_images/34175967/566935700989.jpg')
        default='/home/cchen/data/taobao/taobao_images/35699175/558269853581.jpg')
    parser.add_argument(
        '--checkpoint',
        type=str,
        help='checkpoint file',
        default='/home/cchen/pylibs/mmfashion/checkpoint/AttributePrediction_resnet50_global.pth')
    # default='/home/cchen/pylibs/mmfashion/checkpoint/AttributePrediction_vgg16_global.pth')
    # default='/home/cchen/pylibs/mmfashion/checkpoint/AttributePrediction_vgg16_landmark.pth')
    parser.add_argument(
        '--config',
        help='test config file path',
        default='/home/cchen/pylibs/mmfashion/configs/attribute_predict/global_predictor_resnet_attr.py')
    # default='/home/cchen/pylibs/mmfashion/configs/attribute_predict/global_predictor_vgg_attr.py')
    # default='/home/cchen/pylibs/mmfashion/configs/attribute_predict/roi_predictor_vgg_attr.py')
    parser.add_argument(
        '--use_cuda', type=bool, default=True, help='use gpu or not')
    args = parser.parse_args()
    return args

def main(fp):
    args = parse_args()
    args.config = '/home/cchen/pylibs/mmfashion/configs/attribute_predict/roi_predictor_resnet_attr.py'
    cfg = Config.fromfile(args.config)
    args.input = fp
    img_tensor = get_img_tensor(args.input, args.use_cuda)

    # cfg.model.pretrained = '/home/cchen/pylibs/mmfashion/checkpoint/vgg16.pth'
    # cfg.model.pretrained = None
    cfg.model.pretrained = '/home/cchen/pylibs/mmfashion/checkpoint/AttributePrediction_resnet50_landmark.pth'
    args.checkpoint = '/home/cchen/pylibs/mmfashion/checkpoint/AttributePrediction_resnet50_landmark.pth'
    model = build_predictor(cfg.model)
    load_checkpoint(model, args.checkpoint, map_location='cpu')
    if args.use_cuda:
        model.cuda()

    model.eval()

    # predict probabilities for each attribute
    attr_prob = model(img_tensor, attr=None, landmark=None, return_loss=False)
    for k, v in cfg.data.test.items():
        if k.endswith('_file') or k.endswith('_path'):
            cfg.data.test[k] = os.path.join('/home/cchen/pylibs/mmfashion', cfg.data.test[k])
    return attr_prob.data.cpu().numpy()


if __name__ == '__main__':
    import torch

    args = parse_args()
    args.config = '/home/cchen/pylibs/mmfashion/configs/attribute_predict/global_predictor_vgg_attr.py'
    cfg = Config.fromfile(args.config)
    img_tensor = torch.cat([get_img_tensor('/home/cchen/data/taobao/taobao_images/34587599/566108867386.jpg', True),
                            get_img_tensor('/home/cchen/data/taobao/taobao_images/35699175/558269853581.jpg', True)], 0)

    # cfg.model.pretrained = '/home/cchen/pylibs/mmfashion/checkpoint/vgg16.pth'
    # cfg.model.pretrained = None
    cfg.model.pretrained = '/home/cchen/pylibs/mmfashion/checkpoint/AttributePrediction_vgg16_global.pth'
    args.checkpoint = '/home/cchen/pylibs/mmfashion/checkpoint/AttributePrediction_vgg16_global.pth'
    model = build_predictor(cfg.model)
    load_checkpoint(model, args.checkpoint, map_location='cpu')
    if args.use_cuda:
        model.cuda()

    model.eval()

    # predict probabilities for each attribute
    attr_prob = model(img_tensor, attr=None, landmark=None, return_loss=False)


    a = attr_prob[0].cpu().data.numpy()
    b = attr_prob[1].cpu().data.numpy()
    import numpy as np
    def cos_sim(a, b):
        """Takes 2 vectors a, b and returns the cosine similarity according
        to the definition of the dot product
        """
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        return dot_product / (norm_a * norm_b)
    print(cos_sim(a, b))

##

