import librosa

from src.recognizers import VoiceRecognizer

audio_file = 'speech_dataset/yes/0a2b400e_nohash_0.wav'
y, sr = librosa.load(audio_file)
mf = VoiceRecognizer(y, sr)
print(mf.features)
