# YouTube Video Summarizer (with DeepSeek)

This project extracts YouTube video transcripts and summarizes them using DeepSeek's API.

## Features
- Input a YouTube video URL
- Extract the transcript using `yt-dlp`
- Send the transcript to DeepSeek for summarization
- View the summary in a Streamlit app

## Setup Instructions

```bash
git clone <repo_url>
cd youtube_summarizer
pip install -r requirements.txt
cp app/.env.example app/.env
```

Add your DeepSeek API key in the `.env` file:

```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

## Run the App

```bash
streamlit run app/app.py
```
