"""
1. Use yt-dlp to:
    Validate the URL
    Fetch video metadata
Get the video_id
2. Check if the video has transcripts
3. If yes → fetch transcript using youtube_transcript_api
4. If not → return metadata only (no transcript)
"""

# mad by gml 4.7
"""
Robust YouTube Fetcher:
1. Fetches metadata using yt-dlp.
2. Fetches transcripts using youtube_transcript_api.
3. Returns a detailed dictionary including specific error messages for any failures.
"""

import logging
from typing import Dict, Any, List, Optional

import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    CouldNotRetrieveTranscript,
)

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def fetch_video_metadata(url: str) -> Dict[str, Any]:
    """
    Fetches metadata for a single video.
    Raises specific exceptions if fetching fails.
    """
    options = {
        "skip_download": True,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "logger": None,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)

    if info.get("_type") == "playlist":
        raise ValueError("Playlists are not supported. Please provide a single video URL.")

    return {
        "video_id": info.get("id"),
        "title": info.get("title"),
        "uploader": info.get("uploader"),
        "upload_date": info.get("upload_date"),
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail"),
        "view_count": info.get("view_count"),
        "webpage_url": info.get("webpage_url"),
    }


def _format_transcript(transcript_obj, transcript_data: List[Dict]) -> Dict[str, Any]:
    return {
        "language": transcript_obj.language,
        "language_code": transcript_obj.language_code,
        "is_generated": transcript_obj.is_generated,
        "text": " ".join(item.text for item in transcript_data),
    }


def fetch_transcript(
    video_id: str, languages: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Fetches transcript with specific fallback logic.
    Raises exceptions if no transcript is found or fetching fails.
    """
    if languages is None:
        languages = ["en"]

    transcript_list = YouTubeTranscriptApi().list(video_id)

    # Helper to try fetching specific types
    def try_fetch(transcript_list, lang_codes, generated=False):
        for lang in lang_codes:
            try:
                if generated:
                    t = transcript_list.find_generated_transcript([lang])
                else:
                    t = transcript_list.find_transcript([lang])
                return _format_transcript(t, t.fetch())
            except NoTranscriptFound:
                continue
        return None

    # 1. Try manual
    result = try_fetch(transcript_list, languages, generated=False)
    if result:
        return result

    # 2. Try auto-generated
    result = try_fetch(transcript_list, languages, generated=True)
    if result:
        return result

    # 3. Fallback to ANY available
    try:
        available_transcript = next(iter(transcript_list))
        return _format_transcript(available_transcript, available_transcript.fetch())
    except StopIteration:
        # This specific exception means we iterated but found nothing
        raise NoTranscriptFound("No transcripts found in any language.")


def get_video_with_metadata_transcript(url: str) -> Dict[str, Any]:
    """
    Main function to fetch video data and handle all exceptions explicitly for the user.
    
    Returns a dictionary with:
    - metadata: (dict or None)
    - transcript: (dict or None)
    - metadata_error: (str or None) - Reason metadata failed
    - transcript_error: (str or None) - Reason transcript failed
    """

    result = {
        "metadata": None,
        "transcript": None,
        "metadata_error": None,
        "transcript_error": None,
    }

    # --- STEP 1: FETCH METADATA ---
    try:
        result["metadata"] = fetch_video_metadata(url)
    except ValueError as e:
        # Specific handling for the custom playlist error
        result["metadata_error"] = str(e)
    except DownloadError as e:
        # yt-dlp download error (e.g. Geo-blocking, private video)
        result["metadata_error"] = f"Video unavailable or restricted: {str(e)}"
    except ExtractorError as e:
        # yt-dlp extractor error (e.g. Invalid URL)
        result["metadata_error"] = f"Invalid URL or extraction error: {str(e)}"
    except Exception as e:
        result["metadata_error"] = f"Unexpected error fetching metadata: {str(e)}"

    # If metadata failed completely, we cannot get a transcript (no video_id)
    if result["metadata_error"]:
        return result

    # --- STEP 2: FETCH TRANSCRIPT ---
    # We only run this if metadata succeeded, but we catch errors independently
    # so that a transcript failure doesn't hide the valid metadata.
    try:
        video_id = result["metadata"]["video_id"]
        result["transcript"] = fetch_transcript(video_id)
        
    except TranscriptsDisabled:
        result["transcript_error"] = "Transcripts are disabled for this video by the uploader."
    except NoTranscriptFound:
        result["transcript_error"] = "No transcripts found (manual or auto-generated)."
    except VideoUnavailable:
        # Rare case where metadata passes but transcript API sees it as gone
        result["transcript_error"] = "Video became unavailable while fetching transcript."
    except CouldNotRetrieveTranscript as e:
        # Network issues or YouTube API refusing connection
        result["transcript_error"] = f"Could not retrieve transcript (API error): {str(e)}"
    except Exception as e:
        result["transcript_error"] = f"Unexpected error fetching transcript: {str(e)}"

    return result


if __name__ == "__main__":
    # --- SCENARIOS TO TEST ---
    
    # 1. Valid video with transcript
    # url = "https://www.youtube.com/watch?v=hXaJmpjTiCk&list=RDbWDEyHBZQOQ&index=4"
    url = "https://www.youtube.com/watch?v=fqMOX6JJhGo"
    
    # 2. Valid video WITHOUT transcript (e.g. some music videos)
    # url = "https://www.youtube.com/watch?v=9eWw6pGrkPs&list=RDgaGA8SB4ias&index=5"
    
    # 3. Private Video / Geo-blocked
    # url = "https://www.youtube.com/watch?v=YbJOTdZBX1g" # (Example private video ID)
    
    # 4. Invalid URL
    # url = "https://www.youtube.com/watch?v=invalid_id_here"

    result = get_video_with_metadata_transcript(url)

    # --- DISPLAY RESULTS FOR USER ---
    # import json
    # print(json.dumps(result, indent=4,ensure_ascii=False))
    print(result)