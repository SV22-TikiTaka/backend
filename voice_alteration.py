import numpy as np
from pydub import AudioSegment
import os

ffmpeg_path = "/venv/bin"
os.environ["PATH"] += os.pathsep + ffmpeg_path

filename = 'in.wav'
sound = AudioSegment.from_file(filename, format=filename[-3:])

octaves = 0.5
new_sample_rate = int(sound.frame_rate * (1.5 ** octaves))
hipitch_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
hipitch_sound = hipitch_sound.set_frame_rate(44100)
# export / save pitch changed sound
hipitch_sound.export(f"octave_{octaves}.wav", format="wav")
