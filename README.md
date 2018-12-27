# educated_ai

Don't download, it's not finish, just for keeping my code.

- Python 2.7
- cv2
https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_setup/py_table_of_contents_setup/py_table_of_contents_setup.html
- PIL
http://pythonware.com/products/pil/

``` bash
    pip install -r requirements.txt
```
For Mac
- install brew
- install portaudio
- install pyautoguid https://pyautogui.readthedocs.io/en/latest/install.html
``` bash
brew install portaudio
```
- use separate PyCharm <br>
PyCharm - Settings - Project Interpreter "Add" - Virtualenv Environment
- install opencv (in PyCharm Terminal)
``` bash
pip install opencv-python
```
 - install requirement
 ``` bash
 pip install -r requirements.txt
 ```

if you see many CodernityDB debug log, remove 'print' in below line
/python27/lib/python2.7/site-packages/CodernityDB/storage.py
print locals()