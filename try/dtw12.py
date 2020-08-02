from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import glob
import os
import time
import sys
import numpy as np
import tensorflow as tf
from matplotlib import cm
from matplotlib import pyplot
np.set_printoptions(threshold=sys.maxsize)
ROWS = 8
input_name = 'wav_data:0'
output_name = 'Conv2D:0'
DATABASE_PATH = 'speech_dataset'
SEARCH_FOLDER = 'stop'
SEARCH_FILE_NUM = 20


def load_graph():
    with tf.io.gfile.GFile('conv_actions_frozen.pb', 'rb') as f:
        graph_def = tf.compat.v1.GraphDef()
        graph_def.ParseFromString(f.read())
        tf.import_graph_def(graph_def, name='')


def show_conv(predictions):
    square = ROWS
    ix = 1
    for _ in range(square):
        for _ in range(square):
            ax = pyplot.subplot(square, square, ix)
            img = predictions[:, :, ix - 1]
            img = np.swapaxes(img, 0, 1)
            ax.imshow(img, interpolation='nearest', cmap=cm.coolwarm, origin='lower')
            ix += 1
    pyplot.show()


def gen_graph(file_name):
    # file_name = params[0]
    with open(file_name, 'rb') as wav_file:
        wav_data = wav_file.read()
    with tf.compat.v1.Session() as sess:
        softmax_tensor = sess.graph.get_tensor_by_name(output_name)
        predictions, = sess.run(softmax_tensor, {input_name: wav_data})
        np.save(f'{file_name}_conv', predictions)


# def run_one(filename):
#     tf.compat.v1.app.run(main=gen_graph, argv=[filename])


if __name__ == '__main__':
    time1 = time.time()
    load_graph()
    wav_file = 'speech_dataset/yes/0a2b400e_nohash_0.wav'
    # run_one(wav_file)
    files = glob.glob(os.path.join(DATABASE_PATH, SEARCH_FOLDER, '*.wav'))
    # files = files[:SEARCH_FILE_NUM]
    # for f in files:
    #     gen_graph(f)
    predictions = np.load(f'{wav_file}_conv.npy')
    print(predictions.astype(int))
    show_conv(predictions)
    time2 = time.time()
    print(f'used time {time2 - time1}')
