# the file logic: 
"""
1. Use yt-dlp to:
    Validate the URL
    Fetch video metadata
    Get the video_id
2. Check if the video has transcripts
3. If yes → fetch transcript using youtube_transcript_api
4. If not → return metadata only (no transcript)
"""
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)
import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError


def fetch_video_metadata(url: str) -> dict:
    options = {
        "skip_download": True,
        # don't download or processing a playlist if the URL points to one.
        "noplaylist": True, 
        "quiet": True,          # Hide normal output
        "no_warnings": True,    # Hide warnings
        "logger": None,         # Disable internal logger
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)

    # this is for playlist not supported    
    if(
        info.get("_type") == "playlist"
        or "entries" in info
        or info.get("playlist_count") is not None
        or info.get("playlist_id") is not None
    ):
        raise Exception("Playlist not supported")

    return {
        "video_id": info["id"],
        "title": info.get("title"),
        "uploader": info.get("uploader"),
        "upload_date": info.get("upload_date"),
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail"),
        "view_count": info.get("view_count"),
    }



# def fetch_transcript(video_id: str, languages=("en",)) -> dict | None:
#     try:
#         # checks which transcripts (captions) are available for that video 
#         # without downloading anything yet. return object of all available transcripts
#         youTubeTranscriptApi = YouTubeTranscriptApi()
#         transcript_list = youTubeTranscriptApi.list(video_id)

#         # Try preferred languages first
#         for lang in languages:
#             print("lang", lang)
#             if transcript_list.find_transcript([lang]):
#                 transcript = transcript_list.find_transcript([lang])
#                 # fetch the transcript
#                 data = transcript.fetch()

#                 return {
#                     "language": transcript.language,
#                     "language_code": transcript.language_code,
#                     "is_generated": transcript.is_generated,
#                     "text": " ".join(item.text for item in data),
#                 }
#         # If we don't find the preferred languages, try to get the first available transcript
#         # Fallback: first available transcript or automatically generated ones
#         print("hello hello", transcript_list)
#         transcript = transcript_list.find_generated_transcript(
#             [t.language_code for t in transcript_list]
#         )
#         print("don", transcript_list)
#         data = transcript.fetch()

#         return {
#             "language": transcript.language,
#             "language_code": transcript.language_code,
#             "is_generated": transcript.is_generated,
#             "text": " ".join(item.text for item in data),
#         }

#     # except (TranscriptsDisabled, NoTranscriptFound):
#     except Exception as e:
#         raise e

def fetch_transcript(video_id: str, languages=("en",)):
    try:
        transcript_list = YouTubeTranscriptApi().list(video_id)

        # 1️⃣ Try manual transcripts first
        for lang in languages:
            try:
                transcript = transcript_list.find_transcript([lang])
                data = transcript.fetch()
                return _format(transcript, data)
            except NoTranscriptFound:
                pass

        # 2️⃣ Try auto-generated transcripts
        for lang in languages:
            try:
                transcript = transcript_list.find_generated_transcript([lang])
                data = transcript.fetch()
                return _format(transcript, data)
            except NoTranscriptFound:
                pass

        # 3️⃣ FINAL fallback: ANY available transcript
        transcript = next(iter(transcript_list))
        data = transcript.fetch()
        return _format(transcript, data)

    except TranscriptsDisabled:
        return None


def _format(transcript, data):
    return {
        "language": transcript.language,
        "language_code": transcript.language_code,
        "is_generated": transcript.is_generated,
        "text": " ".join(item.text for item in data),
    }


def get_video_with_metadata_transcript(url: str) -> dict:
    try:
        metadata = fetch_video_metadata(url)
        transcript = fetch_transcript(metadata["video_id"])
        return {
            "metadata": metadata,
            "transcript": transcript,
        }

    # this about fetching video metadata form yt-dlp
    except ExtractorError:
        return {"error": "Video unavailable or restricted"}
    except DownloadError:
        return {"error": "The video is unavailable or restricted"}

    # TranscriptsDisabled, NoTranscriptFound this for transcript fetching
    # transcript from youtube_transcript_api
    except TranscriptsDisabled:
        return {"error": "Video does not allow transcript extraction"}
    except NoTranscriptFound:
        return {"error": "No transcript found for this video"}
    
    except Exception as e:
        if(e.__str__() == "Playlist not supported"):
            return {"error": "Selecte video from playlist because playlist not supported"}
        return {"error": str(e)}



if __name__ == "__main__":
    # video without auto script 
    url = "https://www.youtube.com/watch?v=9eWw6pGrkPs&list=RDgaGA8SB4ias&index=5"
    # video with auto script
    # url = "https://www.youtube.com/watch?v=mejpW0y_4Ms&list=RDgaGA8SB4ias&index=2"
    # playlist
    # url = "https://www.youtube.com/playlist?list=PLGfh57P6nF9E8Lm-sANY-AxiP8uB5weG0"
    result = get_video_with_metadata_transcript(url)
    print(result)
