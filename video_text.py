from groq import Groq
from pytubefix import YouTube

client = Groq(api_key='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')

def transcribe_youtube_with_groq(url):
    """
    Download audio from YouTube as MP3 and transcribe it using Groq's distil-whisper-large-v3-en.
    """


    yt = YouTube(url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    output_file = audio_stream.download(filename="audio.m4a")
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
