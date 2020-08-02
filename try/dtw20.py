# TensorFlow and tf.keras
# Helper libraries
import cv2
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras

print(tf.__version__)

fashion_mnist = keras.datasets.fashion_mnist

(train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()

class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

SMALL = 4
MEDIUM = 3
LARGE = 2
SIZE_UNIT = 7

image_group = {}
for i in range(len(train_labels)):
    image_group.setdefault(train_labels[i], []).append(i)

selected_group = 9
selected_index = 6
selected_image = train_images[image_group[selected_group][selected_index]]
ret, selected_image = cv2.threshold(selected_image, 127, 255, 0)


# selected_image = cv2.Canny(selected_image, 30, 200)


# print(train_images.shape)


def get_blocks(img, size):
    blocks = []
    x = size
    y = size
    step = SIZE_UNIT
    width = SIZE_UNIT + (4 - size) * SIZE_UNIT
    for i in range(x):
        for j in range(y):
            p_x = i * step
            p_y = j * step
            blocks.append(img[p_x:p_x + width, p_y:p_y + width])
    return blocks


def show_block(size):
    blocks = get_blocks(selected_image, size)
    for i in range(len(blocks)):
        plt.subplot(size, size, i + 1)
        plt.imshow(blocks[i], cmap='gray')
    plt.show()


def show_images(size):
    for i in range(size):
        for j in range(size):
            idx = i * size + j
            plt.subplot(size, size, idx + 1)
            plt.imshow(train_images[image_group[selected_group][idx]], cmap='gray')
    plt.show()


# show_block(LARGE)
show_images(4)
