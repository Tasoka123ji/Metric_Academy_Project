from typing import List
from datetime import datetime
from pytubefix import YouTube
from dataclasses import dataclass


sample_video = "https://www.youtube.com/watch?v=BW9Fzwuf43c"



@dataclass
class VideoInfo:
    video_id: str
    title: str
    keywords: List[str]
    publish_date: datetime
    length_seconds: int


class YouTubeVideo:
    def __init__(self, url: str):
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
                text_lines = [line for line in lines if not line.strip().isdigit() and '-->' not in line and line.strip()]
                return '\n'.join(text_lines)
        return f"No captions found starting with: {lang_prefix}"


yt_video = YouTubeVideo(sample_video)

info = yt_video.get_metadata()
print("Video Metadata:" ,info)


print("\n📝 English Captions:")
print(yt_video.get_caption_text("en"))


print("\n📝 English Captions (Plain Text):")
print(yt_video.get_caption_text_plain("en"))


