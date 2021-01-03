import librosa

from src.recognizers import SpeechRecognizer

audio_file = 'speech_dataset/yes/0a2b400e_nohash_0.wav'
y, sr = librosa.load(audio_file)
mf = SpeechRecognizer(y, sr)
print(mf.features)
