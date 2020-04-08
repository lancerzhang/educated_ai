
import os
import stat
import sys

import pygtrie


ps = pygtrie.PrefixSet(factory=pygtrie.StringTrie)

ps.add('/etc/rc.d')
ps.add('/usr/local/share')
ps.add('/usr/local/lib')
ps.add('/usr')  # Will handle the above two as well
ps.add('/usr/lib')  # Does not change anything

print('/usr/lib' in ps)
for p in ps:
    print(p)
