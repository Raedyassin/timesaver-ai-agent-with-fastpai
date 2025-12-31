from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import yt_dlp 
from yt_dlp.utils import DownloadError, ExtractorError

OUTPUB_DIR = "output" 
def get_youtube_transcript(video_id: str):
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_data = ytt_api.fetch(video_id)
        # Convert list → clean text
        transcript = " ".join([item.text for item in transcript_data])
        # print(dir(transcript_data))
        for t in transcript_data:
            print(t.is_generated)
            print(t.language)
            print(t.language_code)
            print(t.video_id)
        # return transcript

        # with open("transcript.txt", "a", encoding="utf-8") as file:
        #     file.write(transcript) 
    except TranscriptsDisabled:
        return "❌ This video does not allow transcript extraction."
    except NoTranscriptFound:
        return "❌ No transcript found for this video (maybe no subtitles)."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def video_metadata(url: str):
  options = {
      'format': 'best',  # Standard option, though not strictly needed for metadata
      'noplaylist': True, # Only process the single video, not a potential playlist
      'skip_download': True, # Crucial: tells yt-dlp NOT to download the actual file
      'quiet': True, # Suppresses console output/warnings from yt-dlp
      'force_json': True, # Ensures output is JSON-like internally
      # 'extractor_args': ['youtube:player_client=default'], # This for this package need NodeJS, so will not show his warning
  }
  try:
    with yt_dlp.YoutubeDL(options) as ydl:
      info = ydl.extract_info(url, download=False)
    return {
      "title": info["title"],
      "uploader": info["uploader"],
      "upload_date": info["upload_date"],
      "duration": info["duration"],
      "thumbnail": info["thumbnail"],
      "view_count": info["view_count"],
      "video_id": info["id"]
    }
  except ExtractorError as e:
        # 1. Handle errors related to the video itself (e.g., unavailable, private)
        print("❌ Video Extractor Error:")
        print(f"   The video is unavailable or restricted. Details: {e}")
        
  except DownloadError as e:
      error_message = str(e)
      print(dir(e))
      # 2. Check for specific HTTP errors by inspecting the message
      
      if "HTTP Error 404: Not Found" in error_message:
          print("🛑 HTTP 404 Error:")
          print("   The video URL is invalid, or the video has been deleted.")
          
      elif "HTTP Error 403: Forbidden" in error_message:
          print("🛑 HTTP 403 Error:")
          print("   The video may be age-restricted, geographically blocked (geo-restricted), or requires sign-in.")
          
      elif "HTTP Error 429: Too Many Requests" in error_message:
          print("🛑 HTTP 429 Error (Rate Limiting):")
          print("   The service is temporarily blocking requests from your IP. Wait and try again.")
          
      else:
          # 3. Handle all other DownloadErrors (network issues, etc.)
          print("❌ Download/General Error:")
          print(f"   A general download/network issue occurred. Details: {error_message}")
  except Exception as e:
    return f"❌ Error: {str(e)}"f

if __name__ == "__main__":
  url = "https://www.youtube.com/shorts/tbVfq9iOb8I"
  # url = "https://www.youtube.com/watch?v=xBZvAFKoqiA&list=RDMNObsbXKZA0&index=4"
  video_metadata =video_metadata(url)
  print(get_youtube_transcript(video_metadata["video_id"]))
