import pygtrie

trie1 = pygtrie.CharTrie()
trie1.enable_sorting(enable=True)
trie1['cat'] = 6
trie1['caterpillar'] = 5
trie1['caa'] = 4
trie1['car'] = 3
trie1['bar'] = 2
trie1['exit'] = 1

print(trie1.has_key('car'))
print(trie1.has_node('car'))
print(trie1.has_subtrie('car'))
print(trie1.items(prefix='ca'))
for i in trie1:
    print(i)
