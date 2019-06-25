# educated_ai

Don't download, it's not finish, just for keeping my code.

## Installation
### Windows
- Python 3.x
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
- Other required modules (in PyCharm Terminal)
 ``` bash
 pip install -r requirements.txt
 ```
- Configure matplotlib
 ``` bash
$ cat ~/.matplotlib/matplotlibrc
backend: TkAgg
 ```
## Train
- To remember something, the best timing is to repeat it in below interval.
5 minutes, 20 minutes, 1 hour, 2 hours, 4 hours, 12 hours, 3 days, 3 months
- If you want to train using video file, audioread is used for reading audio, it depends on some backend library 
(e.g. ffmpeg), make sure you install the library.

#### License: MIT or Apache, whichever you prefer