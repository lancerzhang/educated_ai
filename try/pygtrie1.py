import os
import stat
import sys

import pygtrie

print('Storing file information in the trie')
print('====================================\n')

ROOT_DIR = '/usr/local'
SUB_DIR = os.path.join(ROOT_DIR, 'lib')
SUB_DIRS = tuple(os.path.join(ROOT_DIR, d)
                 for d in ('lib', 'lib32', 'lib64', 'share'))

trie1 = pygtrie.StringTrie(separator=os.path.sep)

# Read sizes regular files into a Trie
for dirpath, unused_dirnames, filenames in os.walk(ROOT_DIR):
    for filename in filenames:
        filename = os.path.join(dirpath, filename)
        try:
            filestat = os.stat(filename)
        except OSError:
            continue
        if stat.S_IFMT(filestat.st_mode) == stat.S_IFREG:
            trie1[filename] = filestat.st_size

# Size of all files we've scanned
print('Size of %s: %d' % (ROOT_DIR, sum(trie1.itervalues())))

# Size of all files of a sub-directory
print('Size of %s: %d' % (SUB_DIR, sum(trie1.itervalues(prefix=SUB_DIR))))

# Check existence of some directories
for directory in SUB_DIRS:
    print(directory, 'exists' if trie1.has_subtrie(directory) else 'does not exist')

# Drop a subtrie
print('Dropping', SUB_DIR)
del trie1[SUB_DIR:]
print('Size of %s: %d' % (ROOT_DIR, sum(trie1.itervalues())))
for directory in SUB_DIRS:
    print(directory, 'exists' if trie1.has_subtrie(directory) else 'does not exist')

print('\nStoring URL handlers map')
print('========================\n')

trie1 = pygtrie.CharTrie()
trie1['/'] = lambda url: sys.stdout.write('Root handler: %s\n' % url)
trie1['/foo'] = lambda url: sys.stdout.write('Foo handler: %s\n' % url)
trie1['/foobar'] = lambda url: sys.stdout.write('FooBar handler: %s\n' % url)
trie1['/baz'] = lambda url: sys.stdout.write('Baz handler: %s\n' % url)

for url in ('/', '/foo', '/foot', '/foobar', 'invalid', '/foobarbaz', '/ba'):
    key, handler = trie1.longest_prefix(url)
    if key is not None:
        handler(url)
    else:
        print('Unable to handle', repr(url))

if not os.isatty(0):
    sys.exit(0)

try:
    import termios
    import tty


    def getch():
        """Reads single character from standard input."""
        attr = termios.tcgetattr(0)
        try:
            tty.setraw(0)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(0, termios.TCSADRAIN, attr)

except ImportError:
    try:
        from msvcrt import getch  # pylint: disable=import-error
    except ImportError:
        sys.exit(0)

print('\nPrefix set')
print('==========\n')

ps = pygtrie.PrefixSet(factory=pygtrie.StringTrie)

ps.add('/etc/rc.d')
ps.add('/usr/local/share')
ps.add('/usr/local/lib')
ps.add('/usr')  # Will handle the above two as well
ps.add('/usr/lib')  # Does not change anything

print('Path prefixes:', ', '.join(iter(ps)))
for path in ('/etc', '/etc/rc.d', '/usr', '/usr/local', '/usr/local/lib'):
    print('Is', path, 'in the set:', ('yes' if path in ps else 'no'))

print('\nDictionary test')
print('===============\n')

trie1 = pygtrie.CharTrie()
trie1['cat'] = True
trie1['caterpillar'] = True
trie1['car'] = True
trie1['bar'] = True
trie1['exit'] = False

print('Start typing a word, "exit" to stop')
print('(Other words you might want to try: %s)\n' % ', '.join(sorted(
    k for k in trie1 if k != 'exit')))

text = ''
while True:
    ch = getch()
    if ord(ch) < 32:
        print('Exiting')
        break

    text += ch
    value = trie1.get(text)
    if value is False:
        print('Exiting')
        break
    if value is not None:
        print(repr(text), 'is a word')
    if trie1.has_subtrie(text):
        print(repr(text), 'is a prefix of a word')
    else:
        print(repr(text), 'is not a prefix, going back to empty string')
        text = ''
