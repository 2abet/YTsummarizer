import streamlit as st
import os
from summarizer import summarize_video

st.title("YouTube Video Summarizer")

video_url = st.text_input("Enter YouTube Video URL:")

if st.button("Summarize"):
    if video_url:
        summary = summarize_video(video_url)
        st.write("## Summary")
        st.write(summary)
    else:
        st.error("Please enter a valid YouTube URL.")
