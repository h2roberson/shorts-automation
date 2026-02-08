import os
import requests
import random
from openai import OpenAI
from moviepy.editor import *

# Load Keys
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
PEXELS_KEY = os.environ.get("PEXELS_API_KEY")
ELEVEN_KEY = os.environ.get("ELEVENLABS_API_KEY")

def get_quote_and_topic():
    # 1. Generate a topic/quote
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a stoic philosopher. Give me a deep, short motivational quote (max 15 words) and a 1-word search term for a background video. Format: Quote|SearchTerm"}]
    )
    content = response.choices[0].message.content
    print(f"Generated: {content}")
    return content.split("|")

def get_stock_video(query):
    # 2. Find a video on Pexels
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1&orientation=portrait"
    r = requests.get(url, headers=headers)
    video_url = r.json()['videos'][0]['video_files'][0]['link']
    
    # Download it
    with open("background.mp4", "wb") as f:
        f.write(requests.get(video_url).content)
    print("Video downloaded.")
    return "background.mp4"

def get_voiceover(text):
    # 3. Get Voice from ElevenLabs
    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM" # Uses "Rachel" voice
    headers = {"xi-api-key": ELEVEN_KEY, "Content-Type": "application/json"}
    data = {"text": text, "model_id": "eleven_monolingual_v1"}
    
    r = requests.post(url, json=data, headers=headers)
    with open("voice.mp3", "wb") as f:
        f.write(r.content)
    print("Voice downloaded.")
    return "voice.mp3"

def make_video(quote, video_path, audio_path):
    # 4. Edit together
    audio = AudioFileClip(audio_path)
    video = VideoFileClip(video_path).subclip(0, audio.duration + 1)
    
    # Resize to vertical 9:16 just in case
    video = video.resize(height=1920)
    video = video.crop(x1=video.w/2 - 540, width=1080)
    
    video = video.set_audio(audio)
    
    # Add Text Overlay
    txt_clip = TextClip(quote, fontsize=70, color='white', font='Arial-Bold', size=(800, None), method='caption')
    txt_clip = txt_clip.set_position('center').set_duration(video.duration)
    
    final = CompositeVideoClip([video, txt_clip])
    final.write_videofile("final_short.mp4", fps=24)
    print("Video successfully rendered!")

if __name__ == "__main__":
    quote_text, search_term = get_quote_and_topic()
    vid_file = get_stock_video(search_term)
    aud_file = get_voiceover(quote_text)
    make_video(quote_text, vid_file, aud_file)
