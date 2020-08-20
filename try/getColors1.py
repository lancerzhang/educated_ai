# importing Image module from PIL package
from PIL import Image

# opening a  image
im = Image.open("rgb1.jpg").convert("RGB")

# getting colors
# multiband images (RBG)
im1 = Image.Image.getcolors(im)
im1 = sorted(im1, key=lambda x: x[0], reverse=True)
print(im1)
