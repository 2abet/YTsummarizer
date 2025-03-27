import os
import requests
import yt_dlp
from dotenv import load_dotenv
import streamlit as st
HUGGINGFACE_API_KEY = st.secrets["HUGGINGFACE_API_KEY"]

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
    API_URL = "https://api-inference.huggingface.co/models/Falconsai/text_summarization"
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }

    # Craft a better input prompt for depth
    prompt = (
        "Please summarize the following transcript in a detailed and informative manner, "
        "highlighting key points, examples, and structure:\n\n" + text
    )

    payload = {
        "inputs": prompt[:2000],  # Truncate if needed
        "parameters": {
            "max_length": 250,     # Try 250–400 for longer summaries
            "min_length": 100,
            "do_sample": False
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()[0]['summary_text']
    else:
        return f"Error: {response.text}"


def summarize_video(video_url):
    transcript = get_transcript(video_url)
    if transcript:
        return summarize_text(transcript[:2000])  # Limit input
    else:
        return "No transcript available."
