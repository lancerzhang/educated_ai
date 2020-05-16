import io
import librosa
import librosa.display as dsp
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
import speech_recognition as sr

r = sr.Recognizer()
m = sr.Microphone()

try:
    print("A moment of silence, please...")
    with m as source:
        r.adjust_for_ambient_noise(source)
    print(("Set minimum energy threshold to {}".format(r.energy_threshold)))
    while True:
        print("Say something!")
        with m as source:
            audio = r.listen(source)
        print("Got it! Now to recognize it...")
        try:
            # recognize speech using Google Speech Recognition
            # value = r.recognize_google(audio)
            wav_data = audio.get_wav_data()
            tmp = io.BytesIO(wav_data)
            y, sr = sf.read(tmp)
            mel_data = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
            plt.figure(figsize=(10, 4))
            librosa.display.specshow(librosa.power_to_db(mel_data, ref=np.max), y_axis='mel', fmax=8000, x_axis='time')
            plt.colorbar(format='%+2.0f dB')
            plt.title('Mel spectrogram')
            plt.tight_layout()
            plt.show()
            np.save('npa.npy', y)
        except sr.UnknownValueError:
            print("Oops! Didn't catch that")
        except sr.RequestError as e:
            print(("Uh oh! Couldn't request results from Google Speech Recognition service; {0}".format(e)))
except KeyboardInterrupt:
    pass
