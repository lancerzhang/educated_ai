# educated_ai

Don't download, it's not finish, just for keeping my code.

## Installation
### Windows
- Python 2.7
- cv2
https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_setup/py_table_of_contents_setup/py_table_of_contents_setup.html
- Other required modules
``` bash
    pip install -r requirements.txt
```
### Mac
- install brew
- Use separate python runtime in PyCharm. PyCharm - Settings - Project Interpreter "Add" - Virtualenv Environment
- install portaudio (in PyCharm Terminal)
``` bash
brew install portaudio
```
- Opencv (in PyCharm Terminal)
``` bash
pip install opencv-python
```
- Other required modules (in PyCharm Terminal)
 ``` bash
 pip install -r requirements.txt
 ```
## Other
if you see many CodernityDB debug log, remove 'print' in below line
/python27/lib/python2.7/site-packages/CodernityDB/storage.py
print locals()

#### License: MIT or Apache, whichever you prefer