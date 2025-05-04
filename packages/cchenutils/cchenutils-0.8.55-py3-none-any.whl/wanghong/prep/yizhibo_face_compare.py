from utils import DATA_DIR
import pandas as pd
import numpy as np
from numpy import dot
from numpy.linalg import norm
from itertools import combinations
from scipy.stats import entropy
import face_recognition



def cosine_sim(a, b):
    return dot(a, b)/(norm(a)*norm(b))


def information_radius(ps):
    a = np.array(ps if isinstance(ps, list) else ps.to_list()).mean(axis=0)
    # return sum(cosine_sim(p, a) for p in ps) / len(ps) if len(ps) else None
    return sum(np.linalg.norm(p - a) for p in ps) / len(ps) if len(ps) else None


df = pd.read_csv(f'{DATA_DIR}/yizhibo_face_recognition.csv', dtype=str).dropna()
df['encoding'] = df['encoding'].apply(lambda x: np.frombuffer(eval(x)))
a = df.groupby(['Yizhibo_UID'], as_index=False).agg({'encoding': information_radius})
face_recognition.compare_faces()