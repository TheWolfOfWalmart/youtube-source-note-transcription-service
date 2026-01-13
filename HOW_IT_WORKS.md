# How the Custom YouTube Transcriber MCP Works

Congratulations on finishing the Python Crash Course! This project is a great practical example of combining **Python**, **Docker**, and the **Model Context Protocol (MCP)**.

This document breaks down the `transcriber` service we built, explaining line-by-line how it turns a YouTube URL into text for your AI agents.

---

## 1. The Core Logic (`server.py`)

This script is the "Brain" of the operation. It uses the `mcp` library to define tools that AI agents can call.

### A. Importing Libraries
```python
from mcp.server.fastmcp import FastMCP
import yt_dlp
import os
import glob
from faster_whisper import WhisperModel
```
*   **`FastMCP`**: A helper from the official MCP SDK that makes creating servers very easy (using decorators like `@tool`).
*   **`yt_dlp`**: The robust library that downloads video/audio from YouTube. It handles the complex logic of parsing YouTube pages.
*   **`faster_whisper`**: A highly optimized version of OpenAI's Whisper model. It runs faster and uses less memory.

### B. Initializing the Server & Model
```python
mcp = FastMCP("YouTube Transcriber")

model_size = "base" 
model = WhisperModel(model_size, device="cpu", compute_type="int8")
```
*   **`mcp = ...`**: We name our server.
*   **`model = ...`**: We load the Whisper neural network. 
    *   `base`: A balance between speed and accuracy. 
    *   `device="cpu"`: We force it to run on the Processor (CPU) instead of Graphics Card (GPU) for compatibility.
    *   `int8`: "Quantization". It makes the model smaller (8-bit integers instead of 32-bit floats) so it runs faster with minimal accuracy loss.

### C. The Tool Definition
```python
@mcp.tool()
def transcribe_youtube(url: str) -> str:
    """
    Downloads audio from a YouTube URL and transcribes it using Whisper.
    Returns the full text transcript.
    """
```
*   **`@mcp.tool()`**: This is a **Decorator**. It tells the MCP library: "Expose this function to the AI."
*   **Type Hinting (`url: str`)**: Critical for MCP. The AI looks at this to know it *must* provide a string.
*   **Docstring**: The text inside `"""..."""` is sent to the AI. It tells the AI *what* this tool does and *when* to use it.

### D. The Execution Flow
Inside `transcribe_youtube`, we do two main things:

**Step 1: Download Audio (`yt_dlp`)**
```python
ydl_opts = {
    'format': 'bestaudio/best',      # get best audio available
    'outtmpl': '/tmp/%(id)s.%(ext)s', # save to /tmp/VIDEO_ID.ext
    'postprocessors': [{             # Convert whatever format to mp3
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
    }],
}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=True)
```
We configure `yt_dlp` to download *only* audio and convert it to MP3 using `ffmpeg`.

**Step 2: Transcribe (`model.transcribe`)**
```python
segments, info = model.transcribe(audio_path, beam_size=5)
for segment in segments:
    transcript_text += segment.text + " "
```
We feed the MP3 file to the AI model. It returns "segments" (chunks of text with timestamps). We loop through them and glue them together into one big string.

---

## 2. The Container (`Dockerfile`)

This file tells Docker how to build the "Computer" that runs your script.

```dockerfile
# 1. Base Image: Start with a slim Linux version containing Python 3.11
FROM python:3.11-slim

# 2. System Deps: Install FFmpeg (needed for audio conversion) and Node.js
RUN apt-get update && apt-get install -y ffmpeg curl ...
RUN curl ... | bash - && apt-get install -y nodejs

# 3. Supergateway: Install the bridge
RUN npm install -g supergateway

# 4. Python Libs: Install our script's dependencies
RUN pip install "mcp[cli]" yt-dlp faster-whisper ffmpeg-python

# 5. Copy Code: Put our script inside the container
COPY server.py /app/server.py

# 6. Command: The command that runs when the container starts
CMD ["npx", "supergateway", "--port", "8080", "--stdio", "python server.py"]
```

**Key Concept: stdio vs HTTP**
*   Our Python script talks via **Standard Input/Output (stdio)** (printing JSON to the console).
*   **Supergateway** wraps this. It listens on port 8080 (HTTP/SSE), receives requests from n8n, translates them to stdio for Python, and sends the result back over HTTP. This lets n8n (a web app) talk to a command-line script.

---

## 3. How to Connect (n8n)

In n8n, you will use the **MCP Client** node (or generic HTTP Request if using raw SSE, but n8n has MCP support).

*   **Connection Type:** SSE (Server-Sent Events)
*   **URL:** `https://transcriber-mcp.your-domain.com/sse`

When you connect, the Agent will "see" the `transcribe_youtube` tool automatically because of the `@mcp.tool()` decorator!

---

## 4. Troubleshooting: Permissions

If you find that Obsidian (the app) or the Obsidian MCP server cannot write to the \/vaults\ directory, it is likely because the Docker volume was created with \oot\ ownership.

To fix this, run the following command on the host:

\\ash
docker run --rm -v obsidian_vaults:/vaults alpine chown -R 1000:1000 /vaults
\
This command starts a tiny temporary container (\lpine\), mounts your vault volume, and changes the ownership of all files to user ID \1000\ (your primary user), which matches the \PUID\ and \PGID\ in your configuration.
