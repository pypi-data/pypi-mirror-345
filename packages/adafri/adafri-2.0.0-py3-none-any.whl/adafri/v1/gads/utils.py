from googleapiclient.discovery import build as discovery_build
import os

YOUTUBE_API_SERVICE_NAME = os.environ.get('YOUTUBE_API_SERVICE_NAME')
YOUTUBE_API_VERSION = os.environ.get('YOUTUBE_API_VERSION')
YOUTUBE_API_DEVELOPER_KEY = os.environ.get('YOUTUBE_API_DEVELOPER_KEY')

def search_youtube_channel_by_id(query): 
    if YOUTUBE_API_SERVICE_NAME is None or YOUTUBE_API_VERSION is None or YOUTUBE_API_DEVELOPER_KEY is None:
        return []
    youtube_object = discovery_build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey = YOUTUBE_API_DEVELOPER_KEY) 
    search_keyword = youtube_object.channels().list(id=query, part="id, snippet", maxResults=1).execute() 
    # extracting the results from search response 
    results = search_keyword.get("items", [])
    print(results)
    channels = [] 
    # extracting required info from each result object 
    for result in results:
        if result['kind'] == "youtube#channel":
            channels.append({
                'id': '',
                'channelId': result["id"],
                'name': result["snippet"]["title"],
                'snippet': result['snippet']['description'],
                'thumbnails': result['snippet']['thumbnails']['medium']['url'],
            })
    return channels

def search_youtube_video_by_id(query): 
    if YOUTUBE_API_SERVICE_NAME is None or YOUTUBE_API_VERSION is None or YOUTUBE_API_DEVELOPER_KEY is None:
        return []
    youtube_object = discovery_build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey = YOUTUBE_API_DEVELOPER_KEY) 
    search_keyword = youtube_object.videos().list(id=query, part="id, snippet", maxResults=1).execute() 
    # extracting the results from search response 
    results = search_keyword.get("items", [])  
    videos = []
    print(results)
    # extracting required info from each result object 
    for result in results:
        if result['kind'] == "youtube#video":
            videos.append({
                'id': '',
                'videoId': result["id"],
                'name': result["snippet"]["title"],
                'snippet': result['snippet']['description'],
                'thumbnails': result['snippet']['thumbnails']['medium']['url'],
            })
    return videos
