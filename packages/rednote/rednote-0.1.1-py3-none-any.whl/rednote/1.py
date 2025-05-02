# record_wsl.py
import sounddevice as sd
import soundfile as sf

def record(seconds=5, rate=48000, fname="demo.wav"):
    print("Recording …")
    audio = sd.rec(int(seconds * rate),
                   samplerate=rate,
                   channels=1,
                   dtype="int16")
    sd.wait()
    sf.write(fname, audio, rate)
    print("Saved:", fname)

if __name__ == "__main__":
    record()
