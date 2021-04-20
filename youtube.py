# Youtube History Calculator
# Tutorial - https://www.thepythoncode.com/article/using-youtube-api-in-python

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

import urllib.parse as p
import re
import os
import pickle

import math
import json

# pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

path = 'history/watch-history.json'
key_file_name = "yt_api_key.txt"


SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

h = []
m = []
s = []

def main():

    print()
    
    # get watch history from json
    with open(path, 'r', encoding='utf8') as f:
        history = json.load(f)
    
    print("Please wait...")
    print(len(history), " total videos watched")
    
    # get time from api
    deleted = 0
    start = 0
    end = len(history)
    # start = 9956
    for i in range(start, end):
        try:
            dur = get_time(history[i]["titleUrl"])
        except HttpError:
            print(f"Ran out of our request quota at index {i} :( stupid google")
            break
        except:
            #print("A video you watched has been deleted/made private (duration not added)")
            deleted += 1
        else:
            h.append(parse_index(dur[0]))
            m.append(parse_index(dur[1]))
            s.append(parse_index(dur[2]))
         
    # add up all the times
    print(f"{deleted} videos were not accounted for due to being deleted/made private")
    calc_time()
    
            
def calc_time():
    time_hours = sum(h)
    time_mins = sum(m)
    time_secs = sum(s)
    
    time_mins += math.floor(time_secs / 60.0)
    time_secs = time_secs % 60
    
    time_hours += math.floor(time_mins / 60.0)
    time_mins = time_mins % 60
    
    #print((time_hours, time_mins, time_secs))
    time_days = 0
    time_years = 0
    
    time_days += math.floor(time_hours / 24.0)
    time_hours = time_hours % 24
    
    time_years += math.floor(time_days / 365.0)
    time_days = time_days % 365
    
    if(time_years == 0 and time_days == 0):
        print(f"You've spent {time_hours} hours, {time_mins} mintues, and {time_secs} seconds watching youtube videos.\n")
    elif (time_years == 0):
        print(f"You've spent {time_days} days, {time_hours} hours, {time_mins} mintues, and {time_secs} seconds watching youtube videos.\n")
    else:
        print(f"You've spent {time_years} years, {time_days} days, {time_hours} hours, {time_mins} mintues, and {time_secs} seconds watching youtube videos.\n")
    
def get_time(url):
    
    #video_url = history[0]["titleUrl"]
    #video_url = "https://www.youtube.com/watch?v=vLm68qbNjkU" # 10 hour test
        
    # authenticate to YouTube API
    youtube = youtube_authenticate()
    
    # parse video ID from URL
    video_id = get_video_id_by_url(url)
    
    # make API call to get video info
    response = get_video_details(youtube, id=video_id)
    
    # get duration
    duration = response.get("items")[0]["contentDetails"]["duration"]
    parsed_duration = re.search(f"PT(\d+H)?(\d+M)?(\d+S)", duration).groups()
    
    return parsed_duration
        
        
def parse_index(input):
    if(isinstance(input, str)):
        return eval(input[:-1])
    else:
        return 0
    

def youtube_authenticate():

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    
    key_file = open(key_file_name, "r")
    api_key = key_file.read()
    key_file.close()

    return build(api_service_name, api_version, developerKey=api_key)
    
    
def get_video_id_by_url(url):

    # split URL parts
    parsed_url = p.urlparse(url)
    # get the video ID by parsing the query of the URL
    video_id = p.parse_qs(parsed_url.query).get("v")
    if video_id:
        return video_id[0]
    else:
        raise Exception(f"Wasn't able to parse video URL: {url}")
        
        
def get_video_details(youtube, **kwargs):
    return youtube.videos().list(
        part="snippet,contentDetails,statistics",
        **kwargs
    ).execute()
    
    
def print_video_infos(video_response):
    items = video_response.get("items")[0]
    # get the snippet, statistics & content details from the video response
    snippet         = items["snippet"]
    statistics      = items["statistics"]
    content_details = items["contentDetails"]
    # get infos from the snippet
    channel_title = snippet["channelTitle"]
    title         = snippet["title"]
    description   = snippet["description"]
    publish_time  = snippet["publishedAt"]
    # get stats infos
    comment_count = statistics["commentCount"]
    like_count    = statistics["likeCount"]
    dislike_count = statistics["dislikeCount"]
    view_count    = statistics["viewCount"]
    # get duration from content details
    duration = content_details["duration"]
    # duration in the form of something like 'PT5H50M15S'
    # parsing it to be something like '5:50:15'
    parsed_duration = re.search(f"PT(\d+H)?(\d+M)?(\d+S)", duration).groups()
    duration_str = ""
    for d in parsed_duration:
        if d:
            duration_str += f"{d[:-1]}:"
    duration_str = duration_str.strip(":")
    print(f"""\
    Title: {title}
    Description: {description}
    Channel Title: {channel_title}
    Publish time: {publish_time}
    Duration: {duration_str}
    Number of comments: {comment_count}
    Number of likes: {like_count}
    Number of dislikes: {dislike_count}
    Number of views: {view_count}
    """)
    
main()