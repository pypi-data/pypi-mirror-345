# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 4/8/20
# @File  : [wanghong] mmml2.py

import csv
import os
import random

import tensorflow as tf

tf.config.experimental_run_functions_eagerly(True)

from keras.layers.core import Reshape
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Layer, Concatenate, Bidirectional, LSTM, GRU, Dense, Average, Conv1D, Flatten
import numpy as np
from tensorflow.keras.backend import softmax, stack, random_uniform, squeeze
from tensorflow.keras.callbacks import TensorBoard, Callback, EarlyStopping
from tensorflow.keras import backend as K
import pickle
from tqdm import trange

os.environ["CUDA_VISIBLE_DEVICES"] = '0'


class Attention(Layer):
    def __init__(self, units):
        super(Attention, self).__init__()
        self.W = Dense(units, activation='tanh')
        self.context_vector = tf.Variable(random_uniform((units, 1), dtype='float32'))

    def call(self, sequences):
        features = self.W(sequences)
        attn_weights = softmax(tf.matmul(features, self.context_vector), axis=1)
        attn_weights = tf.expand_dims(tf.squeeze(attn_weights, 2), 1)
        seq_rep = tf.matmul(attn_weights, sequences)
        return squeeze(seq_rep, axis=1)


class BiLSTMAttn(Layer):
    def __init__(self, attn_size, rnn_size):
        super(BiLSTMAttn, self).__init__()
        self.bilstm = Bidirectional(LSTM(rnn_size,
                                         dropout=0.2,
                                         return_sequences=True,
                                         return_state=False,
                                         recurrent_activation='relu',
                                         recurrent_initializer='glorot_uniform'))
        self.attention = Attention(attn_size)

    def call(self, sequences):
        rnn = self.bilstm(sequences)
        sequence_rep = self.attention(rnn)
        return sequence_rep


class BiLSTMAttn3D(Layer):
    def __init__(self, attn_size1, attn_size2, rnn_size):
        super(BiLSTMAttn3D, self).__init__()
        self.bilstm1 = BiLSTMAttn(attn_size1, rnn_size)
        self.bilstm2 = BiLSTMAttn(attn_size2, rnn_size)

    def call(self, sequences3d):
        sub_reps = stack([self.bilstm1(sequences3d[:, i, :, :])
                          for i in range(sequences3d.shape[1])], axis=1)
        reps = self.bilstm2(sub_reps)
        return reps


class BiGRUAttn(Layer):
    def __init__(self, attn_size, rnn_size):
        super(BiGRUAttn, self).__init__()
        self.bigru = Bidirectional(GRU(rnn_size,
                                       dropout=0.2,
                                       return_sequences=True,
                                       return_state=False))
        # recurrent_activation='relu',
        # recurrent_initializer='glorot_uniform'))
        self.attention = Attention(attn_size)

    def call(self, sequences):
        rnn = self.bigru(sequences)
        sequence_rep = self.attention(rnn)
        return sequence_rep


class BiGRUAttn3D(Layer):
    def __init__(self, attn_size1, attn_size2, rnn_size1, rnn_size2):
        super(BiGRUAttn3D, self).__init__()
        self.bigru1 = BiGRUAttn(attn_size1, rnn_size1)
        self.bigru2 = BiGRUAttn(attn_size2, rnn_size2)

    def call(self, sequences3d):
        sub_reps = stack([self.bigru1(sequences3d[:, i, :, :])
                          for i in range(sequences3d.shape[1])], axis=1)
        reps = self.bigru2(sub_reps)
        return reps


class BimodalAttention(Layer):
    def __init__(self, units):
        super(BimodalAttention, self).__init__()
        self.W1 = Dense(units)
        self.W2 = Dense(units)
        self.W = Dense(units, activation='tanh')
        self.context_vector = tf.Variable(random_uniform((units, 1), dtype='float32'))

    def call(self, sequences1, sequences2):
        features1 = self.W1(sequences1)
        features2 = self.W2(sequences2)
        fusion = Concatenate()([features1, features2])
        features = self.W(fusion)
        attn_weights = softmax(tf.matmul(features, self.context_vector), axis=1)
        attn_weights = tf.expand_dims(tf.squeeze(attn_weights, 2), 1)
        seq_rep = tf.matmul(attn_weights, features)
        return squeeze(seq_rep, axis=1)


class BimodalAttentionTensorKernel(Layer):
    def __init__(self, units):
        super(BimodalAttentionTensorKernel, self).__init__()
        self.W1 = Dense(units)
        self.W2 = Dense(units)
        self.W = Dense(units, activation='tanh')
        self.context_vector = tf.Variable(random_uniform((units, 1), dtype='float32'))

    def call(self, sequences1, sequences2):
        features1 = self.W1(sequences1)
        features2 = self.W2(sequences2)
        fusion = Concatenate()([features1, features2])
        features = self.W(fusion)
        attn_weights = softmax(tf.matmul(features, self.context_vector), axis=1)
        attn_weights = tf.expand_dims(tf.squeeze(attn_weights, 2), 1)
        seq_rep = tf.matmul(attn_weights, Concatenate()([sequences1, sequences2]))
        return squeeze(seq_rep, axis=1)


class BimodalBiGRUAttn(Layer):
    def __init__(self, attn_size, rnn_size):
        super(BimodalBiGRUAttn, self).__init__()
        self.bigru1 = Bidirectional(GRU(rnn_size,
                                        dropout=0.2,
                                        return_sequences=True,
                                        return_state=False))
        self.bigru2 = Bidirectional(GRU(rnn_size,
                                        dropout=0.2,
                                        return_sequences=True,
                                        return_state=False))
        self.attention = BimodalAttention(attn_size)

    def call(self, sequences1, sequences2):
        rnn1 = self.bigru1(sequences1)
        rnn2 = self.bigru2(sequences2)
        sequence_rep = self.attention(rnn1, rnn2)
        return sequence_rep


class BimodalBiGRUAttn3D(Layer):
    def __init__(self, attn_size1, attn_size2, rnn_size1, rnn_size2):
        super(BimodalBiGRUAttn3D, self).__init__()
        self.bigru1 = BimodalBiGRUAttn(attn_size1, rnn_size1)
        self.bigru2 = BiGRUAttn(attn_size2, rnn_size2)

    def call(self, sequences3d1, sequences3d2):
        sub_reps = stack([self.bigru1(sequences3d1[:, i, :, :], sequences3d2[:, i, :, :])
                          for i in range(sequences3d1.shape[1])], axis=1)
        reps = self.bigru2(sub_reps)
        return reps


class PBiGRUAttn3D(Layer):
    def __init__(self, attn_size1, attn_size2, rnn_size1, rnn_size2, rnn_size3):
        super(PBiGRUAttn3D, self).__init__()
        self.bigru1 = BimodalBiGRUAttn(attn_size1, rnn_size1)
        self.bigru2 = BimodalBiGRUAttn(attn_size2, rnn_size2)
        self.bigru3 = Bidirectional(GRU(rnn_size3,
                                        dropout=0.2,
                                        return_sequences=True,
                                        return_state=False))

    def call(self, sequences3d1, sequences3d2, sequences3d3):
        rep_ia = stack([self.bigru1(sequences3d1[:, i, :, :], sequences3d2[:, i, :, :])
                        for i in range(sequences3d1.shape[1])], axis=1)
        rep_s = self.bigru3(sequences3d3)
        reps = stack([self.bigru2(rep_ia[:, i, :, :], rep_s[:, i, :, :])
                      for i in range(rep_ia.shape[1])], axis=1)
        return reps



class BimodalBiLSTMAttn(Layer):
    def __init__(self, attn_size, rnn_size):
        super(BimodalBiLSTMAttn, self).__init__()
        self.bilstm1 = Bidirectional(LSTM(rnn_size,
                                          dropout=0.2,
                                          return_sequences=True,
                                          return_state=False))
        self.bilstm2 = Bidirectional(LSTM(rnn_size,
                                          dropout=0.2,
                                          return_sequences=True,
                                          return_state=False))
        self.attention = BimodalAttention(attn_size)

    def call(self, sequences1, sequences2):
        rnn1 = self.bilstm1(sequences1)
        rnn2 = self.bilstm2(sequences2)
        sequence_rep = self.attention(rnn1, rnn2)
        return sequence_rep


class BimodalBiLSTMAttn3D(Layer):
    def __init__(self, attn_size1, attn_size2, rnn_size1, rnn_size2):
        super(BimodalBiLSTMAttn3D, self).__init__()
        self.bilstm1 = BimodalBiLSTMAttn(attn_size1, rnn_size1)
        self.bilstm2 = BiLSTMAttn(attn_size2, rnn_size2)

    def call(self, sequences3d1, sequences3d2):
        sub_reps = stack([self.bilstm1(sequences3d1[:, i, :, :], sequences3d2[:, i, :, :])
                          for i in range(sequences3d1.shape[1])], axis=1)
        reps = self.bilstm2(sub_reps)
        return reps


class EarlyStoppingByAccVal(Callback):
    def __init__(self, monitor='accuracy', value=0.99, verbose=0):
        super(Callback, self).__init__()
        self.monitor = monitor
        self.value = value
        self.verbose = verbose

    def on_epoch_end(self, epoch, logs):
        current = logs.get(self.monitor)
        if current >= self.value:
            if self.verbose > 0:
                print("Epoch %05d: early stopping THR" % epoch)
            self.model.stop_training = True


def recall_m(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())
    return recall


def precision_m(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision


def f1_m(y_true, y_pred):
    precision = precision_m(y_true, y_pred)
    recall = recall_m(y_true, y_pred)
    return 2*((precision*recall)/(precision+recall+K.epsilon()))

##
if __name__ == '__main__':
    # from wanghong.utils import DATA_DIR

    DATA_DIR = '/home/cchen/data/wanghong'
    # y_train = np.load(os.path.join(DATA_DIR, 'y_train.npy'))
    # y_test = np.load(os.path.join(DATA_DIR, 'y_valid.npy'))
    #
    # Xtrn_train = np.load(os.path.join(DATA_DIR, 'X_trn_train.npy'))
    # Xtrn_test = np.load(os.path.join(DATA_DIR, 'X_trn_valid.npy'))
    # # XXtrn_train = np.array([line[1] for line in Xtrn_train])
    # # XXtrn_test = np.array([line[1] for line in Xtrn_test])
    #
    # Xirv2_train = np.load(os.path.join(DATA_DIR, 'X_irv2_train.npy'))
    # Xirv2_test = np.load(os.path.join(DATA_DIR, 'X_irv2_valid.npy'))
    # XXtrn_train = np.array([line[0] for line in Xtrn_train])
    # XXirv2_train = np.array([line[0] for line in Xirv2_train])
    #
    # Xw2v_train = np.load(os.path.join(DATA_DIR, 'X_w2v_train.npy'))
    # Xw2v_test = np.load(os.path.join(DATA_DIR, 'X_w2v_valid.npy'))

    y = np.load(os.path.join(DATA_DIR, 'data_300', 'y.npy'))
    Xtrn = np.load(os.path.join(DATA_DIR, 'data_300', 'X_trn.npy'))
    Xirv2 = np.load(os.path.join(DATA_DIR, 'data_300', 'X_irv2.npy'))
    Xw2v = np.load(os.path.join(DATA_DIR, 'data_300', 'X_w2v.npy'))

    y_train = y[:240]
    y_valid = y[-60:]
    Xtrn_train = Xtrn[:240]
    Xtrn_valid = Xtrn[-60:]
    Xirv2_train = Xirv2[:240]
    Xirv2_valid = Xirv2[-60:]
    Xw2v_train = Xw2v[:240]
    Xw2v_valid = Xw2v[-60:]

    # Xtrn_test = np.load(os.path.join(DATA_DIR, 'data_300', 'X_trn_test.npy'))
    # Xirv2_test = np.load(os.path.join(DATA_DIR, 'data_300', 'X_irv2_test.npy'))
    # Xw2v_test = np.load(os.path.join(DATA_DIR, 'data_300', 'X_w2v_test.npy'))

    # sequences = Input(shape=Xirv2_train.shape[1:], dtype='float32')
    # video = BiGRUAttn3D(50, 20, 100)(sequences)
    # output = Dense(1, activation='sigmoid')(video)
    # model = Model(inputs=sequences, outputs=output)
    # adam = tf.keras.optimizers.Adam(lr=0.0001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)
    # model.compile(optimizer=adam, loss='binary_crossentropy', metrics=['accuracy'])
    # early_stop = EarlyStopping(monitor='loss', min_delta=0, patience=5, verbose=0, mode='auto')
    # tensorboard = TensorBoard(log_dir='mytensorboard', write_graph=True, write_images=True)
    # history = model.fit(Xirv2_train, y_train, epochs=50, batch_size=200, verbose=1
    #                     , callbacks=[tensorboard], shuffle=True
    #                     # , validation_split=0.25)
    #                     , validation_data=(Xirv2_test, y_test))
    # model.evaluate(Xirv2_test, y_test)

    # optimizers = ['Adam', 'SGD', 'Adagrad', 'RMSprop', 'AdaDelta']
    # layers = [(int(50 * i // 2), int(20 * i // 2), int(100 * i // 2), int(40 * i // 2)) for i in range(1, 7)]
    # finals = ['sigmoid', 'tanh']
    #
    # ress = []
    # for optimizer in optimizers:
    #     for layer in layers:
    #         for final in finals:
    #             print(optimizer, layer, final)
    # sequences1 = Input(shape=Xtrn_train.shape[1:], dtype='float32')
    # sequences2 = Input(shape=Xirv2_train.shape[1:], dtype='float32')
    # sequences3 = Input(shape=Xw2v_train.shape[1:], dtype='float32')
    # video = BimodalBiGRUAttn3D(100, 40, 200, 80)(sequences1, sequences2)
    # text = BiGRUAttn3D(100, 40, 200, 80)(sequences3)
    # # fusion = Concatenate()([video, text])
    #
    # output1 = Dense(1, activation='sigmoid')(video)
    # output2 = Dense(1, activation='sigmoid')(text)
    # output = Average()([output1, output2])
    # model = Model(inputs=[sequences1, sequences2, sequences3], outputs=output)
    # model.compile(optimizer='adagrad', loss='binary_crossentropy', metrics=['accuracy', f1_m, precision_m, recall_m])
    # # early_stop = EarlyStopping(monitor='loss', min_delta=0, patience=1, verbose=0, mode='auto', restore_best_weights=True)
    # # early_stop = EarlyStopping(monitor='accuracy', baseline=0.99, patience=2, verbose=0, mode='auto',)
    # early_stop = EarlyStoppingByAccVal(monitor='accuracy', value=0.9)
    # tensorboard = TensorBoard(log_dir='mytensorboard', write_graph=True, write_images=True)
    # history = model.fit([Xtrn_train, Xirv2_train, Xw2v_train], y_train, epochs=50, batch_size=200, verbose=1
    #                     , callbacks=[tensorboard, early_stop]
    #                     # , validation_split=0.25)
    #                     , validation_data=([Xtrn_valid, Xirv2_valid, Xw2v_valid], y_valid))
    # this_res = ['gru', optimizer, *layer, final, *model.evaluate([Xtrn_test, Xirv2_test, Xw2v_test], y_test)]
    # ress.append(this_res)
    # with open('res_gru.txt', 'a') as o:
    #     csvwriter = csv.writer(o)
    #     csvwriter.writerow(this_res)
    early_stop_acc = EarlyStoppingByAccVal(monitor='accuracy', value=0.95)
    early_stop = EarlyStopping(monitor='val_accuracy', min_delta=0, patience=5, verbose=0, mode='auto')
    early_stop_loss = EarlyStopping(monitor='loss', min_delta=0, patience=5, verbose=0, mode='auto')
    tensorboard = TensorBoard(log_dir='mytensorboard', write_graph=True, write_images=True)

    candidates = [i * 20 for i in range(4, 10)] + [150]
    # attn_size1, attn_size2, rnn_size1, rnn_size2
    layers = []
    for rnn_size1 in candidates:
        for attn_size1 in candidates:
            for rnn_size2 in candidates:
                for attn_size2 in candidates:
                    if rnn_size1 > attn_size1 > rnn_size2 > attn_size2:
                        layers.append([attn_size1, attn_size2, rnn_size1, rnn_size2])
    random.seed(1)
    layers = random.sample(layers, len(layers))

    epochs = 100
    batch_size = 50
    verbose = 1

    # 3-way model
    for seed in range(100):
        np.random.seed(seed)
        tf.random.set_seed(seed)
        sequences1 = Input(shape=Xtrn_train.shape[1:], dtype='float32')
        sequences2 = Input(shape=Xirv2_train.shape[1:], dtype='float32')
        sequences3 = Input(shape=Xw2v_train.shape[1:], dtype='float32')
        video = BimodalBiGRUAttn3D(150, 80, 160, 140)(sequences1, sequences2)
        text = BiGRUAttn3D(150, 100, 160, 120)(sequences3)
        fusion = Concatenate()([video, text])
        fusion = Dense(280)(fusion)
        output = Dense(1, activation='sigmoid')(fusion)
        model = Model(inputs=[sequences1, sequences2, sequences3], outputs=output)
        model.compile(optimizer='Adagrad', loss='binary_crossentropy', metrics=['accuracy', f1_m, precision_m, recall_m])
        model.fit([Xtrn_train, Xirv2_train, Xw2v_train], y_train, epochs=epochs, batch_size=batch_size, verbose=verbose
                            , callbacks=[early_stop_loss]
                            , validation_data=([Xtrn_valid, Xirv2_valid, Xw2v_valid], y_valid))
        res0 = model.evaluate([Xtrn_valid, Xirv2_valid, Xw2v_valid], y_valid)


        # np.random.seed(seed)
        # tf.random.set_seed(seed)
        # sequences1 = Input(shape=Xtrn_train.shape[1:], dtype='float32')
        # sequences2 = Input(shape=Xirv2_train.shape[1:], dtype='float32')
        # sequences3 = Input(shape=Xw2v_train.shape[1:], dtype='float32')
        # video = BiGRUAttn3D(150, 80, 160, 140)(sequences1)
        # trn = BiGRUAttn3D(150, 80, 160, 140)(sequences2)
        # text = BiGRUAttn3D(150, 100, 160, 120)(sequences3)
        # fusion = Concatenate()([video, trn, text])
        # fusion = Dense(280)(fusion)
        # output = Dense(1, activation='sigmoid')(fusion)
        # # output1 = Dense(1, activation='sigmoid')(video)
        # # output2 = Dense(1, activation='sigmoid')(trn)
        # # output3 = Dense(1, activation='sigmoid')(text)
        # # output = Average()([output1, output2, output3])
        # model = Model(inputs=[sequences1, sequences2, sequences3], outputs=output)
        # model.compile(optimizer='Adagrad', loss='binary_crossentropy', metrics=['accuracy', f1_m, precision_m, recall_m])
        # model.fit([Xtrn_train, Xirv2_train, Xw2v_train], y_train, epochs=epochs, batch_size=batch_size, verbose=verbose
        #                     , callbacks=[early_stop_loss]
        #                     , validation_data=([Xtrn_valid, Xirv2_valid, Xw2v_valid], y_valid))
        # res01 = model.evaluate([Xtrn_valid, Xirv2_valid, Xw2v_valid], y_valid)
        #
        #
        # with open('_our_latefuse.csv', 'a') as o:
        #     csvwriter = csv.writer(o)
        #     csvwriter.writerow([seed] + res01)


        # tsn
        # np.random.seed(seed)
        # tf.random.set_seed(seed)
        # sequences1 = Input(shape=Xtrn_train.shape[1:], dtype='float32')
        # sequences2 = Input(shape=Xirv2_train.shape[1:], dtype='float32')
        # c1 = stack([Conv1D(3, 3, activation='tanh', input_shape=Xtrn_train.shape[1:])(sequences1[:, i, :, :])
        #             for i in range(sequences1.shape[1])], axis=1)
        # c2 = stack([Conv1D(3, 3, activation='tanh', input_shape=Xirv2_train.shape[1:])(sequences2[:, i, :, :])
        #             for i in range(sequences2.shape[1])], axis=1)
        # fusion = Concatenate()([c1, c2])
        # f = Flatten()(fusion)
        # output = Dense(1, activation='sigmoid')(f)
        #
        # model = Model(inputs=[sequences1, sequences2], outputs=output)
        # model.compile(optimizer='Adagrad', loss='binary_crossentropy',
        #               metrics=['accuracy', f1_m, precision_m, recall_m])
        # model.fit([Xtrn_train, Xirv2_train], y_train, epochs=epochs, batch_size=batch_size, verbose=verbose
        #           , callbacks=[early_stop_loss]
        #           , validation_data=([Xtrn_valid, Xirv2_valid], y_valid))
        # res01 = model.evaluate([Xtrn_valid, Xirv2_valid], y_valid)
        # print(res01)
        # with open('_our_tsn.csv', 'a') as o:
        #     csvwriter = csv.writer(o)
        #     csvwriter.writerow([seed] + res01)


    # layers = layers[49:]
    # for seed in range(1, 100):
    #     for i in trange(len(layers)):

    # layer = layers[i]

    # layer = [140, 100, 200, 120]
    # layer = [200,80,220,160]
    # layer = [200,100,240,180]
    # layer = [160,100,220,150]
    # layer = [150,80,160,140]

    # out = [*layer]

    # 3-way model
    # np.random.seed(seed)
    # tf.random.set_seed(seed)
    # sequences1 = Input(shape=Xtrn_train.shape[1:], dtype='float32')
    # sequences2 = Input(shape=Xirv2_train.shape[1:], dtype='float32')
    # sequences3 = Input(shape=Xw2v_train.shape[1:], dtype='float32')
    # video = BimodalBiGRUAttn3D(*layer)(sequences1, sequences2)
    # text = BiGRUAttn3D(*layer)(sequences3)
    # fusion = Concatenate()([video, text])
    # fusion = Dense(280)(fusion)
    # output = Dense(1, activation='sigmoid')(fusion)
    # model = Model(inputs=[sequences1, sequences2, sequences3], outputs=output)
    # model.compile(optimizer='Adagrad', loss='binary_crossentropy', metrics=['accuracy', f1_m, precision_m, recall_m])
    # model.fit([Xtrn_train, Xirv2_train, Xw2v_train], y_train, epochs=epochs, batch_size=batch_size, verbose=verbose
    #                     , callbacks=[early_stop]
    #                     , validation_data=([Xtrn_valid, Xirv2_valid, Xw2v_valid], y_valid))
    # res0 = model.evaluate([Xtrn_valid, Xirv2_valid, Xw2v_valid], y_valid)
    # with open('_our.csv', 'a') as o:
    #     csvwriter = csv.writer(o)
    #     csvwriter.writerow([seed] + layer + res0)
    # pred = model.predict([Xtrn_test, Xirv2_test, Xw2v_test])
    # pred = (pred >= 0.5).astype(int).squeeze()
    # with open(os.path.join(DATA_DIR, 'data_300', 'y_pred.txt'), 'w') as o:
    #     for y_pred in pred:
    #         o.write(str(y_pred) + '\n')

    ################################################ 3-way model test needs debug
    # np.random.seed(1)
    # tf.random.set_seed(1)
    # sequences1 = Input(shape=Xtrn_train.shape[1:], dtype='float32')
    # sequences2 = Input(shape=Xirv2_train.shape[1:], dtype='float32')
    # sequences3 = Input(shape=Xw2v_train.shape[1:], dtype='float32')
    # # video = BimodalBiGRUAttn3D(*layer)(sequences1, sequences2)
    # # fusion = BimodalBiGRUAttn3D(*layer)(video, sequences3)
    # fusion = PBiGRUAttn3D(150,80,160,140,280)(sequences1, sequences2, sequences3)
    # # fusion = Dense(280)(fusion)
    # output = Dense(1, activation='sigmoid')(fusion)
    # model = Model(inputs=[sequences1, sequences2, sequences3], outputs=output)
    # model.compile(optimizer='Adagrad', loss='binary_crossentropy', metrics=['accuracy', f1_m, precision_m, recall_m])
    # model.fit([Xtrn_train, Xirv2_train, Xw2v_train], y_train, epochs=epochs, batch_size=batch_size, verbose=verbose
    #                     , callbacks=[early_stop]
    #                     , validation_data=([Xtrn_valid, Xirv2_valid, Xw2v_valid], y_valid))
    # res0 = model.evaluate([Xtrn_valid, Xirv2_valid, Xw2v_valid], y_valid)
    # pred = model.predict([Xtrn_test, Xirv2_test, Xw2v_test])
    # pred = (pred >= 0.5).astype(int).squeeze()
    ################################################################################################################################################

    #     # 3-way late
    #     np.random.seed(1)
    #     tf.random.set_seed(1)
    #     sequences1 = Input(shape=Xtrn_train.shape[1:], dtype='float32')
    #     sequences2 = Input(shape=Xirv2_train.shape[1:], dtype='float32')
    #     sequences3 = Input(shape=Xw2v_train.shape[1:], dtype='float32')
    #     video = BiGRUAttn3D(*layer)(sequences1)
    #     trn = BiGRUAttn3D(*layer)(sequences2)
    #     text = BiGRUAttn3D(*layer)(sequences3)
    #     fusion = Concatenate()([video, trn, text])
    #     fusion = Dense(280)(fusion)
    #     output = Dense(1, activation='sigmoid')(fusion)
    #     # output1 = Dense(1, activation='sigmoid')(video)
    #     # output2 = Dense(1, activation='sigmoid')(trn)
    #     # output3 = Dense(1, activation='sigmoid')(text)
    #     # output = Average()([output1, output2, output3])
    #     model = Model(inputs=[sequences1, sequences2, sequences3], outputs=output)
    #     model.compile(optimizer='Adagrad', loss='binary_crossentropy', metrics=['accuracy', f1_m, precision_m, recall_m])
    #     model.fit([Xtrn_train, Xirv2_train, Xw2v_train], y_train, epochs=epochs, batch_size=batch_size, verbose=verbose
    #                         , callbacks=[early_stop]
    #                         , validation_data=([Xtrn_valid, Xirv2_valid, Xw2v_valid], y_valid))
    #     res01 = model.evaluate([Xtrn_valid, Xirv2_valid, Xw2v_valid], y_valid)
    #
    #     # model fusion
    #     np.random.seed(1)
    #     tf.random.set_seed(1)
    #     sequences1 = Input(shape=Xtrn_train.shape[1:], dtype='float32')
    #     sequences2 = Input(shape=Xirv2_train.shape[1:], dtype='float32')
    #     video = BimodalBiGRUAttn3D(*layer)(sequences1, sequences2)
    #     output = Dense(1, activation='sigmoid')(video)
    #     model = Model(inputs=[sequences1, sequences2], outputs=output)
    #     model.compile(optimizer='Adagrad', loss='binary_crossentropy', metrics=['accuracy', f1_m, precision_m, recall_m])
    #     model.fit([Xtrn_train, Xirv2_train], y_train, epochs=epochs, batch_size=batch_size, verbose=verbose
    #                         , callbacks=[early_stop]
    #                         , validation_data=([Xtrn_valid, Xirv2_valid], y_valid))
    #     res1 = model.evaluate([Xtrn_valid, Xirv2_valid], y_valid, verbose=verbose)
    #     if res1[1] < 0.83:
    #         continue
    #     out += [*res1]
    #     # d = history.history
    #     # out += [d['val_accuracy'], d['val_f1_m'], d['val_precision_m'], d['val_recall_m']]
    #     # with open(f'{DATA_DIR}/models/model/{layer[0]}_{layer[1]}_{layer[2]}_{layer[3]}.pkl', 'wb') as o:
    #     #     pickle.dump(history.history, o)
    #     # 50. 0.81666666, 0.82555777, 0.78888893, 0.86607146
    #
    #     # late fusion
    #     np.random.seed(1)
    #     tf.random.set_seed(1)
    #     sequences1 = Input(shape=Xtrn_train.shape[1:], dtype='float32')
    #     sequences2 = Input(shape=Xirv2_train.shape[1:], dtype='float32')
    #     video = BiGRUAttn3D(*layer)(sequences1)
    #     trn = BiGRUAttn3D(*layer)(sequences2)
    #     output1 = Dense(1, activation='sigmoid')(video)
    #     output2 = Dense(1, activation='sigmoid')(trn)
    #     output = Average()([output1, output2])
    #     model = Model(inputs=[sequences1, sequences2], outputs=output)
    #     model.compile(optimizer='Adagrad', loss='binary_crossentropy', metrics=['accuracy', f1_m, precision_m, recall_m])
    #     model.fit([Xtrn_train, Xirv2_train], y_train, epochs=epochs, batch_size=batch_size, verbose=verbose
    #                         , callbacks=[early_stop]
    #                         , validation_data=([Xtrn_valid, Xirv2_valid], y_valid))
    #     res2 = model.evaluate([Xtrn_valid, Xirv2_valid], y_valid, verbose=verbose)
    #
    #     np.random.seed(1)
    #     tf.random.set_seed(1)
    #     # sequences1 = Input(shape=Xtrn_train.shape[1:], dtype='float32')
    #     sequences2 = Input(shape=Xirv2_train.shape[1:], dtype='float32')
    #     sequences3 = Input(shape=Xw2v_train.shape[1:], dtype='float32')
    #     # video = BiGRUAttn3D(*layer)(sequences1)
    #     trn = BiGRUAttn3D(*layer)(sequences2)
    #     text = BiGRUAttn3D(*layer)(sequences3)
    #     # output1 = Dense(1, activation='sigmoid')(video)
    #     output2 = Dense(1, activation='sigmoid')(trn)
    #     output3 = Dense(1, activation='sigmoid')(text)
    #     output = Average()([output2, output3])
    #     model = Model(inputs=[sequences2, sequences3], outputs=output)
    #     model.compile(optimizer='Adagrad', loss='binary_crossentropy', metrics=['accuracy', f1_m, precision_m, recall_m])
    #     model.fit([Xirv2_train, Xw2v_train], y_train, epochs=epochs, batch_size=batch_size, verbose=verbose
    #                         , callbacks=[early_stop]
    #                         , validation_data=([Xirv2_valid, Xw2v_valid], y_valid))
    #     res21 = model.evaluate([Xirv2_valid, Xw2v_valid], y_valid)
    #
    #     if res2[1] > res1[1]:
    #         continue
    #     out += [*res2]
    #     # d = history.history
    #     # out += [d['val_accuracy'], d['val_f1_m'], d['val_precision_m'], d['val_recall_m']]
    #     # with open(f'{DATA_DIR}/models/late/{layer[0]}_{layer[1]}_{layer[2]}_{layer[3]}.pkl', 'wb') as o:
    #     #     pickle.dump(history.history, o)
    #
    #     # early fusion
    #     np.random.seed(1)
    #     tf.random.set_seed(2)
    #     sequences1 = Input(shape=Xtrn_train.shape[1:], dtype='float32')
    #     sequences2 = Input(shape=Xirv2_train.shape[1:], dtype='float32')
    #     sequences = Concatenate(axis=3)([sequences1, sequences2])
    #     video = BiGRUAttn3D(*layer)(sequences)
    #     output = Dense(1, activation='sigmoid')(video)
    #     model = Model(inputs=[sequences1, sequences2], outputs=output)
    #     model.compile(optimizer='Adagrad', loss='binary_crossentropy', metrics=['accuracy', f1_m, precision_m, recall_m])
    #     model.fit([Xtrn_train, Xirv2_train], y_train, epochs=epochs, batch_size=batch_size, verbose=verbose
    #                         , callbacks=[early_stop]
    #                         , validation_data=([Xtrn_valid, Xirv2_valid], y_valid))
    #     res3 = model.evaluate([Xtrn_valid, Xirv2_valid], y_valid, verbose=verbose)
    #     out += [*res3]
    #     # d = history.history
    #     # out += [d['val_accuracy'], d['val_f1_m'], d['val_precision_m'], d['val_recall_m']]
    #     # with open(f'{DATA_DIR}/models/early/{layer[0]}_{layer[1]}_{layer[2]}_{layer[3]}.pkl', 'wb') as o:
    #     #     pickle.dump(history.history, o)
    #
    # this_X = Xirv2_train
    # this_Xt = Xirv2_valid
    # np.random.seed(seed)
    # tf.random.set_seed(seed)
    # sequences3 = Input(shape=this_X.shape[1:], dtype='float32')
    # text = BiGRUAttn3D(*layer)(sequences3)
    # output = Dense(1, activation='sigmoid')(text)
    # model = Model(inputs=sequences3, outputs=output)
    # model.compile(optimizer='Adagrad', loss='binary_crossentropy', metrics=['accuracy', f1_m, precision_m, recall_m])
    # model.fit(this_X, y_train, epochs=epochs, batch_size=batch_size, verbose=verbose
    #                     , callbacks=[early_stop_loss]
    #                     , validation_data=(this_Xt, y_valid))
    # res4 = model.evaluate(this_Xt, y_valid, verbose=verbose)
    # with open('_irv2_loss.csv', 'a') as o:
    #     csvwriter = csv.writer(o)
    #     csvwriter.writerow([seed] + layer + res4)
    # out += [*res4]
    # d = history.history
    # out += [d['val_accuracy'], d['val_f1_m'], d['val_precision_m'], d['val_recall_m']]

    # this_X = Xtrn_train
    # this_Xt = Xtrn_valid
    # np.random.seed(seed)
    # tf.random.set_seed(seed)
    # sequences3 = Input(shape=this_X.shape[1:], dtype='float32')
    # text = BiGRUAttn3D(*layer)(sequences3)
    # output = Dense(1, activation='sigmoid')(text)
    # model = Model(inputs=sequences3, outputs=output)
    # model.compile(optimizer='Adagrad', loss='binary_crossentropy', metrics=['accuracy', f1_m, precision_m, recall_m])
    # model.fit(this_X, y_train, epochs=epochs, batch_size=batch_size, verbose=verbose
    #                     , callbacks=[early_stop_loss]
    #                     , validation_data=(this_Xt, y_valid))
    # res5 = model.evaluate(this_Xt, y_valid, verbose=verbose)
    # with open('_trn_loss.csv', 'a') as o:
    #     csvwriter = csv.writer(o)
    #     csvwriter.writerow([seed] + layer + res5)
    # if res2[1] <= res5[1]:
    #     continue
    # out += [*res5]

    # this_X = Xw2v_train
    # this_Xt = Xw2v_valid
    # np.random.seed(seed)
    # tf.random.set_seed(seed)
    # sequences3 = Input(shape=this_X.shape[1:], dtype='float32')
    # text = BiGRUAttn3D(*layer)(sequences3)
    # output = Dense(1, activation='sigmoid')(text)
    # model = Model(inputs=sequences3, outputs=output)
    # model.compile(optimizer='Adagrad', loss='binary_crossentropy', metrics=['accuracy', f1_m, precision_m, recall_m])
    # model.fit(this_X, y_train, epochs=epochs, batch_size=batch_size, verbose=verbose
    #                     , callbacks=[early_stop_loss]
    #                     , validation_data=(this_Xt, y_valid))
    # res6 = model.evaluate(this_Xt, y_valid, verbose=verbose)
    # with open('_txt_loss.csv', 'a') as o:
    #     csvwriter = csv.writer(o)
    #     csvwriter.writerow([seed] + layer + res6)
    # d = history.history
    # out += [d['val_accuracy'], d['val_f1_m'], d['val_precision_m'], d['val_recall_m']]


    # this_X = Xw2v_train
    # this_Xt = Xw2v_valid
    # np.random.seed(seed)
    # tf.random.set_seed(seed)
    # sequences3 = Input(shape=this_X.shape[1:], dtype='float32')
    # text = BiGRUAttn3D(*layer)(sequences3)
    # output = Dense(1, activation='sigmoid')(text)
    # model = Model(inputs=sequences3, outputs=output)
    # model.compile(optimizer='Adagrad', loss='binary_crossentropy', metrics=['accuracy', f1_m, precision_m, recall_m])
    # history = model.fit(this_X, y_train, epochs=50, batch_size=batch_size, verbose=1
    #                     , callbacks=[early_stop]
    #                     , validation_data=(this_Xt, y_valid))
    # res = model.evaluate(this_Xt, y_valid)
    # with open('txt.csv', 'a') as o:
    #     csvwriter = csv.writer(o)
    #     csvwriter.writerow([seed] + res)
    #
    #     # with open('res3_gridsearch.csv', 'a') as o:
    #     #     csvwriter = csv.writer(o)
    #     #     csvwriter.writerow(out)
    #
    #
    #     # with open(f'{DATA_DIR}/models/early/{layer[0]}_{layer[1]}_{layer[2]}_{layer[3]}.pkl', 'wb') as o:
    #     #     pickle.dump(history.history, o)
    #
    #
    #
    # # from glob import glob
    # # import os
    # # import pickle
    # # import pandas as pd
    # # out = []
    # # for fp in glob('/home/cchen/data/wanghong/models/model/*.pkl'):
    # #     layer = os.path.relpath(fp, '/home/cchen/data/wanghong/models/model/').split('.')[0].split('_')
    # #     with open(fp, 'rb') as i:
    # #         d = pickle.load(i)
    # #     for cnt, it in enumerate(zip(d['val_accuracy'], d['val_f1_m'], d['val_precision_m'], d['val_recall_m'])):
    # #         out.append(layer + [cnt + 1] + list(it))
    # #
    # # a = pd.DataFrame(out)
    # # a.to_csv('res_tmp.csv', index=False, header=False)