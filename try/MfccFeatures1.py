import librosa

from components.recognizers import MfccRecognizer

audio_file = 'speech_dataset/yes/0a2b400e_nohash_0.wav'
y, sr = librosa.load(audio_file)
mf = MfccRecognizer(y, sr)
print(mf.features)
