import torchaudio


def load_audio(audio_path: str):
    waveform, sample_rate = torchaudio.load(audio_path)

    # Преобразуем стерео в моно (если нужно)
    if waveform.size(0) > 1:  # Если больше одного канала
        waveform = waveform.mean(dim=0)  # Усредняем каналы

    # Ресэмплируем до 16 кГц (если нужно)
    if sample_rate != 16000:
        transform = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
        waveform = transform(waveform)

    return waveform, 16000