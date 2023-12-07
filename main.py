import os
from openai import OpenAI
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

# Set your API keys as an environment variable in your OS or IDE
api_key = os.environ.get('YOUTUBE_API_KEY')

def get_playlist_video_data(playlist_id):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=50  # Adjust this value to fetch more videos if needed
        )
        response = request.execute()
        videos = [item['snippet']['resourceId']['videoId'] for item in response['items']]
        playlist_data = [
            {
                'playlistId': item['snippet']['playlistId'],
                'channelTitle': item['snippet']['channelTitle'],
                'channelId': item['snippet']['channelId'],
                'title': item['snippet']['title'],
                'videoId': item['snippet']['resourceId']['videoId'],
                # 'endAt': item['contentDetails']['endAt'],
                'description': item['snippet']['description'],
                # 'thumbnailUrl': item['snippet']['thumbnails']['url']
            }
            for item in response['items']
        ]
        return playlist_data
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

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

def summarize_text(text):
  try:
      client = OpenAI()
      response = client.chat.completions.create(
          model="gpt-3.5-turbo-1106",
          # api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
          messages=[
            {"role": "system", "content": "You summarize YouTube videos solely on the video's transcript. Explain and highlight core concepts and key points in great detail."},
            {"role": "user", "content": text}
          ],
          # max_tokens=150  # Adjust the length of the summary as needed
      )
      return response.choices[0].message.content
  except Exception as e:
      print(f"Error: {str(e)}")
      return None

# Compare Pricing
# https://openai.com/pricing
# Monitor Your Usage
# https://platform.openai.com/usage
# SET TO TRUE TO ENABLE SUMMARIZATION
# THIS WILL REQUIRE A FREE OPENAI API KEY AND TOKENS PURCHASED
USE_AI = False

# Replace 'PLAYLIST_ID' with the ID of the YouTube playlist
playlist_id = 'PLqR0DrEFzD9v7tE8VWFXvKi2qku8nIQIg'
playlist_data = get_playlist_video_data(playlist_id)

for item in playlist_data:
    if item["videoId"]:
        print(f"Processing video: {item['title']}")
        transcript = get_transcript_with_timestamps(item['videoId'])
        if transcript:
            full_transcript_text_only = ''
            transcript_text_with_timestamps = ''
            for line in transcript:
                transcript_text_with_timestamps += f"{line['text']} ({line['start']} - {line['start'] + line['duration']})\n"
                full_transcript_text_only += f"{line['text']} "
            save_to_file(transcript_text_with_timestamps, f'{item["title"]} - transcript.txt')
            print(full_transcript_text_only)

            # CANT USE ALL YOUR TOKENS!
            if USE_AI:
                summarized_text = summarize_text(full_transcript_text_only)
                if summarized_text:
                    print("Summarized Text:")
                    print(summarized_text)
                    save_to_file(summarized_text, f'{item["title"]} - transcript.txt')