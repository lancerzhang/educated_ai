import cv2

from components.recognizers import ImgShapeRecognizer

files = ['head1.jpg', 'head2.jpg', 'head3.jpg', 'head4.jpg', 'head5.jpg', 'head10.jpg', 'head11.jpg', 'gb1.jpg',
         'image1.jpg', 'image2.jpg', 'l1-1.jpg', 'l1-2.jpg', 'manu.jpg', 'rgb1.jpg', 'rgb2.jpg', 's1.jpg', 's2.jpg',
         'square1.jpg', 'square2.jpg', 'square3.jpg', 'triangle1.jpg']
# files = ['image2.jpg']

for file1 in ['square1.jpg']:
    im1 = cv2.imread(file1)
    ics = ImgShapeRecognizer(im1, mode='ssim')
    # ics.similar_threshold = 0.6
    for file2 in files:
        im2 = cv2.imread(file2)
        if file1 == file2:
            continue
        if ics.is_similar(im2):
            print(f'{file1} is similar to {file2}')

# size = 3
# idx = 1
# for im in ics.matched:
#     plt.subplot(size, size, idx)
#     plt.imshow(im, cmap='gray')
#     idx += 1
# plt.show()
