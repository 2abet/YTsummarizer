import os
import requests
import yt_dlp
from dotenv import load_dotenv

load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

def get_transcript(video_url):
    ydl_opts = {
        "quiet": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "skip_download": True,
        "subtitlesformat": "vtt",
        "subtitleslangs": ["en"],
        "outtmpl": "%(id)s.%(ext)s",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        subtitles = info_dict.get("subtitles") or info_dict.get("automatic_captions")
        if not subtitles or "en" not in subtitles:
            return None
        
        # Attempt to fetch subtitle URL
        subtitle_url = subtitles["en"][0]["url"]
        response = requests.get(subtitle_url)
        if response.status_code != 200:
            return None

        # Parse WebVTT to plain text
        lines = response.text.splitlines()
        transcript = []
        for line in lines:
            if "-->" not in line and line.strip() != "":
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
