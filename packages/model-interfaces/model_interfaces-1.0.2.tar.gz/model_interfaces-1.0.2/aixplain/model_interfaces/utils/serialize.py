import base64
import io
import tempfile

from pydub import AudioSegment

ENCODING = 'ascii'
FFMPEG_FORMAT = 'wav'

def audio_file_handle(file_path, source_format, out_format=FFMPEG_FORMAT, frame_rate=16000):
    sound_file = AudioSegment.from_file(file_path, source_format)
    sound_file = sound_file.set_frame_rate(frame_rate)
    file_handle = sound_file.export(format=out_format)
    return file_handle

def encode(to_be_encoded):
    return base64.b64encode(to_be_encoded).decode(ENCODING)

def decode(encoded):
    b64_decoded = base64.b64decode(encoded.encode(ENCODING))
    return b64_decoded
