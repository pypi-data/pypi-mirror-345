import csv
import os
from zipfile import ZipFile

import face_recognition
import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm

from utils import DATA_DIR

df_panel = pd.read_csv('../analysis/df_panel_items_sellerrate.csv')\
    .merge(pd.read_csv(f'{DATA_DIR}/uids.csv'), on='Taobao_SID', how='left')
uids = set(df_panel['Yizhibo_UID'].apply(lambda x: x[2:]))

fp_dst = f'D:/yizhibo_face_recognition.csv'
if os.path.exists(fp_dst):
    with open(fp_dst, encoding='utf-8') as i:
        csvreader = csv.reader(i)
        next(csvreader)
        read = {(row[0][2:], row[1][2:], row[2]) for row in csvreader}
else:
    with open(fp_dst, 'w', encoding='utf-8') as o:
        csvwriter = csv.writer(o, lineterminator='\n')
        csvwriter.writerow(['Yizhibo_UID', 'Yizhibo_VID', 'snippet', 'frame', 'location', 'encoding'])
    read = set()


videos = []
for uid in os.listdir('D:/img'):
    if uid not in uids:
        continue
    for vid in os.listdir(f'D:/img/{uid}'):
        for snippet in os.listdir(f'D:/img/{uid}/{vid}'):
            if (uid, vid, snippet[:-4]) not in read:
                videos.append((uid, vid, snippet[:-4]))

with tqdm(videos) as bar:
    for uid, vid, snippet in bar:
        bar.set_description(f'{uid}/{vid}/{snippet}')
        with ZipFile(f'D:/img/{uid}/{vid}/{snippet}.zip') as myzip, open(fp_dst, 'a', encoding='utf-8') as o:
            csvwriter = csv.writer(o, lineterminator='\n')
            images = []
            names = myzip.namelist()[8:][::16]
            out = []
            for name in names:
                myfile = myzip.open(name)
                im = Image.open(myfile).convert('RGB')
                images.append(np.array(im))
            face_locations = face_recognition.batch_face_locations(images, batch_size=128)
            for name, image, faces in zip(names, images, face_locations):
                if not faces:
                    csvwriter.writerow([f'YU{uid}', f'YV{vid}', snippet, name[:-4], None, None])
                encodings = face_recognition.face_encodings(image, faces)
                for face, enc in zip(faces, encodings):
                    csvwriter.writerow([f'YU{uid}', f'YV{vid}', snippet, name[:-4],
                                       '|'.join(str(px) for px in face), enc.tobytes()])