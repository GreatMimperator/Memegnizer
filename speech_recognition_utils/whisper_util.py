import numpy as np
import torch
from pydub import AudioSegment
from transformers import WhisperProcessor
from whisper import Whisper


def transcribe_audio_with_whisper(audio_path: str, model: Whisper):
    result = model.transcribe(audio_path)
    return result['text']

def prepare_whisper_processor_audio(audio_path: str):
    audio = AudioSegment.from_file(audio_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    return np.array(audio.get_array_of_samples())

def transcribe_audio_with_whisper_transformer(audio_path: str, processor: WhisperProcessor, model):
    audio = AudioSegment.from_file(audio_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio_array = np.array(audio.get_array_of_samples())

    inputs = processor(audio_array, sampling_rate=16000, return_tensors="pt")

    with torch.no_grad():
        print(inputs)
        predicted_ids = model.generate(inputs["input_features"])

    return processor.decode(predicted_ids[0], skip_special_tokens=True)