import os
from pytubefix import YouTube
from groq import Groq
import yt_dlp

client = Groq(api_key='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')

def transcribe_youtube_with_groq(url):
    """
    Download audio from YouTube as MP3 and transcribe it using Groq's distil-whisper-large-v3-en.
    """

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',   # ✅ Force MP3
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        output_file = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'  # ✅ match extension

    print(f"Downloaded: {output_file} ({os.path.getsize(output_file)} bytes)")

    with open(output_file, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=("audio.mp3", file.read()),
            model="distil-whisper-large-v3-en",
            response_format="verbose_json",
        )

    return transcription.text



def get_answer(question):
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": question}],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    response = ""
    for chunk in completion:
        if isinstance(chunk.choices[0].delta.content, str):
            response += chunk.choices[0].delta.content

    return response
