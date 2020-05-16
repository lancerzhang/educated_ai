import librosa
import librosa.display as dsp
import matplotlib.pyplot as plt
import pyaudio
import time
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 3
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

y, sr = librosa.load(WAVE_OUTPUT_FILENAME, sr=None)
start = time.time()
mfccs = librosa.feature.mfcc(y, sr=44100, n_mfcc=40)
print('mfcc used(ms):', (time.time() - start) * 1000)
# mfccs = librosa.feature.mfcc(y, sr=44100)
print(mfccs)
plt.figure(figsize=(10, 4))
dsp.specshow(mfccs, x_axis='time')
plt.colorbar()
plt.title('MFCC')
plt.tight_layout()
plt.show()
