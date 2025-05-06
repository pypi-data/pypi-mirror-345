# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/10/20
# @File  : [wanghong] audio.py


import numpy as np
import webrtcvad
from pyAudioAnalysis.audioBasicIO import stereo2mono
from pyAudioAnalysis.audioFeatureExtraction import mtFeatureExtraction
from pyAudioAnalysis.audioSegmentation import silenceRemoval, flags2segs
from pyAudioAnalysis.audioTrainTest import load_model, load_model_knn, classifierWrapper
from pydub import AudioSegment

from wanghong.utils import call


class Audio(AudioSegment):

    def to_array(self):
        if self.sample_width == 2:
            data = np.frombuffer(self.raw_data, np.int16)
        elif self.sample_width == 4:
            data = np.frombuffer(self.raw_data, np.int32)
        else:
            return (-1, -1)
        self.x = []
        for chn in list(range(self.channels)):
            self.x.append(data[chn::self.channels])
        self.x = np.array(self.x).T

        if self.x.ndim == 2:
            if self.x.shape[1] == 1:
                self.x = self.x.flatten()
        self.x = stereo2mono(self.x)
        self.duration = len(self.x) / self.frame_rate
        return self

    def remove_silence(self, st_win, st_step, smooth_window, weight, offset=0):
        self.to_array()
        audio_segs = []
        segs = silenceRemoval(self.x, self.frame_rate, st_win, st_step, smooth_window, weight, plot=False)
        segs = smooth_intervals(segs, window=0.5, min_duration=20., max_duration=30.)
        for seg in segs:
            ll = int(seg[0] * self.sample_width * self.frame_rate) // self.frame_width * self.frame_width
            rr = int(seg[1] * self.sample_width * self.frame_rate) // self.frame_width * self.frame_width
            audio = Audio(data=self.raw_data[ll: rr + self.frame_width],
                          sample_width=self.sample_width,
                          frame_rate=self.frame_rate,
                          channels=self.channels)
            if audio.duration_seconds > 30.:
                smooth_window /= 2.
                audio_segs.extend(audio.remove_silence(st_win, st_step, smooth_window, weight, offset=seg[0]))
            else:
                audio_segs.append((seg[0] + offset, seg[1] + offset, audio))

        return audio_segs

    def classify_speech_music(self, model_type='svm'):
        """
        This function performs mid-term classification of an audio stream.
        Towards this end, supervised knowledge is used, i.e. a pre-trained classifier.

        Speech vs. Music

        ARGUMENTS:
            - model_type:       svm or knn depending on the classifier type

        RETURNS:
            - speech_segs:      list of segment limits in seconds (e.g [[0.1, 0.9], [1.4, 3.0]] means that
                                the resulting segments are (0.1 - 0.9) seconds and (1.4, 3.0) seconds
            - music_segs:       list of segment limits in seconds (e.g [[0.1, 0.9], [1.4, 3.0]] means that
                                the resulting segments are (0.1 - 0.9) seconds and (1.4, 3.0) seconds
        """
        model_name = model_type + 'SM'
        classifier, MEAN, STD, class_names, mt_win, mt_step, st_win, st_step, compute_beat = \
            load_model_knn(model_name) if model_type == "knn" else load_model(model_name)
        mt_feats, _, _ = mtFeatureExtraction(self.x, self.frame_rate, mt_win * self.frame_rate,
                                             mt_step * self.frame_rate,
                                             round(self.frame_rate * st_win),
                                             round(self.frame_rate * st_step))
        flags = []
        Ps = []
        flags_ind = []
        for i in range(mt_feats.shape[1]):  # for each feature vector (i.e. for each fix-sized segment):
            cur_fv = (mt_feats[:, i] - MEAN) / STD  # normalize current feature vector
            res, P = classifierWrapper(classifier, model_type, cur_fv)  # classify vector
            flags_ind.append(res)
            flags.append(class_names[int(res)])  # update class label matrix
            Ps.append(np.max(P))  # update probability matrix
        flags_ind = np.array(flags_ind)

        # 1-window smoothing
        for i in range(1, len(flags_ind) - 1):
            if flags_ind[i - 1] == flags_ind[i + 1]:
                flags_ind[i] = flags_ind[i + 1]
        # convert fix-sized flags to segments and classes
        segs, classes = flags2segs(flags_ind, mt_step)
        speech_index = class_names.index('speech')
        music_index = class_names.index('music')
        speech_segs = segs[np.array(classes) == speech_index]
        music_segs = segs[np.array(classes) == music_index]
        return speech_segs, music_segs

    def to_frames(self, fps):
        assert fps in {50, 100}
        self.fps = fps
        x = int(self.frame_rate / fps * self.sample_width)
        self.frames = [self.raw_data[offset:offset + x] for offset in range(0, len(self.raw_data) - x, x)]
        return self

    def vad(self, agressivenes):
        voiceact_detector = webrtcvad.Vad(agressivenes)
        self.voiceact = [voiceact_detector.is_speech(frame, self.frame_rate) for frame in self.frames]
        self.vps = np.mean(self.voiceact)
        # self.vps = [np.mean(self.voiceact[c: c + self.fps]) for c in range(0, len(self.voiceact) + self.fps, self.fps)]
        return self.vps



def over_max_duration(segs, max_duration):
    if len(segs) <= 2:
        return False
    for seg in segs:
        if seg[1] - seg[0] > max_duration:
            return True
    return False


def smooth_intervals(segs, window=1., min_duration=20., max_duration=30.):
    if len(segs) <= 2:
        return []
    out_segments = []
    out_interval = list(segs[0])
    for seg in segs[1:]:
        if seg[0] - out_interval[1] <= window or seg[1] - out_interval[0] <= min_duration:
            if seg[1] - out_interval[0] > max_duration:
                out_segments.append(out_interval)
                out_interval = seg
            else:
                out_interval[1] = seg[1]
        else:
            out_segments.append(out_interval)
            out_interval = seg
    if len(out_segments) < 1:
        return []
    if out_segments[-1] != out_interval:
        out_segments.append(out_interval)
    return out_segments


def get_duration(fp):
    try:
        out = call('ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {}'.format(fp),
                   print_cmd=False)
        return float(out.strip())
    except ValueError:
        return None


def intersect2d(segments1, segments2):
    def intersect1d(interval1, interval2):
        l1, r1 = interval1
        l2, r2 = interval2
        ll = max(l1, l2)
        rr = min(r1, r2)
        return [] if ll >= rr else [ll, rr]

    def index_increment(index1, index2, interval1, interval2):
        if index1 == len(segments1) - 1:
            index2 += 1
        elif index2 == len(segments2) - 1:
            index1 += 1
        elif interval1[0] <= interval2[0] and interval1[1] >= interval2[1]:
            index2 += 1
        elif interval1[0] > interval2[0] and interval1[1] < interval2[1]:
            index1 += 1
        elif interval1[0] <= interval2[0]:
            index1 += 1
        else:
            index2 += 1
        return index1, index2

    index1 = 0
    index2 = 0
    intersections = []
    while index1 < len(segments1) - 1 or index2 < len(segments2) - 1:
        interval1 = segments1[index1]
        interval2 = segments2[index2]
        intersection = intersect1d(interval1, interval2)
        if intersection:
            intersections.append(intersection)
        index1, index2 = index_increment(index1, index2, interval1, interval2)
    return intersections