# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/27/20
# @File  : [wanghong] utils.py


import csv
import multiprocessing
import os
import subprocess
import time
from datetime import datetime
from functools import partial

from tqdm import tqdm

# DATA_DIR = os.getcwd().replace('Dropbox/projects', 'data')
DATA_DIR = '/home/cchen/data/wanghong'
SUCCESS = '_SUCCESS'
ERROR = '_ERROR'


def touch(fp, content=''):
    with open(fp, 'w') as o:
        o.write(content)
    return True


def mark(folder, info):
    return touch(os.path.join(folder, info))


def remove(folder, info):
    try:
        os.remove(os.path.join(folder, info))
        return True
    except WindowsError:
        return False


def exists(folder, info):
    return os.path.exists(os.path.join(folder, info))


mark_success = partial(mark, info=SUCCESS)
mark_error = partial(mark, info=ERROR)
remove_error = partial(remove, info=ERROR)
exists_success = partial(exists, info=SUCCESS)
exists_error = partial(exists, info=ERROR)


def call(cmd, wait=True, print_cmd=True):
    DEVNULL = open(os.devnull, 'wb')
    if print_cmd:
        print(cmd)
    return subprocess.check_output(cmd, stderr=DEVNULL, shell=True) if wait else \
        subprocess.Popen(cmd, stderr=DEVNULL, shell=True)


def mmap(fnc, lst, n=8, **kwargs):
    pool = multiprocessing.Pool(n)
    with tqdm(pool.imap_unordered(fnc, iter(lst)), total=len(lst), ascii=kwargs.get('ascii', True), ncols=160) as bar:
        for status, res in bar:
            bar.set_description(status)


def mmap_nobar(fnc, lst, n=8):
    pool = multiprocessing.Pool(n)
    it = pool.imap_unordered(fnc, iter(lst))
    count = 0
    total = len(lst)
    digit = len(str(total))
    while True:
        count += 1
        try:
            status, res = it.next(timeout=10*60)
            tt = datetime.fromtimestamp(time.mktime(time.localtime(time.time()))).strftime("%Y/%m/%d %H:%M:%S")
            print(f'{count:{digit}d} / {total}', f'{tt}', status, sep='\t')
        except multiprocessing.TimeoutError:
            continue
        except KeyboardInterrupt:
            break


def omap(fnc, lst, outfile, n=8, **kwargs):
    with open(outfile, 'ab') as o:
        csvwriter = csv.writer(o, lineterminator='\n')
        pool = multiprocessing.Pool(n)
        with tqdm(pool.imap_unordered(fnc, iter(lst)), total=len(lst), ascii=kwargs.get('ascii', True),
                  ncols=160) as bar:
            for status, row in bar:
                csvwriter.writerow(row)
                bar.set_description(status)


def qmap(fnc, lst, listener, n=8, **kwargs):
    global counter
    manager = multiprocessing.Manager()
    q = manager.Queue()
    pool = multiprocessing.Pool(n)
    pool.imap_unordered(listener, iter([q, ]))
    with tqdm(pool.imap_unordered(fnc, iter(lst)), total=len(lst), ascii=kwargs.get('ascii', True), ncols=160) as bar:
        for status, res in bar:
            if res:
                q.put(res)
            bar.set_description(status)
    q.put('done')


def write_csv_1d(queue, fp, mode='a'):
    with open(fp, mode) as o:
        csvwriter = csv.writer(o, lineterminator='\n')
        while True:
            row = queue.get()
            if row == 'done':
                break
            if row:
                csvwriter.writerow(row)

def write_csv_2d(queue, fp, mode='a'):
    with open(fp, mode) as o:
        csvwriter = csv.writer(o, lineterminator='\n')
        while True:
            rows = queue.get()
            if rows == 'done':
                break
            if rows:
                for row in rows:
                    csvwriter.writerow(row)


def tmap(fnc, lst, **kwargs):
    n = kwargs.get('n')
    if n:
        return mmap(fnc, lst, n, **kwargs)
    with tqdm(lst, ncols=160, **kwargs) as bar:
        for item in bar:
            status, res = fnc(item)
            if not res:
                print(status)
            bar.set_description(status)


class Counter(object):
    def __init__(self):
        self.val = multiprocessing.Value('i', 0)

    def increment(self, n=1):
        with self.val.get_lock():
            self.val.value += n

    @property
    def value(self):
        return self.val.value


