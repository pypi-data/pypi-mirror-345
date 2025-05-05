import os
import re
import typing

from .lushrequests import *
from .lushtypes import *

EXT_X_MEDIA_Regex = re.compile(r"#EXT-X-MEDIA:TYPE=([A-Za-z0-9]+),GROUP-ID=\"([A-Za-z0-9]+)\",NAME=\"([A-Za-z0-9]+)\",AUTOSELECT=([A-Za-z0-9]+),DEFAULT=([A-Za-z0-9]+)")
EXT_X_STREAM_INF_Regex = re.compile(r"#EXT-X-STREAM-INF:BANDWIDTH=(\d+),CODECS=\"([A-Za-z0-9\.,]+)\",RESOLUTION=([A-Za-z0-9]+),VIDEO=\"([A-Za-z0-9]+)\"")
    
class TwitchGQL_API:
  API_URL = "https://gql.twitch.tv/gql"
  CLIENT_ID = "kd1unb4b3q4t58fwlpcbzcbnm76a8fp"
  DEFAULT_HEADERS = { "Client-ID": CLIENT_ID }
  REQ = RateLimitedRequests(400, 60)
  
  def __raise_req_error(self, response : requests.Response):
    raise Exception(f'Status {response.status_code}: {response.reason}')
    
  def get_clip(self, clip_id : str) -> GQL_Clip:
    """Get clip information from Twitch's GQL API.

    Args:
        clip_id (string): Clip ID

    Returns:
        dict: Clip info
    """
    content = [
      {
        "operationName": "VideoAccessToken_Clip",
        "variables": {
          "slug": f"{clip_id}"
        },
        "extensions": {
          "persistedQuery": {
            "version": 1,
            "sha256Hash": "36b89d2507fce29e5ca551df756d27c1cfe079e2609642b4390aa4c35796eb11"
          }
        }
      }
    ]
    r : requests.Response = self.REQ.post(url = self.API_URL, headers = self.DEFAULT_HEADERS, json = content)
    
    if r.status_code == 200:
      response_json : typing.List[dict] = r.json()
      if len(response_json) > 0:
        response_data : dict = response_json[0].get("data", {})
        response_clip : dict = response_data.get("clip", {})
        return GQL_Clip(response_clip)
      else:
        raise GQL_Clip.DoesNotExist(f"Clip ID \"{clip_id}\" was not found.")
    else:
      self.__raise_req_error(r)
    
  def get_video(self, video_id):
    """Get video info.

    Args:
        video_id (string): Video ID

    Returns:
        dict: Video information
    """
    content = {
      "query": "query{video(id:\"" + video_id + "\"){id,title,thumbnailURLs(height:180,width:320),createdAt,publishedAt,lengthSeconds,owner{id,displayName}}}",
      "variables": {}
    }
    r : requests.Response = self.REQ.post(url = self.API_URL, headers = self.DEFAULT_HEADERS, json = content)
    
    if r.status_code == 200:
        response_json : dict = r.json()
        response_data : dict = response_json.get("data", {})
        response_video : dict = response_data.get("video", {})
        return GQL_Video(response_video)
    else:
      self.__raise_req_error(r)

  def download_clip(self, clip_id, filename, saveover = False):
    """Download a Twitch clip.

    Args:
        clip_id (string): Clip ID
        filename (string): Filename
        saveover (bool, optional): Overwrite existing files with the same name. Defaults to False.

    Returns:
        bool: Download succeeded/failed.
    """
    if (not saveover and os.path.exists(filename)):
      print(f"Skipping {clip_id} because the filename '{filename}' is taken.")
      return True
    
    info = self.get_clip(clip_id)
    
    for videoQuality in info.videoQualities:
      print(f"Attempting to download clip in \"{videoQuality.quality}\"")
      url = videoQuality.sourceURL
      signature = info.playbackAccessToken.signature
      token = info.playbackAccessToken.value_raw
      full_url = f"{url}?sig={signature}&token={token}"
      
      try:
        r = requests.get(full_url)
        if r.status_code >= 200 and r.status_code < 300:
          with open(filename, 'wb') as outfile:
            outfile.write(r.content)
            return True
        else:
          print(f"Failed to download clip with quality \"{videoQuality.quality}\": {r.reason} ({r.status_code})")
      except Exception as e:
        print(f"Failed to download clip with quality \"{videoQuality.quality}\": {e}")
      
    return False
    
  def get_video_token(self, video_id):
    content = {
      "operationName": "PlaybackAccessToken_Template", 
      "query":"query PlaybackAccessToken_Template($login: String!, $isLive: Boolean!, $vodID: ID!, $isVod: Boolean!, $playerType: String!) {  streamPlaybackAccessToken(channelName: $login, params: {platform: \"web\", playerBackend: \"mediaplayer\", playerType: $playerType}) @include(if: $isLive) {    value    signature    __typename  }  videoPlaybackAccessToken(id: $vodID, params: {platform: \"web\", playerBackend: \"mediaplayer\", playerType: $playerType}) @include(if: $isVod) {    value    signature    __typename  }}",
      "variables": {
        "isLive": False,
        "login": "",
        "isVod": True,
        "vodID": video_id,
        "playerType": "embed"
        }
      }
    
    r = self.REQ.post(url = self.API_URL, headers = self.DEFAULT_HEADERS, json = content)
    
    try:
      return r.json()['data']['videoPlaybackAccessToken']
    except:
      return {}
    
  def get_video_playlist(self, video_id, access_token):
    playlistUrl = f"http://usher.ttvnw.net/vod/{video_id}?nauth={access_token['value']}&nauthsig={access_token['signature']}&allow_audio_only=true&allow_source=true&player=twitchweb"
    
    r : requests.Response = self.REQ.get(url = playlistUrl, headers = self.DEFAULT_HEADERS)
    
    try:
      return str(r.content).split("\\n")
    except:
      return []
    
  def __get_playlist_url(self, video_id, quality : str = "720"):
    token = self.get_video_token(video_id)
    playlist = self.get_video_playlist(video_id, token)
    
    if "vod_manifest_restricted" in playlist[0] or "unauthorized_entitlements" in playlist[0]:
      print("Video restricted. Unable to download.")
      return None
    
    video_qualities : dict[str, dict] = {}
    
    for index in range(len(playlist)):
      item = playlist[index]
      
      media_match = EXT_X_MEDIA_Regex.match(item)
      if media_match:
        string_quality = media_match.group(3)
        
        stream_info_item = playlist[index + 1]
        info_match = EXT_X_STREAM_INF_Regex.match(stream_info_item)
        bandwidth = int(info_match.group(1))
        
        if string_quality not in video_qualities.keys():
          video_qualities[string_quality] = {}
          video_qualities[string_quality]["url"] = playlist[index + 2]
          video_qualities[string_quality]["bandwidth"] = bandwidth
          
    for video_quality in video_qualities.keys():
      if video_quality.lower().startswith(quality.lower()):
        return video_qualities[video_quality]
      
    return video_qualities[list(video_qualities.keys())[0]]
        
    
  def get_video_chapters(self, video_id):
    content = {
      "extensions" : { 
        "persistedQuery": {
          "sha256Hash": "8d2793384aac3773beab5e59bd5d6f585aedb923d292800119e03d40cd0f9b41",
          "version": 1
        }
      },
      "operationName": "VideoPlayer_ChapterSelectButtonVideo",
      "variables": {
        "videoID": video_id
      }
    }
    r = self.REQ.post(url = self.API_URL, headers = self.DEFAULT_HEADERS, json = content)
    try:
      return r.json()['data']['video']['moments']['edges']
    except:
      return []
    
  def __get_or_generate_video_chapters(self, video_id, video_info):
    chapters = self.get_video_chapters(video_id)
    
    if len(chapters) == 0:
      dummy_chapter = {
        "node": {
          "id": "",
          "_type": "GAME_CHANGE",
          "positionMilliseconds": 0,
          "durationMilliseconds": video_info["lengthSeconds"] * 1000,
          "description": "Unknown" if "game" not in video_info else video_info["game"]["displayName"],
          "subDescription": "",
          "details": {
            "game": {
              "id": "-1" if "game" not in video_info else video_info["game"]["id"],
              "displayName": "Unknown" if "game" not in video_info else video_info["game"]["displayName"],
              "boxArtUrl": "" if "game" not in video_info else video_info["game"]["boxArtURL"].replace("{width}", "40").replace("{height}", "40")
            }
          }
        }
      }
      
      chapters.append(dummy_chapter)
      
    return chapters
    
  def __fetch_all_chat(self, video_id):
    """Fetches the chat messages without checking uniqueness or sorting.

    Args:
        video_id (string): Video ID

    Returns:
        list: List of chat messages
    """
    content = [
      {
        "operationName": "VideoCommentsByOffsetOrCursor",
        "variables": {
          "videoID": video_id,
          "contentOffsetSeconds": 0
        },
        "extensions": {
          "persistedQuery": {
            "version": 1,
            "sha256Hash": "b70a3591ff0f4e0313d126c6a1502d79a1c02baebb288227c582044aa76adf6a"
          }
        }
      }
    ]
    
    comments = []
    while True:
      r = self.REQ.post(url = self.API_URL, headers = self.DEFAULT_HEADERS, json = content)
      
      try:
        commentlist = r.json()[0]['data']['video']['comments']['edges']
      except KeyError:
        print("Improper response format.")
        return comments
      
      cursor = None
      for commentdata in commentlist:
        comment = commentdata['node']
        comments.append(comment)
        cursor = commentdata['cursor']
        
      try:
        has_next_page = r.json()[0]['data']['video']['comments']['pageInfo']['hasNextPage']
      except KeyError:
        print("Issue with comment list. Missing pageInfo or hasNextPage.")
        return comments
      
      if has_next_page:
        if "contentOffsetSeconds" in content[0]['variables']:
          content[0]['variables'].pop("contentOffsetSeconds")
        content[0]['variables']['cursor'] = cursor
      else:
        return comments
      
  def get_chat_messages(self, video_id):
    """Get all chat messages and remove duplicates, sort by timestamp

    Args:
        video_id (string): Video ID

    Returns:
        list: List of chat messages
    """
    raw_chat = self.__fetch_all_chat(video_id)
    
    processed_chat = [i for n, i in enumerate(raw_chat) if i not in raw_chat[n + 1:]]
    
    processed_chat.sort(key=lambda a: a['contentOffsetSeconds'])
    return processed_chat
  
  def __get_video_parts_list(self, playlist_url):
    try:
      r = requests.get(playlist_url)
      
      video_chunks : list[str] = str(r.content).split("\\n")
    
      video_list : dict[str, float] = {}
      video_parts : list[str] = []  
    
      for index in range(len(video_chunks)):
        chunk = video_chunks[index]
      
        if chunk.startswith("#EXTINF"):
          nextchunk = video_chunks[index + 1]
          if nextchunk.startswith("#EXT-X-BYTERANGE"):
            nextnextchunk = video_chunks[index + 2]
            if nextnextchunk in video_list.keys():
              video_list[nextnextchunk] += float(chunk[8:-1])
            else:
              video_list[nextnextchunk] = float(chunk[8:-1])
          else:
            video_list[nextchunk] = float(chunk[8:-1])
            
      for video in video_list.keys():
        video_parts.append(video)
        
      return video_parts
    except:
      return []
  
  def download_video(self, video_id : str, filename, quality = "720", saveover = False):
    """Download a Twitch video. Outputs a .ts file that can be converted to your choice of format with ffmpeg.

    Args:
        clip_id (string): Clip ID
        filename (string): Filename
        saveover (bool, optional): Overwrite existing files with the same name. Defaults to False.

    Returns:
        bool: Download succeeded/failed.
    """
    if (not saveover and os.path.exists(filename)):
      print(f"Skipping {video_id} because the filename '{filename}' is taken.")
      return True
    
    playlist_url_bandwidth = self.__get_playlist_url(video_id, quality)
    playlist_url : str = playlist_url_bandwidth["url"]
    
    base_url = playlist_url[:playlist_url.rindex("/") + 1]
    
    video_parts = self.__get_video_parts_list(playlist_url)
  
    with open(filename, "wb") as outfile:
      for part in video_parts:
        full_url = base_url + part
        r = requests.get(full_url)
        outfile.write(r.content)
      outfile.close()