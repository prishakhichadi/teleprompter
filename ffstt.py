import sounddevice as sd
import numpy as np
import torch
import torchaudio
import whisper
import threading

RATE_IN = 48000
RATE_OUT = 16000
CHANNELS = 1
CHUNK_SEC = 3

# Load whisper once
print("Loading Whisper model locally...")
_model = whisper.load_model("base")
print("Whisper loaded.")

_resampler = torchaudio.transforms.Resample(
    orig_freq=RATE_IN,
    new_freq=RATE_OUT,
)

def _record_chunk():
    # Record int16 at RATE_IN
    audio = sd.rec(int(CHUNK_SEC * RATE_IN), samplerate=RATE_IN, channels=CHANNELS, dtype="int16")
    sd.wait()
    audio_np = audio.flatten()  # int16 numpy
    # Convert to float32 in [-1,1]
    audio_tensor = torch.from_numpy(audio_np.astype(np.float32)) / 32768.0
    # Resample to 16k (returns torch.tensor)
    audio_16k = _resampler(audio_tensor)
    # Convert to numpy float32 (shape: N,)
    return audio_16k.numpy()


def _transcribe_audio_np(audio_16k_np):
    try:
        result = _model.transcribe(audio_16k_np, fp16=False)
        return result.get("text", "").strip()
    except Exception as e:
        print("Whisper transcription error:", e)
        return ""
    


def _transcribe_audio_np(audio_16k_np):
    try:
        result = _model.transcribe(audio_16k_np, fp16=False)

        if result.get("language") != "en":
            print("[STT] Ignored non-English speech:", result.get("language"))
        
        return result.get("text", "").strip()
    except Exception as e:
        print("Whisper transcription error:", e)
        return ""



def stt_loop(callback, stop_event=None):
    """
    Run an infinite loop recording audio chunks and calling callback when text found.
    callback: function that receives a single argument (transcribed_text)
    """
    print("STT loop started")
    while True:
        if stop_event is not None and stop_event.is_set():
            print("STT loop stopping due to stop_event.")
            break
        try:
            audio_16k = _record_chunk()
            text = _transcribe_audio_np(audio_16k)
            if text:
                callback(text)
        except Exception as e:
            print("Error in stt_loop:", e)
