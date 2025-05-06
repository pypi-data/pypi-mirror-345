import base64
import csv
import os
import time
from io import BytesIO
from zipfile import ZipFile

import pandas as pd
import requests
from PIL import Image
from tqdm import tqdm

from utils import DATA_DIR


def img2base64(img):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue())


def facepp(img):
    payload = {
        'api_key': 'pqLY9sQp07cBuyXXgr3ntl47WY-p8a-F',
        'api_secret': 'qljRujMaShVUmz1tqByEyjmdrsGMwhxT',
        'image_base64': img2base64(img),
        'return_attributes': 'gender,age,smiling,headpose,facequality,blur,eyestatus,emotion,beauty,mouthstatus,eyegaze,skinstatus',
    }
    res = requests.post('https://api-us.faceplusplus.com/facepp/v3/detect', data=payload)
    data = res.json()
    if 'error_message' in data and data['error_message'] == 'CONCURRENCY_LIMIT_EXCEEDED':
        time.sleep(3)
        return facepp(img)
    return data


if __name__ == '__main__':
    fp_dst = r"D:\yizhibo_facepp.csv"

    frames = pd.read_csv(f'{DATA_DIR}/yizhibo_faces_snippet.csv', dtype=str)
    if os.path.exists(fp_dst):
        with open(fp_dst, encoding='utf-8') as i:
            csvreader = csv.reader(i)
            next(csvreader)
            read = {'|'.join(row[:4]) for row in csvreader}
    else:
        with open(fp_dst, 'a', encoding='utf-8') as o:
            csvwriter = csv.writer(o, lineterminator='\n')
            outheader = [
                'Yizhibo_UID', 'Yizhibo_VID', 'snippet', 'frame', 'face_token',
                'face_rectangle/top', 'face_rectangle/left', 'face_rectangle/width', 'face_rectangle/height',
                'gender', 'beauty/male_score', 'beauty/female_score',
                'age', 'smile',
                'headpose/pitch_angle', 'headpose/roll_angle', 'headpose/yaw_angle',
                'blurness', 'motionblur', 'gaussianblur',
                'left_eye_status/no_glass_eye_open', 'left_eye_status/no_glass_eye_close',
                'left_eye_status/normal_glass_eye_open', 'left_eye_status/normal_glass_eye_close',
                'left_eye_status/dark_glasses', 'left_eye_status/occlusion',
                'right_eye_status/no_glass_eye_open', 'right_eye_status/no_glass_eye_close',
                'right_eye_status/normal_glass_eye_open', 'right_eye_status/normal_glass_eye_close',
                'right_eye_status/dark_glasses', 'right_eye_status/occlusion',
                'anger', 'disgust', 'fear', 'happiness', 'neutral', 'sadness', 'surprise',
                'facequality',
                'mouthstatus/surgical_mask_or_respirator', 'mouthstatus/open', 'mouthstatus/close',
                'mouthstatus/other_occlusion',
                'lefteyegaze/position_x_coordinate', 'lefteyegaze/position_y_coordinate',
                'lefteyegaze/vector_x_component', 'lefteyegaze/vector_y_component', 'lefteyegaze/vector_z_component',
                'righteyegaze/position_x_coordinate', 'righteyegaze/position_y_coordinate',
                'righteyegaze/vector_x_component', 'righteyegaze/vector_y_component', 'righteyegaze/vector_z_component',
                'skinstatus/health', 'skinstatus/stain', 'skinstatus/dark_circle', 'skinstatus/acne',
                'glass'
            ]
            csvwriter.writerow(outheader)
            read = set()

    for _, row in tqdm(frames.iterrows(), total=frames.shape[0]):
        if '|'.join([row["Yizhibo_UID"], row["Yizhibo_VID"], row["snippet"], row['frame']]) in read:
            continue
        path = f'D:/img/{row["Yizhibo_UID"][2:]}/{row["Yizhibo_VID"][2:]}/{row["snippet"]}.zip'
        with ZipFile(path) as myzip, myzip.open(row['frame'] + '.jpg') as myfile, open(fp_dst, 'a', encoding='utf-8') as o:
            csvwriter = csv.writer(o, lineterminator='\n')
            img = Image.open(myfile)
            data = facepp(img)
            for face in data['faces']:
                outrow = [
                    row["Yizhibo_UID"], row["Yizhibo_VID"], row["snippet"], row['frame'], face['face_token'],
                    (box := face['face_rectangle'])['top'], box['left'], box['width'], box['height'],
                    (attr := face['attributes'])['gender']['value'],
                    attr['beauty']['male_score'], attr['beauty']['female_score'],
                    attr['age']['value'],
                    attr['smile']['value'],
                    (headpose := attr['headpose'])['pitch_angle'], headpose['roll_angle'], headpose['yaw_angle'],
                    (blur := attr['blur'])['blurness']['value'],
                    blur['motionblur']['value'], blur['gaussianblur']['value'],
                    (lefteye := attr['eyestatus']['left_eye_status'])['no_glass_eye_open'],
                    lefteye['no_glass_eye_close'], lefteye['normal_glass_eye_open'],
                    lefteye['normal_glass_eye_close'], lefteye['dark_glasses'], lefteye['occlusion'],
                    (righteye := attr['eyestatus']['right_eye_status'])['no_glass_eye_open'],
                    righteye['no_glass_eye_close'], righteye['normal_glass_eye_open'],
                    righteye['normal_glass_eye_close'], righteye['dark_glasses'], righteye['occlusion'],
                    (emotion := attr['emotion'])['anger'], emotion['disgust'], emotion['fear'], emotion['happiness'],
                    emotion['neutral'], emotion['sadness'], emotion['surprise'],
                    attr['facequality']['value'],
                    (mouth := attr['mouthstatus'])['surgical_mask_or_respirator'],
                    mouth['open'], mouth['close'], mouth['other_occlusion'],
                    (lefteyegaze := attr['eyegaze']['left_eye_gaze'])['position_x_coordinate'],
                    lefteyegaze['position_y_coordinate'], lefteyegaze['vector_x_component'],
                    lefteyegaze['vector_y_component'], lefteyegaze['vector_z_component'],
                    (righteyegaze := attr['eyegaze']['right_eye_gaze'])['position_x_coordinate'],
                    righteyegaze['position_y_coordinate'], righteyegaze['vector_x_component'],
                    righteyegaze['vector_y_component'], righteyegaze['vector_z_component'],
                    (skinstatus := attr['skinstatus'])['health'],
                    skinstatus['stain'], skinstatus['dark_circle'], skinstatus['acne'],
                    None if (glass := attr['glass']['value']) == 'None' else glass,
                ]
                csvwriter.writerow(outrow)
                time.sleep(1)