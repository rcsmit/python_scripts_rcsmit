import numpy as np
from pydub import AudioSegment
from pydub.generators import Sine
from scipy.signal import sawtooth
import io

# Settings
bpm = 120
beat_duration = 60 / bpm  # one beat in seconds
counts_per_tone = 8
tone_duration = beat_duration * counts_per_tone  # duration of each tone in seconds
sample_rate = 44100

# Frequencies for notes (C4=261.63 Hz)
notes1 = [261.63, 293.66, 329.63, 349.23]  # C, D, E, F
notes2 = [392.00, 440.00, 493.88, 523.25]  # G, A, B, C

def generate_saw(frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = sawtooth(2 * np.pi * frequency * t)
    # normalize to 16-bit PCM
    audio = np.int16(wave * 32767)
    return audio

def create_track(notes, filename):
    track = np.array([], dtype=np.int16)
    silence = np.zeros(int(sample_rate * 0.05), dtype=np.int16)  # 50 ms silence
    for f in notes:
        tone = generate_saw(f, tone_duration, sample_rate)
        
        track = np.concatenate((track, tone, silence))
    # Convert to AudioSegment
    audio_segment = AudioSegment(
        track.tobytes(),
        frame_rate=sample_rate,
        sample_width=2,  # 16-bit
        channels=1
    )
    buffer = io.BytesIO()
    audio_segment.export(buffer, format="mp3", bitrate="192k")
    return buffer.getvalue()

# Generate both MP3s
mp3_1 = create_track(notes1, "track1.mp3")
mp3_2 = create_track(notes2, "track2.mp3")

# Save files
with open("CDEF.mp3", "wb") as f:
    f.write(mp3_1)

with open("GABC.mp3", "wb") as f:
    f.write(mp3_2)

"/mnt/data/track1.mp3", "/mnt/data/track2.mp3"
