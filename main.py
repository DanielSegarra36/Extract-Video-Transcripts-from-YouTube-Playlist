from googleapiclient.discovery import build
import os
from youtube_transcript_api import YouTubeTranscriptApi

# Set your API key as an environment variable or directly assign it here
api_key = os.environ.get('YOUTUBE_API_KEY')  # Replace with your actual API key

def get_playlist_videos(playlist_id):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=50  # Adjust this value to fetch more videos if needed
        )
        response = request.execute()
        videos = [item['snippet']['resourceId']['videoId'] for item in response['items']]
        return videos
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

def get_video_title(video_id):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.videos().list(part='snippet', id=video_id)
        response = request.execute()
        video_title = response['items'][0]['snippet']['title']
        return video_title
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def get_transcript_with_timestamps(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript_list
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def save_to_file(text, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(text)
        print(f"Transcript saved to '{filename}'")
    except Exception as e:
        print(f"Error saving file: {str(e)}")

# Replace 'PLAYLIST_ID' with the ID of the YouTube playlist
playlist_id = 'PLqR0DrEFzD9ufgr22HZod71yFKMqekKwp'
videos_in_playlist = get_playlist_videos(playlist_id)

for video_id in videos_in_playlist:
    video_title = get_video_title(video_id)
    if video_title:
        print(f"Processing video: {video_title}")
        transcript = get_transcript_with_timestamps(video_id)
        if transcript:
            transcript_text = ''
            for line in transcript:
                transcript_text += f"{line['text']} ({line['start']} - {line['start'] + line['duration']})\n"
            save_to_file(transcript_text, f'{video_title}_transcript.txt')