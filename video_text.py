import os
from pytubefix import YouTube
from groq import Groq

def transcribe_youtube_with_groq(url):
    """
    Download audio from YouTube and transcribe it using Groq's distil-whisper-large-v3-en.
    """
    # 1. Download audio
    yt = YouTube(url, use_po_token=True)
    audio_stream = yt.streams.filter(only_audio=True).first()
    output_file = audio_stream.download(filename="audio.m4a")

    # 2. Transcribe with Groq
    client = Groq(api_key='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')

    with open(output_file, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=("audio.m4a", file.read()),
            model="distil-whisper-large-v3-en",
            response_format="verbose_json",
        )

    return transcription.text




