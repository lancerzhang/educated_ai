import librosa,scipy,io
import speech_recognition as sr
import matplotlib.pyplot as plt
import librosa.display as dsp
import soundfile as sf

r = sr.Recognizer()
m = sr.Microphone()

try:
    print("A moment of silence, please...")
    with m as source: r.adjust_for_ambient_noise(source)
    print("Set minimum energy threshold to {}".format(r.energy_threshold))
    while True:
        print("Say something!")
        with m as source: audio = r.listen(source)
        print("Got it! Now to recognize it...")
        try:
            # recognize speech using Google Speech Recognition
            # value = r.recognize_google(audio)
            wav_data=audio.get_wav_data()
            tmp = io.BytesIO(wav_data)
            data, samplerate = sf.read(tmp)
            # mfccs = librosa.feature.mfcc(y, sr=44100, n_mfcc=40)
            mfccs = librosa.feature.mfcc(data, sr=44100)
            plt.figure(figsize=(10, 4))
            dsp.specshow(mfccs, x_axis='time')
            plt.colorbar()
            plt.title('MFCC')
            plt.tight_layout()
            plt.show()
        except sr.UnknownValueError:
            print("Oops! Didn't catch that")
        except sr.RequestError as e:
            print("Uh oh! Couldn't request results from Google Speech Recognition service; {0}".format(e))
except KeyboardInterrupt:
    pass
