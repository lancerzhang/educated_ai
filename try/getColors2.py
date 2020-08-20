import components.color_cluster as cc

hist = cc.cluster('square1.jpg')
for h in hist:
    print(h)
