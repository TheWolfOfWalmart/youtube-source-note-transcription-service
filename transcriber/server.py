from mcp.server.fastmcp import FastMCP
import yt_dlp
import os
import glob
from faster_whisper import WhisperModel

# Initialize MCP Server
mcp = FastMCP("YouTube Transcriber")

# Initialize Whisper Model (download on first run)
# 'tiny' or 'base' is good for CPU. 'medium'/'large' for GPU.
# We'll use 'base' for GPU inference. Can upgrade to 'small' or 'medium' for better accuracy.
model_size = "base" 
try:
    model = WhisperModel(model_size, device="cuda", compute_type="float16")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

@mcp.tool()
def transcribe_youtube(url: str) -> str:
    """
    Downloads audio from a YouTube URL and transcribes it using Whisper.
    Returns the full text transcript.
    """
    if not model:
        return "Error: Whisper model failed to load."

    print(f"Processing URL: {url}")
    
    # 1. Download Audio with yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '/tmp/%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info['id']
            # Find the file
            files = glob.glob(f"/tmp/{video_id}.mp3")
            if not files:
                return "Error: Audio download failed."
            audio_path = files[0]
            
            print(f"Audio downloaded to: {audio_path}")

            # 2. Transcribe
            segments, info = model.transcribe(audio_path, beam_size=5)
            
            transcript_text = ""
            for segment in segments:
                transcript_text += segment.text + " "
            
            # Cleanup
            os.remove(audio_path)
            
            return transcript_text.strip()

    except Exception as e:
        return f"Error during transcription: {str(e)}"

if __name__ == "__main__":
    mcp.run()
