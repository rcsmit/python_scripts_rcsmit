import numpy as np
import scipy.signal
import soundfile as sf
from scipy.signal import butter, lfilter
import sounddevice as sd

# Shared defaults
DEFAULTS = {
    "sample_rate": 44100,
    "bpm": 140,
    "beats": 4,
    "base_freq": 499,
    "attack_time": 0.3,
    "release_time": 0.3,
    "cutoff": 3000,
    "delay_time": 1.0,
    "delay_amount": 0.15,
    "noise_level": 0.05,
}

def time_array(cfg):
    beat_sec = 60.0 / cfg["bpm"]
    dur = cfg["beats"] * beat_sec
    return np.linspace(0, dur, int(cfg["sample_rate"] * dur), False)

def detuned_saw(cfg, t):
    f = cfg["base_freq"]
    return 0.5 * sum(
        scipy.signal.sawtooth(2*np.pi*(f + d)*t)
        for d in (0, 6)
    )

def envelope(cfg, t, start_beat=0):
    sr = cfg["sample_rate"]
    atk = int(cfg["attack_time"] * sr)
    rel = int(cfg["release_time"] * sr)
    start = int(start_beat * len(t) / cfg["beats"])
    env = np.zeros_like(t)
    env[start:start+atk] = np.linspace(0, 1, atk)
    env[start+atk:-rel] = 1
    env[-rel:] = np.linspace(1, 0, rel)
    return env

def lowpass(x, cfg):
    b,a = butter(4, cfg["cutoff"]/(0.5*cfg["sample_rate"]), "low")
    return lfilter(b,a,x)

def add_delay(x, cfg):
    ds = int(cfg["delay_time"]*cfg["sample_rate"])
    d = np.zeros_like(x)
    if ds < len(x):
        d[ds:] = cfg["delay_amount"] * x[:-ds]
    return x + d

def normalize(x):
    return x / np.max(np.abs(x))

def play_save(x, cfg, name):
    sf.write(name, normalize(x), cfg["sample_rate"])
    print(f"Saved {name}")
    sd.play(x, cfg["sample_rate"])
    sd.wait()
    print("Done")

def make_pad(cfg, synth_start=0):
    t = time_array(cfg)
    noise = cfg["noise_level"] * np.random.randn(len(t))
    saw = detuned_saw(cfg, t) if synth_start < cfg["beats"] else np.zeros_like(t)
    env = envelope(cfg, t, start_beat=synth_start)
    sig = noise + saw*env
    sig = lowpass(sig, cfg)
    sig = add_delay(sig, cfg)
    return sig

def four_beats():
    cfg = DEFAULTS.copy()
    sig = make_pad(cfg, synth_start=0)
    play_save(sig, cfg, "4beats_pad.wav")

def two_and_two():
    cfg = DEFAULTS.copy()
    # start synth on beat 2 of 4
    sig = make_pad(cfg, synth_start=1)
    play_save(sig, cfg, "2n2_pad.wav")

# run your choice
two_and_two()
