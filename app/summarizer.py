import os
import requests
import yt_dlp
from dotenv import load_dotenv
import streamlit as st

# Get API key securely from Streamlit Secrets
TOGETHER_API_KEY = st.secrets["TOGETHER_API_KEY"]

def get_transcript(video_url):
    ydl_opts = {
        "quiet": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "skip_download": True,
        "subtitlesformat": "vtt",  # Prefer VTT or SRT
        "subtitleslangs": ["en"],
        "outtmpl": "%(id)s.%(ext)s"
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)

        # Check requested subtitles
        subtitles_info = info_dict.get("requested_subtitles", {}).get("en")
        if not subtitles_info:
            return None

        subtitle_url = subtitles_info.get("url")
        if not subtitle_url:
            return None

        response = requests.get(subtitle_url)
        if response.status_code != 200:
            return None

        # Handle WebVTT (vtt) or SRT format
        lines = response.text.splitlines()
        transcript = []
        for line in lines:
            if "-->" not in line and line.strip():
                transcript.append(line.strip())

        return " ".join(transcript)

def summarize_text(text):
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    # Instruction prompt for LLaMA 3
    payload = {
        "model": "meta-llama/Llama-3-8b-chat",
        "messages": [
            {
                "role": "user",
                "content": (
                    "You are a helpful assistant. Please summarize the following YouTube transcript "
                    "in a detailed and structured way, covering main points, examples, and flow:\n\n" + text
                )
            }
        ],
        "temperature": 0.3,
        "max_tokens": 512
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.text}"


def summarize_video(video_url):
    transcript = get_transcript(video_url)
    if transcript:
        return summarize_text(transcript[:2000])  # Limit input
    else:
        return "No transcript available."
