from fastapi import FastAPI, UploadFile, File, Form
import whisper
import uvicorn
import tempfile
import os
import kokoro
from kokoro import KPipeline
import numpy as np
import soundfile as sf
import math

app = FastAPI()
model = whisper.load_model("base")  # Choose model size: tiny, base, small, etc.
tts_model = KPipeline(lang_code="a")

OUTPUT_DIR = "/app/subs"
TTS_DIR = "/app/audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TTS_DIR, exist_ok=True)

@app.post("/synthesize/")
async def synthesize(text: str = Form(...), filename: str = Form(...)):
    gen = tts_model(text, voice="af_heart")

    audio_chunks = [audio for _, _, audio in gen]
    full_audio = np.concatenate(audio_chunks)

    base_filename = os.path.splitext(filename)[0]
    file_path = os.path.join(TTS_DIR, f"{base_filename}.mp3")
    sf.write(file_path, full_audio, 24000)

    # Generate SRT file
    srt_path = await transcribe(file_path, filename)

    return {"status": "success", "length": len(full_audio)/24000}

# async def transcribe(audio_path: str, filename: str):

#     # Run transcription and get segments
#     result = model.transcribe(audio_path, task="transcribe", verbose=False, word_timestamps=True)

#     # Generate SRT filename
#     srt_path = os.path.join(OUTPUT_DIR, f"{filename}.srt")
#     index = 1

#     # Write the segments to an SRT file
#     with open(srt_path, "w", encoding="utf-8") as f:
#         for segment in result["segments"]:
#             words = segment.get("words", [])

#             if not words:
#                 # fallback to segment if word timestamps are missing
#                 words = [{"word": w, "start": segment["start"], "end": segment["end"]} for w in segment["text"].split()]

#             # Break into chunks of 2–3 words
#             chunk_size = 3
#             for i in range(0, len(words), chunk_size):
#                 chunk = words[i:i+chunk_size]
#                 chunk_text = " ".join(w["word"].strip() for w in chunk)
#                 start = chunk[0]["start"]
#                 end = chunk[-1]["end"]

#                 f.write(f"{index}\n")
#                 f.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
#                 f.write(f"{chunk_text}\n\n")
#                 index += 1

#     return {srt_path}

async def transcribe(audio_path: str, filename: str):
    result = model.transcribe(audio_path, task="transcribe", verbose=False, word_timestamps=True)

    ass_path = os.path.join(OUTPUT_DIR, f"{filename}.ass")
    index = 0

    def ass_timestamp(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int((seconds - int(seconds)) * 100)
        return f"{h:02d}:{m:02d}:{s:02d}.{cs:02d}"


    with open(ass_path, "w", encoding="utf-8") as f:
        # ASS header with styles
        f.write("""[Script Info]
Title: Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Verdana,90,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,2,0,5,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""")

        for segment in result["segments"]:
            words = segment.get("words", [])
            if not words:
                words = [{"word": w, "start": segment["start"], "end": segment["end"]} for w in segment["text"].split()]

            chunk_size = 2
            for i in range(0, len(words), chunk_size):
                chunk = words[i:i+chunk_size]
                text = " ".join(w["word"].strip() for w in chunk)
                start = chunk[0]["start"]
                end = chunk[-1]["end"]

                f.write(f"Dialogue: 0,{ass_timestamp(start)},{ass_timestamp(end)},Default,,0,0,0,,{text}\n")

    speedup_ass(ass_path, ass_path, 1.5)
    return {ass_path}

def speedup_ass(path_in: str, path_out: str, speed: float):
    with open(path_in, "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open(path_out, "w", encoding="utf-8") as f:
        for line in lines:
            if line.startswith("Dialogue:"):
                parts = line.split(",", 9)
                start = _scale_ass_time(parts[1], speed)
                end = _scale_ass_time(parts[2], speed)
                parts[1] = start
                parts[2] = end
                f.write(",".join(parts))
            else:
                f.write(line)

def _scale_ass_time(time_str: str, speed: float) -> str:
    h, m, s_cs = time_str.strip().split(":")
    s, cs = map(int, s_cs.split("."))
    total_sec = int(h)*3600 + int(m)*60 + s + cs/100
    new_sec = total_sec / speed
    h = int(new_sec // 3600)
    m = int((new_sec % 3600) // 60)
    s = int(new_sec % 60)
    cs = int((new_sec - int(new_sec)) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

# def format_timestamp(seconds: float) -> str:
#     h = int(seconds // 3600)
#     m = int((seconds % 3600) // 60)
#     s = int(seconds % 60)
#     ms = int((seconds - int(seconds)) * 1000)
#     return f"{h:02}:{m:02}:{s:02},{ms:03}"

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8881)
