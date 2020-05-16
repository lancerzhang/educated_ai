from PIL import Image

im = Image.open("head1.jpg")
im = im.resize((3, 3), Image.ANTIALIAS).convert('L')
im.show()
