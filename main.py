import os
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
        playlist_data = [
            {
                'playlistId': item['snippet']['playlistId'],
                'channelTitle': item['snippet']['videoOwnerChannelTitle'],
                'channelId': item['snippet']['videoOwnerChannelId'],
                'title': item['snippet']['title'],
                'videoId': item['snippet']['resourceId']['videoId'],
                'description': item['snippet']['description'],
                'thumbnailUrl': item['snippet']['thumbnails']['maxres']['url']
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

# Path to save transcripts and summaries (must end in forward slash, i.e. '/root/folder/')
folder_path = ''

# Replace 'PLAYLIST_ID' with the ID of the YouTube playlist
playlist_id = 'PLqR0DrEFzD9ufgr22HZod71yFKMqekKwp'
playlist_data = get_playlist_video_data(playlist_id)

for video in playlist_data:
  if video["videoId"]:
      print(f"Processing video: {video['title']}")

      transcript = get_transcript_with_timestamps(video['videoId'])

      header = f"▬▬▬▬▬▬ METADATA ▬▬▬▬▬▬\n" + f"TITLE: {video['title']}\n" + f"CHANNEL TITLE: {video['channelTitle']}\n" + f"THUMBNAIL URL: {video['thumbnailUrl']}\n" + f"VIDEO ID: {video['videoId']}\n" + f"CHANNEL ID: {video['channelId']}\n" + f"PLAYLIST ID: {video['playlistId']}\n\n" + f"DESCRIPTION: {video['description']}\n" + f"▬▬▬▬▬▬ END OF METADATA ▬▬▬▬▬▬\n\n"

      filename = f'{folder_path}{video["title"][:30]} by {video["channelTitle"]}'

      if transcript:
          full_transcript_text_only = ''
          transcript_text_with_timestamps = ''

          for line in transcript:
              line_of_text = line['text']
              start_time = round(line['start'],2)
              end_time = round(line['start'] + line['duration'], 2)
              transcript_text_with_timestamps += f"{line_of_text} ({start_time} - {end_time})\n"
              full_transcript_text_only += f"{line_of_text} "
          save_to_file(header + transcript_text_with_timestamps, f'{filename} - (TRANSCRIPT).txt')
          # print(full_transcript_text_only)
      else:
          print(f"No transcript found for video: {video['title']}")