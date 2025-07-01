from typing import List
from datetime import datetime
from pytubefix import YouTube
from dataclasses import dataclass
import subprocess
import streamlit as st


@dataclass
class VideoInfo:
    video_id: str
    title: str
    keywords: List[str]
    publish_date: datetime
    length_seconds: int


class YouTubeVideo:
    def __init__(self, url: str):
        self.url = url
        self.video = YouTube(url)

    def __str__(self):
        return f"{self.video.title} ({self.video.video_id})"

    def get_metadata(self) -> VideoInfo:
        return VideoInfo(
            video_id=self.video.video_id,
            title=self.video.title,
            keywords=self.video.keywords,
            publish_date=self.video.publish_date,
            length_seconds=self.video.length
        )

    def get_caption_text(self, lang_prefix='en') -> str:
        for key, caption in self.video.captions.lang_code_index.items():
            if key.startswith(lang_prefix):
                return caption.generate_srt_captions()
        return f"No captions found starting with: {lang_prefix}"

    def get_caption_text_plain(self, lang_prefix='en') -> str:
        for key, caption in self.video.captions.lang_code_index.items():
            if key.startswith(lang_prefix):
                srt = caption.generate_srt_captions()
                lines = srt.split('\n')
                text_lines = [
                    line for line in lines
                    if not line.strip().isdigit() and '-->' not in line and line.strip()
                ]
                return '\n'.join(text_lines)
        return f"No captions found starting with: {lang_prefix}"

    def get_stream_url(self) -> str:
        """
        Uses streamlink to get the direct stream URL.
        """
        try:
            cmd = ["streamlink", "--stream-url", self.url, "best"]
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"❌ Error running Streamlink:\n{e.stderr.strip()}"
        except FileNotFoundError:
            return "❌ Streamlink is not installed or not found in PATH."


def main():
    st.title("🎬 YouTube Video Info + Streamlink")

    youtube_url = st.text_input(
        "Enter YouTube URL:",
        value="https://www.youtube.com/watch?v=BW9Fzwuf43c"
    )

    if st.button("Fetch Video Info"):
        try:
            yt_video = YouTubeVideo(youtube_url)

            info = yt_video.get_metadata()
            st.subheader("📄 Video Metadata")
            st.json(info.__dict__)

            st.subheader("📝 Captions (SRT)")
            srt_captions = yt_video.get_caption_text("en")
            st.code(srt_captions, language='srt')

            st.subheader("📝 Captions (Plain Text)")
            plain_captions = yt_video.get_caption_text_plain("en")
            st.code(plain_captions, language='text')

            st.subheader("🔗 Direct Stream URL (Streamlink)")
            stream_url = yt_video.get_stream_url()
            st.code(stream_url, language='text')

        except Exception as e:
            st.error(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
