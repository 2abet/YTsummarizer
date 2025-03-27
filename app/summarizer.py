import os
import requests
import yt_dlp
from dotenv import load_dotenv
import streamlit as st
HUGGINGFACE_API_KEY = st.secrets["HUGGINGFACE_API_KEY"]

def get_transcript(video_url):
    ydl_opts = {
        "quiet": False,  # enable logs
        "writesubtitles": True,
        "writeautomaticsub": True,
        "skip_download": True,
        "subtitlesformat": "vtt",
        "subtitleslangs": ["en"],
        "outtmpl": "%(id)s.%(ext)s",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        print("INFO:", info_dict.keys())

        subtitles = info_dict.get("subtitles")
        auto_captions = info_dict.get("automatic_captions")

        print("Subtitles:", subtitles)
        print("Automatic Captions:", auto_captions)

        # Try subtitles first, then auto-captions
        captions = subtitles or auto_captions
        if not captions or "en" not in captions:
            return None

        subtitle_url = captions["en"][0]["url"]
        response = requests.get(subtitle_url)
        if response.status_code != 200:
            print("Subtitle download failed:", response.status_code)
            return None

        lines = response.text.splitlines()
        transcript = []
        for line in lines:
            if "-->" not in line and line.strip():
                transcript.append(line.strip())

        return " ".join(transcript)

def summarize_text(text):
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": text,
        "parameters": {"max_length": 130, "min_length": 30, "do_sample": False}
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
