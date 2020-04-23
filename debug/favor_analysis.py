from components.favor import Favor
from components import favor
from components import util
from matplotlib import pyplot
import numpy as np
import cv2
import skimage.measure
import pickle

with open('../try/vgg16.l1.filters', 'rb') as filters:
    vgg16_filters = pickle.load(filters)

favor1 = Favor()
favor.FAVOR_FILE = '../data/favor.npy'
favor1.load()
for f in favor1.vuk.items:
    print(f)

img = cv2.imread('../try/triangle1.jpg', 0)
# from keras.applications.vgg16 import preprocess_input
# from keras.preprocessing.image import load_img
# from keras.preprocessing.image import img_to_array
# img = load_img('../try/triangle1.jpg', target_size=(224, 224))
# img = img_to_array(img)
# img = preprocess_input(img)
x = 8
y = 8
for i in range(x * y):
    pyplot.subplot(x, y, i + 1)
    # kernel_str = favor1.vuk.items[ix - 1].key
    # kernel = util.string_to_feature_matrix(kernel_str)
    # kernel = kernel.astype(np.float64)
    kernel = vgg16_filters[:, :, 0, i]
    feature = cv2.filter2D(img, -1, kernel)
    # feature = skimage.measure.block_reduce(feature, (2, 2), np.max)
    # feature = skimage.measure.block_reduce(feature, (2, 2), np.max)
    pyplot.imshow(feature, cmap='gray')

pyplot.show()
