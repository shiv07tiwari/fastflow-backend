import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def fetch_youtube_comments(video_id, max_results=100):
    # Retrieve the API key from environment variable
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key:
        raise ValueError("YouTube API key not found. Please set the YOUTUBE_API_KEY environment variable.")

    youtube = build('youtube', 'v3', developerKey=api_key)

    comments = []
    try:
        # Fetch comments using the YouTube Data API
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_results,
            textFormat="plainText"
        )

        while request and len(comments) < max_results:
            response = request.execute()

            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'author': comment['authorDisplayName'],
                    'text': comment['textDisplay'],
                    'likes': comment['likeCount'],
                    'published_at': comment['publishedAt']
                })

            # Check if there are more comments to fetch
            if 'nextPageToken' in response:
                request = youtube.commentThreads().list_next(request, response)
            else:
                break

    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred: {e.content}")

    return comments[:max_results]
