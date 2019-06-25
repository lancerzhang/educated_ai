import cv2
from components import util


def avhash(im):
    im = cv2.imread(im,1)
    return util.image_hash(im, 3)


hash1=avhash("head1.jpg")
hash2=avhash("head4.jpg")
print(hash1)
print(hash2)
print(util.hamming(hash1, hash2))
