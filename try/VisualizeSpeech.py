# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
r"""Runs a trained audio graph against a WAVE file and reports the results.

The model, labels and .wav file specified in the arguments will be loaded, and
then the predictions from running the model against the audio data will be
printed to the console. This is a useful script for sanity checking trained
models, and as an example of how to use an audio model from Python.

Here's an example of running it:

python tensorflow/examples/speech_commands/label_wav.py \
--graph=/tmp/my_frozen_graph.pb \
--labels=/tmp/speech_commands_train/conv_labels.txt \
--wav=/tmp/speech_dataset/left/a5d485dc_nohash_0.wav

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import sys

import numpy as np
import tensorflow as tf
from matplotlib import cm
from matplotlib import pyplot

FLAGS = None
ROWS = 4


def load_graph(filename):
    """Unpersists graph from file as default graph."""
    with tf.io.gfile.GFile(filename, 'rb') as f:
        graph_def = tf.compat.v1.GraphDef()
        graph_def.ParseFromString(f.read())
        tf.import_graph_def(graph_def, name='')


def load_labels(filename):
    """Read in labels, one label per line."""
    return [line.rstrip() for line in tf.io.gfile.GFile(filename)]


def run_graph(wav_data, labels, input_layer_name, output_layer_name,
              num_top_predictions):
    """Runs the audio data through the graph and prints predictions."""
    with tf.compat.v1.Session() as sess:
        # Feed the audio data as input to the graph.
        #   predictions  will contain a two-dimensional array, where one
        #   dimension represents the input image count, and the other has
        #   predictions per class
        softmax_tensor = sess.graph.get_tensor_by_name(output_layer_name)
        predictions, = sess.run(softmax_tensor, {input_layer_name: wav_data})

        if 'Conv' in output_layer_name:
            show_conv(predictions)
        else:
            show_img(predictions)


def show_img(img):
    ax = pyplot.subplot(1, 1, 1)
    img = np.swapaxes(img, 0, 1)
    ax.imshow(img, interpolation='nearest', cmap=cm.coolwarm, origin='lower')
    pyplot.show()


def show_conv(predictions):
    # plot all 64 maps in an 8x8 squares
    square = ROWS
    ix = 1
    for _ in range(square):
        for _ in range(square):
            # specify subplot and turn of axis
            ax = pyplot.subplot(square, square, ix)
            # plot filter channel in grayscale
            img = predictions[:, :, ix - 1]
            img = np.swapaxes(img, 0, 1)
            ax.imshow(img, interpolation='nearest', cmap=cm.coolwarm, origin='lower')
            ix += 1
    # show the figure
    pyplot.show()


def label_wav(wav, labels, graph, input_name, output_name, how_many_labels):
    """Loads the model and labels, and runs the inference to print predictions."""
    if not wav or not tf.io.gfile.exists(wav):
        raise ValueError('Audio file does not exist at {0}'.format(wav))
    if not labels or not tf.io.gfile.exists(labels):
        raise ValueError('Labels file does not exist at {0}'.format(labels))

    if not graph or not tf.io.gfile.exists(graph):
        raise ValueError('Graph file does not exist at {0}'.format(graph))

    labels_list = load_labels(labels)

    # load graph, which is stored in the default session
    load_graph(graph)

    with open(wav, 'rb') as wav_file:
        wav_data = wav_file.read()

    run_graph(wav_data, labels_list, input_name, output_name, how_many_labels)


def main(_):
    """Entry point for script, converts flags to arguments."""
    label_wav(FLAGS.wav, FLAGS.labels, FLAGS.graph, FLAGS.input_name,
              FLAGS.output_name, FLAGS.how_many_labels)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--wav', type=str, default='speech_dataset/follow/0a2b400e_nohash_1.wav', help='Audio file to be identified.')
    parser.add_argument(
        '--graph', type=str, default='conv_actions_frozen.pb', help='Model to use for identification.')
    parser.add_argument(
        '--labels', type=str, default='conv_actions_labels.txt', help='Path to file containing labels.')
    parser.add_argument(
        '--input_name',
        type=str,
        default='wav_data:0',
        help='Name of WAVE data input node in model.')
    parser.add_argument(
        '--output_name',
        type=str,
        # default='Mfcc:0',
        # default='AudioSpectrogram:0',
        default='Conv2D:0',
        # default='Conv2D_1:0',
        help='Name of node outputting a prediction in the model.')
    parser.add_argument(
        '--how_many_labels',
        type=int,
        default=3,
        help='Number of results to show.')

    FLAGS, unparsed = parser.parse_known_args()
    tf.compat.v1.app.run(main=main, argv=[sys.argv[0]] + unparsed)
