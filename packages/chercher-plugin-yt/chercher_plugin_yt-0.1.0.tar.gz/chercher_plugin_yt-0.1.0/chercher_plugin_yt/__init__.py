from typing import Generator
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from chercher import Document, hookimpl

ytt_api = YouTubeTranscriptApi()
formatter = TextFormatter()


@hookimpl
def ingest(uri: str, settings: dict) -> Generator[Document, None, None]:
    try:
        parsed_uri = urlparse(uri)
    except Exception:
        return

    if parsed_uri.scheme not in ("http", "https"):
        return

    if parsed_uri.netloc not in ("www.youtube.com", "youtube.com"):
        return

    video_id = parse_qs(parsed_uri.query).get("v", [None])[0]
    if not video_id:
        return

    settings = settings.get("yt", {})
    languages = settings.get("languages", ["en"])

    try:
        transcript = ytt_api.fetch(video_id, languages=languages)
        text_formmated = formatter.format_transcript(transcript)
        yield Document(
            uri=uri,
            title="",
            body=text_formmated,
            metadata={},
        )
    except Exception:
        return


if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=wo_e0EvEZn8"
    for document in ingest(url, {}):
        print(document)
