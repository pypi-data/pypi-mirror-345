import multiprocessing
import time

from tqdm import tqdm
from utils import touch
import numpy as np


def reader(qr):
    while True:
        signal = qr.get()
        if signal == 'done':
            qe.put('done')
            break
        # time.sleep(1)
        touch('/home/cchen/Downloads/test/t1_{}.txt'.format(signal + 2))
        print('r1')
        qe.put((signal + 2, signal + 3))
        print('r2')


def executor(qe):
    while True:
        signal = qe.get()
        print('e1')
        if signal == 'done':
            qe.put('done')
            break
        _, signal = signal
        time.sleep(2)
        touch('/home/cchen/Downloads/test/t2_{}.txt'.format(signal * 3))
        qw.put(signal * 3)


def writer(qw):
    while True:
        signal = qw.get()
        if signal == 'done':
            qe.put('done')
            break
        # time.sleep(1)
        print(signal)
        touch('/home/cchen/Downloads/test/t3_{}.txt'.format(signal - 2))
        qn.put(True)


def main(qm):
    while True:
        uid_vid_se = qm.get()
        print(uid_vid_se)
        qr.put(uid_vid_se)
        qn.get()




if __name__ == '__main__':
    manager = multiprocessing.Manager()
    qr = manager.Queue()
    qe = manager.Queue()
    qw = manager.Queue()
    qn = manager.Queue()
    qm = manager.Queue()
    for it in list(range(2, 5)) + ['done']:
        qm.put(it)
    pool = multiprocessing.Pool(3)
    pool.imap_unordered(main, iter([qm,]))
    pool.imap_unordered(reader, iter([qr, ]))
    pool.imap_unordered(writer, iter([qw, ]))

    qr.put(1)
    executor(qe)

    # print(qn.get())
    # while qn.get():
    #     uid_vid_se = next(bar)
    #     qr.put(uid_vid_se)
    # qr.put('done')

##
