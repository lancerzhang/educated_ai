# plot feature map of first conv layer for given image
from keras import Input, layers
from keras.applications.vgg16 import VGG16
from keras.applications.vgg16 import preprocess_input
from keras.models import Model
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import load_img
from matplotlib import pyplot
from numpy import expand_dims

# load the model
model = VGG16()
filters, biases = model.layers[1].get_weights()


def my_kernel(shape, dtype=None):
    return filters


input_tensor = Input(shape=(224, 224, 3))
x = layers.Conv2D(filters=64,
                  kernel_size=3,
                  kernel_initializer=my_kernel,
                  strides=1,
                  activation='relu',
                  padding='same')(input_tensor)
model = Model(inputs=input_tensor, outputs=x)
model.summary()

# load the image with the required shape
img = load_img('triangle1.jpg', target_size=(224, 224))
# convert the image to an array
img = img_to_array(img)
# expand dimensions so that it represents a single 'sample'
img = expand_dims(img, axis=0)
# prepare the image (e.g. scale pixel values for the vgg)
img = preprocess_input(img)
# get feature map for first hidden layer
feature_maps = model.predict(img)
# plot all 64 maps in an 8x8 squares
square = 8
ix = 1
for _ in range(square):
    for _ in range(square):
        # specify subplot and turn of axis
        ax = pyplot.subplot(square, square, ix)
        # plot filter channel in grayscale
        pyplot.imshow(feature_maps[0, :, :, ix - 1], cmap='gray')
        ix += 1
# show the figure
pyplot.show()
