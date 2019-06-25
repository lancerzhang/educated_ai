import cv2

from PIL import Image
from functools import reduce


def avhash(im):
    if not isinstance(im, Image.Image):
        im = Image.open(im)
    im = im.resize((3, 3), Image.ANTIALIAS).convert('L')
    avg = reduce(lambda x, y: x + y, im.getdata()) / 9.
    return reduce(lambda x, (y, z): x | (z << y),
                  enumerate([0 if i < avg else 1 for i in im.getdata()]),
                  0)


def hamming(h1, h2):
    h, d = 0, h1 ^ h2
    while d:
        h += 1
        d &= d - 1
    return h

hash1=avhash("head1.jpg")
hash2=avhash("head2.jpg")
print(hash1)
print(hash2)
print(hamming(hash1,hash2 ))
