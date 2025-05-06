import csv
import os
from zipfile import ZipFile

from PIL import Image
from facenet_pytorch import MTCNN
from tqdm import tqdm

from utils import DATA_DIR


fp_dst = f'{DATA_DIR}/yizhibo_face.csv'
if os.path.exists(fp_dst):
    with open(fp_dst, encoding='utf-8') as i:
        csvreader = csv.reader(i)
        next(csvreader)
        read = {f'{row[0][2:]}/{row[1][2:]}/{row[2]}' for row in csvreader}
else:
    with open(fp_dst, 'w', encoding='utf-8') as o:
        csvwriter = csv.writer(o, lineterminator='\n')
        csvwriter.writerow(['Yizhibo_UID', 'Yizhibo_VID', 'snippet', 'frame', 'probabilities'])
    read = set()


with tqdm(os.listdir('D:/img')) as bar:
    for uid in bar:
        for vid in os.listdir(f'D:/img/{uid}'):
            for snippet in os.listdir(f'D:/img/{uid}/{vid}'):
                this_file = f'{uid}/{vid}/{snippet[:-4]}'
                if this_file in read:
                    continue
                bar.set_description(this_file)
                with ZipFile(f'D:/img/{uid}/{vid}/{snippet}') as myzip, open(fp_dst, 'a', encoding='utf-8') as o:
                    csvwriter = csv.writer(o, lineterminator='\n')
                    images = []
                    names = myzip.namelist()
                    for name in names:
                        myfile = myzip.open(name)
                        images.append(Image.open(myfile))
                    mtcnn = MTCNN(image_size=images[0].size[0], margin=0, keep_all=True, device='cuda:0')
                    _, probs = mtcnn(images, return_prob=True)
                    for name, prob in zip(names, probs):
                        row = [f'YU{uid}', f'YV{vid}', snippet[:-4], name[:-4],
                               prob[0] if len(prob) == 1 else '|'.join(f'{p}' for p in prob)]
                        csvwriter.writerow(row)
