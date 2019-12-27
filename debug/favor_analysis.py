from components.favor import Favor

favor = Favor()
favor.FAVOR_FILE = '../data/favor.npy'
favor.load()
for f in favor.suk.items:
    print(f)
