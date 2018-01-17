import librosa

wav = librosa.load(librosa.util.example_audio_file())
melM = librosa.feature.mfcc(wav, sr=44100, n_mfcc=20)
print melM