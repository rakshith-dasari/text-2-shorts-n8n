# text-2-shorts-n8n
Automated, zero-cost pipeline that turns Reddit posts into fully-captioned YouTube Shorts using n8n, self-hosted Whisper, Kokoro-TTS, and DeepSeek-R1 Qwen.

## Features
- Completely open-source stack

- End‑to‑end workflow orchestrated in n8n on Docker
  
- Post to speech with natural‑sounding voice‑over with [Kokoro](https://github.com/hexgrad/kokoro?tab=readme-ov-file)
  
- Speech to Subtitles via OpenAI Whisper and custom Python script.
  
- DeepSeek‑R1 Qwen‑8.5B LLM hosted for free on [OpenRouter](https://openrouter.ai/) to craft catchy titles, descriptions & tags

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) to download copyright free videos and [FFmpeg](https://ffmpeg.org/) to generate final video
  
- YouTube upload through official Data API v3


## Workflow Screenshot:

![image](https://github.com/user-attachments/assets/a43efef1-4162-4bc6-8ffb-fd2b4ca46d81)
