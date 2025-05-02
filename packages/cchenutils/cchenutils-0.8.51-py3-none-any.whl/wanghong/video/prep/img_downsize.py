# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 4/2/20
# @File  : [wanghong] img_downsize.py

from PIL import Image
import os
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from wanghong.utils import touch
import time
from io import BytesIO


img_path = '/home/cchen/Downloads/00134.jpg'
img = Image.open(img_path)

img.thumbnail((299, 9999), Image.ANTIALIAS)
img.size

img.show()

'/home/cchen/data/nosilence_20to30s/img/43412816/4i-vJOOBZHsloy_d/65.30_79.14.zip'


def downsize(uid_vid_se, dp_src, dp_dst, size=(299, 299)):
    fp_src = os.path.join(dp_src, uid_vid_se + '.zip')
    fp_dst = os.path.join(dp_dst, uid_vid_se + '.zip')
    fp_run = os.path.join(dp_dst, uid_vid_se + '.run')

    t1 = time.time()
    imgs = {}
    with ZipFile(fp_src) as zipi:
        for entry in zipi.infolist():
            with zipi.open(entry) as i:
                img = Image.open(i)
                img.thumbnail((size[0], 9999) if img.size[0] < img.size[1] else (9999, size[1]), Image.ANTIALIAS)
                imgs[entry.filename] = img

    # touch(fp_run)
    with ZipFile(fp_dst, 'w') as zipo:
        for filename, img in imgs.items():
            buffered = BytesIO()
            img.save(buffered, 'JPEG', optimize=True, quality=50)
            info = ZipInfo(filename, date_time=time.localtime(time.time()))
            info.compress_type = ZIP_DEFLATED
            info.create_system = 0
            zipo.writestr(info, buffered.getvalue())
    t2 = time.time()