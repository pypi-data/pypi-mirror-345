# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/24/20
# @File  : [wanghong] async.py


import multiprocessing
from tqdm import tqdm


def exec_async(lst, executor, setup, cleanup):
    manager = multiprocessing.Manager()
    qs = manager.Queue()
    qe = manager.Queue()
    qc = manager.Queue()
    pool = multiprocessing.Pool(3)
    pool.imap_unordered(setup, iter([qs, ]))
    pool.imap_unordered(executor, iter([qe, ]))
    pool.imap_unordered(cleanup, iter([qc, ]))

    for it in tqdm(lst):
        qs.put(it)
        qe.put(it)
        qc.put(it)


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
