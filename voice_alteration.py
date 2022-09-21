from pydub import AudioSegment
import os

# ffmpeg_path = "/venv/bin"
# os.environ["PATH"] += os.pathsep + ffmpeg_path


def voice_alteration(filepath: str, comment_id: int):
    sound = AudioSegment.from_file(filepath, format=filepath[-3:])

    octaves = 0.7
    new_sample_rate = int(sound.frame_rate * (1.8 ** octaves))
    hipitch_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
    hipitch_sound = hipitch_sound.set_frame_rate(44100)
    # export / save pitch changed sound
    hipitch_sound.export(f"temp/{comment_id}.mp4", format="mp4")
