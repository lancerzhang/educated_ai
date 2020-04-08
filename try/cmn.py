import csv
import pygtrie
import time

lol = list(csv.reader(open('cmn.txt', 'r', encoding='utf8'), delimiter='\t'))
print(f'len of sentences {len(lol)}')
en_words = set()
cn_words = set()
for l in lol:
    for w in l[0].split():
        en_words.add(w)
    for c in l[1]:
        cn_words.add(c)
print(f'len of en words {len(en_words)}')
print(f'len of en words {len(cn_words)}')

trie1 = pygtrie.CharTrie()
time1=time.time()
for w in en_words:
    trie1[w] = len(w)
time2=time.time()
print(trie1.items(prefix='ca'))
time3=time.time()
print(f'1 used {time2-time1}')
print(f'1 used {time3-time2}')

