# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 4/6/20
# @File  : [wanghong] mmml.py


import os

import tensorflow as tf

tf.config.experimental_run_functions_eagerly(True)

from tensorflow import keras
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Input, Layer, Concatenate, Bidirectional, LSTM, GRU, Dense, Flatten, Softmax
import numpy as np
from tensorflow.keras.backend import tanh, softmax, stack, mean, concatenate
from tensorflow.keras.callbacks import EarlyStopping, TensorBoard


os.environ["CUDA_VISIBLE_DEVICES"] = '0'


class Attention(Layer):
    def __init__(self, units):
        super(Attention, self).__init__()
        self.W1 = tf.keras.layers.Dense(units)
        self.W2 = tf.keras.layers.Dense(units)
        self.V = tf.keras.layers.Dense(1)

    def call(self, features, hidden):
        # Bahdanau
        hidden_with_time_axis = tf.expand_dims(hidden, 1)
        score = tanh(self.W1(features) + self.W2(hidden_with_time_axis))
        attention_weights = softmax(self.V(score), axis=1)
        context_vector = attention_weights * features
        context_vector = tf.reduce_sum(context_vector, axis=1)
        return context_vector, attention_weights
    # def call(self):
    #     # https://www.cs.cmu.edu/~./hovy/papers/16HLT-hierarchical-attention-networks.pdf
    #     embedding = Dense(unit, activation='tanh', )(hidden)
    #     attention_weights = Activation('softmax')(embedding * context_vector)
    #     summarized_vector = sum(attention_weights * hidden)


class BiGRUAttn(Layer):
    def __init__(self, attn_size, rnn_size):
        super(BiGRUAttn, self).__init__()
        self.attn_size = attn_size
        self.rnn_size = rnn_size
        self.bigru = Bidirectional(GRU(rnn_size,
                                       dropout=0.2,
                                       return_sequences=True,
                                       return_state=True))
        self.attention = Attention(attn_size)

    def call(self, embedded_sequences):
        rnn, forward_h, backward_h = self.bigru(embedded_sequences)
        hidden_state = Concatenate()([forward_h, backward_h])
        context_vector, attention_weights = self.attention(rnn, hidden_state)
        return context_vector


class BiLSTMAttn(Layer):
    def __init__(self, attn_size, rnn_size):
        super(BiLSTMAttn, self).__init__()
        self.attn_size = attn_size
        self.rnn_size = rnn_size
        self.bilstm = Bidirectional(LSTM(rnn_size,
                                         dropout=0.2,
                                         return_sequences=True,
                                         return_state=True,
                                         recurrent_activation='relu',
                                         recurrent_initializer='glorot_uniform'))
        self.attention = Attention(attn_size)

    def call(self, embedded_sequences):
        rnn, forward_h, forward_c, backward_h, backward_c = self.bilstm(embedded_sequences)
        hidden_state = Concatenate()([forward_h, backward_h])
        context_vector, attention_weights = self.attention(rnn, hidden_state)
        return context_vector


class BiGRUHierarchicalAttn(Layer):
    def __init__(self, attn_size, rnn_size):
        super(BiGRUHierarchicalAttn, self).__init__()
        self.attn_size = attn_size
        self.rnn_size = rnn_size
        self.bigru1 = BiGRUAttn(attn_size, rnn_size)
        self.bigru2 = BiGRUAttn(attn_size, rnn_size)

    def call(self, embedded_sequences):
        attns = stack([self.bigru1(embedded_sequences[:, i, :, :]) for i in range(5)], axis=1)
        attn = self.bigru2(attns)
        return attn


def UnimodalBiGRUHierarchicalAttn(input_shape):
    rnn_size = 100
    model = Sequential([
        Input(shape=input_shape, dtype='float32'),
        BiGRUHierarchicalAttn(20, rnn_size),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model


class BimodalAttention(Layer):
    def __init__(self, units):
        super(BimodalAttention, self).__init__()
        self.W1 = tf.keras.layers.Dense(units)
        self.W2 = tf.keras.layers.Dense(units)

    def call(self, features1, features2):
        feature = softmax(self.W1(features1) + softmax(self.W2(features1)))

        return feature


class BimodalBiGRUAttention(Layer):
    def __init__(self, attn_size, rnn_size):
        super(BimodalBiGRUAttention, self).__init__()
        self.attn_size = attn_size
        self.rnn_size = rnn_size
        self.bigru1 = Bidirectional(GRU(rnn_size,
                                       dropout=0.2,
                                       return_sequences=True,
                                       return_state=False))
        self.bigru2 = Bidirectional(GRU(rnn_size,
                                       dropout=0.2,
                                       return_sequences=True,
                                       return_state=False))
        self.attention1 = BimodalAttention(attn_size)
        self.attention2 = Attention(attn_size)

    # def call(self, sequences1, sequences2):
    #     rnn1 = self.bigru1(sequences1)
    #     rnn2 = self.bigru2(sequences2)
    #     fusion = self.attention1(rnn1, rnn2)
    #     rnn, forward_h, backward_h = self.bigru3(fusion)
    #     hidden_state = Concatenate()([forward_h, backward_h])
    #     context_vector, attention_weights = self.attention2(rnn, hidden_state)
    #     return context_vector
    def call(self, sequences1, sequences2):
        rnn1, forward_h1, backward_h1 = self.bigru1(sequences1)
        rnn2, forward_h2, backward_h2 = self.bigru1(sequences1)
        rnn = self.attention1([rnn1, rnn2])
        hidden_state = Concatenate()([forward_h1, backward_h1])
        context_vector, attention_weights = self.attention(rnn, hidden_state)
        # fusion = self.attention1(sequences1, sequences2)
        # rnn, forward_h, backward_h = self.bigru(fusion)
        # hidden_state = Concatenate()([forward_h, backward_h])
        # context_vector, attention_weights = self.attention2(rnn, hidden_state)
        return context_vector


class BimodalBiGRUHierarchicalAttention(Layer):
    def __init__(self, attn_size, rnn_size):
        super(BimodalBiGRUHierarchicalAttention, self).__init__()
        self.attn_size = attn_size
        self.rnn_size = rnn_size
        self.bigru1 = BimodalBiGRUAttention(attn_size, rnn_size)
        self.bigru2 = BiGRUAttn(attn_size, rnn_size)

    def call(self, sequences1, sequences2):
        # return self.bigru1(sequences1[:, i, :, :], sequences2[:, i, :, :])
        attns = stack([self.bigru1(sequences1[:, i, :, :], sequences2[:, i, :, :]) for i in range(5)], axis=1)
        attn = self.bigru2(attns)
        return attn

def BimodalBiGRUHierarchicalAttnHidden(input1_shape, input2_shape):
    rnn_size = 100

    input1 = Input(shape=input1_shape, dtype='float32')
    input2 = Input(shape=input2_shape, dtype='float32')
    attn = BimodalBiGRUHierarchicalAttention(20, rnn_size)(input1, input2)
    output = Dense(1, activation='sigmoid')(attn)

    model = Model(inputs=[input1, input2], outputs=output)
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def BimodalBiGRUHierarchicalAttnConcatenate(input1_shape, input2_shape):
    rnn_size = 100

    input1 = Input(shape=input1_shape, dtype='float32')
    attn1 = BiGRUHierarchicalAttn(20, rnn_size)(input1)
    attn1 = softmax(attn1)

    input2 = Input(shape=input2_shape, dtype='float32')
    attn2 = BiGRUHierarchicalAttn(20, rnn_size)(input2)
    attn2 = softmax(attn2)

    fusion = concatenate([attn1, attn2])
    output = Dense(1, activation='sigmoid')(fusion)

    model = Model(inputs=[input1, input2], outputs=output)
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model


if __name__ == '__main__':

    y_train = np.load('video/mmml/y_train.npy')
    y_test = np.load('video/mmml/y_test.npy')

    Xtrn_train = np.load('video/mmml/trn_train.npy')
    Xtrn_test = np.load('video/mmml/trn_test.npy')

    Xirv2_train = np.load('video/mmml/irv2_train.npy')
    Xirv2_test = np.load('video/mmml/irv2_test.npy')

    Xw2v_train = np.load('video/mmml/w2v_train.npy')
    Xw2v_test = np.load('video/mmml/w2v_test.npy')


    # model = UnimodalBiGRUHierarchicalAttn(Xtrn_train.shape[1:])
    # model = BimodalBiGRUHierarchicalAttnHidden(Xtrn_train.shape[1:], Xirv2_train.shape[1:])



    rnn_size = 100

    input1 = Input(shape=Xtrn_train.shape[1:], dtype='float32')
    input2 = Input(shape=Xirv2_train.shape[1:], dtype='float32')
    attn = BimodalBiGRUHierarchicalAttention(500, rnn_size)(input1, input2)
    output = Dense(1, activation='sigmoid')(attn)

    model = Model(inputs=[input1, input2], outputs=output)
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])



    early_stop = EarlyStopping(monitor='val_loss', min_delta=0, patience=3, verbose=0, mode='auto')
    history = model.fit([Xtrn_train, Xirv2_train], y_train, epochs=50, batch_size=200, verbose=1
                        , callbacks=[TensorBoard(log_dir='mytensorboard', write_graph=True, write_images=True)]
                        , validation_data=([Xtrn_test, Xirv2_test], y_test))

    model.evaluate([Xtrn_test, Xirv2_test], y_test)

