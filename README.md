# YouTube Source Note Transcription Service

![](docs/Pasted%20image%2020260113081654.png)

## Overview
Supergateway is a self-hosted, containerized infrastructure stack designed to bridge the gap between ephemeral information streams (YouTube) and long-term knowledge bases (Obsidian). It runs entirely within a private AI Sandbox, ensuring data sovereignty and local control.

By utilizing the **Model Context Protocol (MCP)** and **Supergateway**, this project enables networked AI agents (n8n, Custom GPTs) to autonomously "watch," transcribe, and synthesize video content into structured **Zettelkasten** notes. 
![](docs/graph%20view.png)
## The Context: GTD Meets Zettelkasten
My everyday routine combines **Getting Things Done (GTD)** for task management with **Zettelkasten** for knowledge management.
*   **GTD (The Inbox):** All potentially useful inputs (ideas, links, articles) are dumped into an Inbox to be sorted during a daily review.
*   **Zettelkasten (The Database):** Useful content is processed into "Source Notes," from which "Atomic Notes" (single concepts, independent of the source) are extracted and linked to build a web of semantically connected information.

### The Problem: The Video Backlog
I found my Inbox accumulating too many YouTube links—technical lectures, tutorials, and industry analysis—tagged for "review." The friction of watching a 40-minute video to extract a handful of atomic notes created a massive bottleneck. 

### The Insight
**Reading is faster than watching.** 
I realized that processing a high-fidelity transcript allows for rapid scanning, searching, and extraction of concepts, significantly increasing the velocity of information entering the Zettelkasten. 

![Insight](docs/Pasted%20image%2020260113082925.png)

Beyond efficiency, managing my PKM in this way essentially turns me into a **human embedding model** for my own knowledge. By manually extracting and linking atomic notes, I am pre-processing information so that its semantic value can be utilized directly by a terminal-based AI during conversational reasoning and project management, rather than being probabilistically determined in vector-similarity like a traditional RAG pipeline.

## The Workflow
**By combining custom local transcription with Supergateway, I can treat YouTube as a text-based, queryable database:**
1.  **Input**: I send a YouTube link to my personal assistant bot/agent on **Telegram**.
2.  **Transcription**: The self-hosted system pulls the required models from **Hugging Face** on first run and transcribes audio locally using `faster-whisper` (GPU-accelerated) within the AI Sandbox.
3.  **Synthesis**: The agent processes the raw text into a summarized "Source Note," using an adjustable "verbosity" parameter in the agent prompt.
4.  **Output**: The agent injects the completed note into my local Obsidian vault and places a link to it in my **GTD Inbox**, ready for processing during my morning review.

## The Architecture
The stack consists of two primary self-hosted MCP servers coordinated via Docker Compose, made accessible through **Supergateway**:

1.  **YouTube Transcriber**:
    -   **Engine**: `faster-whisper` (OpenAI Whisper optimized for performance).
    -   **Function**: Downloads audio from any YouTube URL via `yt-dlp` and performs high-accuracy transcription locally using models sourced from **Hugging Face**.
    -   **Hardware**: Configured for NVIDIA GPU acceleration (CUDA) for near-instant transcription of long-form content.
2.  **Obsidian Bridge**:
    -   **Function**: Provides a secure interface for AI agents to read from and write to the local Obsidian vault. 
    -   **Implementation**: This service utilizes the community-developed **Obsidian MCP Server** in conjunction with the **Obsidian REST API** plugin to enable standardized programmatic access to the vault.
    -   **Security**: Token-based authentication and restricted volume mounting to the host filesystem.

## Connectivity via Supergateway
Standard MCP servers typically communicate over **Standard Input/Output (stdio)**, making them difficult to access for cloud-hosted AI agents or automation platforms like n8n.

I use **Supergateway** (the SSE transport engine) to:
-   Wrap these stdio-based Python scripts into an **SSE (Server-Sent Events)** server.
-   Provide a stable HTTP endpoint reachable via a reverse proxy (Caddy).
-   Enable seamless integration between my local AI Sandbox and n8n's MCP Client node.

## System Stack
-   **Language**: Python 3.11 (FastMCP SDK)
-   **Infrastructure**: Self-Hosted Docker Swarm / Compose
-   **AI Models**: Faster-Whisper (Base/Medium)
-   **Networking**: SSE over HTTP, Caddy Reverse Proxy
-   **Integration**: n8n, AI Agents, Obsidian

## Setup
1.  Clone the repository.
2.  Copy `.env.example` to `.env` and provide your `OBSIDIAN_API_KEY`.
3.  Deploy the stack:
    ```bash
    docker-compose up -d --build
    ```
4.  Point your n8n MCP node to `https://transcriber-mcp.your-domain.com/sse`.

---
*Project Status: Active / Tooling*
