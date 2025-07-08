import matplotlib.pyplot as plt
import soundfile as sf


# https://gist.github.com/Mlawrence95/fd20ac0a73c9643321c88704a9d8c9fa
from pydub import AudioSegment

# we want to convert source, mp3, into dest, a .wav file
source = "./recordings/test.mp3"
dest = "./recordings/test.wav"

src = r"C:\Users\rcxsm\Music\MET PYTHON GEDOWNLOAD\al overgezet\Deborah De Luca @ Vele Di Scampia Italy.mp3"
dest = r"C:\Users\rcxsm\Music\MET PYTHON GEDOWNLOAD\al overgezet\Deborah De Luca @ Vele Di Scampia Italy.wav"
# conversion - check!
sound = AudioSegment.from_mp3(src)
sound.export(dest, format="wav")

# we can now load in the .wav file as a numpy-style array like so
data, samplerate = sf.read(dest)

# make a plot of the sound data. Super rewarding - tada!
plt.plot(data)
