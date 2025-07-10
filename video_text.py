from groq import Groq
from pytubefix import YouTube
import yt_dlp

client = Groq(api_key='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')


def download_audio(url: str, dst: str = "/tmp/audio.mp3") -> str:
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "/tmp/%(id)s.%(ext)s",
        # turn the downloaded .webm/.m4a into MP3 so Whisper likes it
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp3"

    
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
