from .lushrequests import *
from .lushwebsocket import *
from .lushevents import *
from .lushtypes import *

import typing

class TwitchAPI:
  API_URL = "https://api.twitch.tv/helix"
  OAUTH_URL = "https://id.twitch.tv/oauth2"
  AUTHENTICATED = False
  CLIENT_ID = ""
  CLIENT_SECRET = ""
  ACCESS_TOKEN = ""
  REFRESH_TOKEN = ""
  AUTH_TYPE = "client_credentials"
  EXPIRES_IN = -1
  DEFAULT_HEADERS = {}
  rlrequests = RateLimitedRequests(400, 60)
  TWITCH_WEBSOCKET = None
  
  def __add_parameters(self, url : str, params : dict):
    """Add parameters to an API request URL.

    Args:
        url (string): API endpoint
        params (string): Dictionary of parameters. See function descriptions for valid params.

    Returns:
        string: URL with params.
    """
    separator = "?"
    for k, v in params.items():
      url += f"{separator}{k}={v}"
      separator = "&"
    return url
  
  def __raise_req_error(self, response : requests.Response):
    raise Exception(f'Status {response.status_code}: {response.reason}')

  def __init__(self, credentials : dict, override_api_url : str = "", override_oauth_url : str = ""):
    """Constructor for TwitchAPI. Must pass in credentials in the form of a dictionary.

    Args:
        credentials (dict): API Credentials. "CLIENT_ID" and "CLIENT_SECRET" should be in the dict.
    """
    if override_api_url != "":
      self.API_URL = override_api_url
      
    if override_oauth_url != "":
      self.OAUTH_URL = override_oauth_url
    
    self.CLIENT_ID = credentials.get("CLIENT_ID", "")
    self.CLIENT_SECRET = credentials.get("CLIENT_SECRET", "")
    
    if self.CLIENT_ID == "":
      raise Exception("Missing Client ID.")
    
    if 'ACCESS_TOKEN' in credentials:
      self.ACCESS_TOKEN = credentials.get("ACCESS_TOKEN", "")
      self.EXPIRES_IN = credentials.get("EXPIRES_IN", 0)
      self.REFRESH_TOKEN = credentials.get("REFRESH_TOKEN", "")
      self.AUTH_TYPE = credentials.get("AUTH_TYPE", "authorization_code")
    else:
      self.AUTH_TYPE = "client_credentials"
      
      r = requests.post(f'{self.OAUTH_URL}/token?client_id={self.CLIENT_ID}&client_secret={self.CLIENT_SECRET}&grant_type=client_credentials', headers = {'Content-Type': 'application/x-www-form-urlencoded'})
    
      try:
        self.ACCESS_TOKEN = r.json()['access_token']
        self.EXPIRES_IN = r.json()["expires_in"]
      except:
        raise Exception("Failed to create access token. Invalid credentials.")
    
    self.AUTHENTICATED = True
    self.DEFAULT_HEADERS = { "Authorization": f"Bearer {self.ACCESS_TOKEN}", "Client-Id": self.CLIENT_ID }
    
  def refresh_authorization(self) -> bool:
    if self.AUTH_TYPE == "client_credentials":
      return self._refresh_client_credential_authentication()
    else:
      return self.refresh_access_token()
    
  def refresh_access_token(self, refresh_token : str = None) -> bool:
    if refresh_token == None:
      refresh_token = self.REFRESH_TOKEN
    
    url = f'{self.OAUTH_URL}/token'
    post_params = {
      'client_id': self.CLIENT_ID,
      'client_secret': self.CLIENT_SECRET,
      'grant_type': 'refresh_token',
      'refresh_token': refresh_token
    }
    url = self.__add_parameters(url, post_params)
    
    r : requests.Response = self.rlrequests.post(url = url, headers = { 'Content-Type': 'application/x-www-form-urlencoded' })
    
    try:
      self.ACCESS_TOKEN = r.json()['access_token']
      self.REFRESH_TOKEN = r.json()['refresh_token']
    except:
      self.AUTHENTICATED = False
      raise Exception(f"{r.status_code}: {r.content}.\nFailed to refresh access token.")
    
    self.DEFAULT_HEADERS = { "Authorization": f"Bearer {self.ACCESS_TOKEN}", "Client-Id": self.CLIENT_ID }
    self.AUTHENTICATED = True
    
    return self.AUTHENTICATED
  
  def _refresh_client_credential_authentication(self) -> bool:
    r = requests.post(f'{self.OAUTH_URL}/token?client_id={self.CLIENT_ID}&client_secret={self.CLIENT_SECRET}&grant_type=client_credentials', headers = {'Content-Type': 'application/x-www-form-urlencoded'})
  
    try:
      self.ACCESS_TOKEN = r.json()['access_token']
      self.EXPIRES_IN = r.json()["expires_in"]
    except:
      self.AUTHENTICATED = False
      raise Exception("Failed to create access token. Invalid credentials.")
    
    self.DEFAULT_HEADERS = { "Authorization": f"Bearer {self.ACCESS_TOKEN}", "Client-Id": self.CLIENT_ID }
    self.AUTHENTICATED = True
    
    return self.AUTHENTICATED
    

  def get_user_id(self, login : str = "") -> str:
    """Get user ID from username.

    Args:
        username (string): Username

    Returns:
        string: User ID
    """
    twitch_user = self.get_user_by_login(login)
    return twitch_user.user_id
      
  def get_user(self, user_id : str) -> TwitchUser:
    """Get user by user ID

    Args:
        user_id (str): user ID

    Returns:
        dict: user information
    """
    url = f"{self.API_URL}/users?id={user_id}"
    r : requests.Response = self.rlrequests.get(url = url, headers = self.DEFAULT_HEADERS)
    
    if r.status_code == 200:
      response_json : dict = r.json()
      response_data : typing.List[dict] = response_json.get("data", [])
      if len(response_data) > 0:
        return TwitchUser(response_data[0])
      else:
        raise TwitchUser.DoesNotExist(f"User ID \"{user_id}\" was not found.")
    elif r.status_code == 401:
      if self.refresh_authorization():
        return self.get_user(user_id)
      else:
        self.__raise_req_error(r)
    else:
      self.__raise_req_error(r)
      
  def get_user_by_login(self, login : str) -> TwitchUser:
    """Get user ID from login.

    Args:
        login (string): Login

    Returns:
        string: User ID
    """
    url = f"{self.API_URL}/users?login={login}"
    r : requests.Response = self.rlrequests.get(url = url, headers = self.DEFAULT_HEADERS)
    
    if r.status_code == 200:
      response_json : dict = r.json()
      response_data : typing.List[dict] = response_json.get("data", [])
      if len(response_data) > 0:
        return TwitchUser(response_data[0])
      else:
        raise TwitchUser.DoesNotExist(f"User login \"{login}\" was not found.")
    elif r.status_code == 401:
      if self.refresh_authorization():
        return self.get_user_by_login(login)
      else:
        self.__raise_req_error(r)
    else:
      self.__raise_req_error(r)
  
  def get_channel_info(self, broadcaster_id : str) -> TwitchChannelInfo:
    """Get Channel Information.

    Args:
        user_id (string): User ID

    Returns:
        dict: Channel information
    """
    url = f"{self.API_URL}/channels?broadcaster_id={broadcaster_id}"
    r : requests.Response = self.rlrequests.get(url = url, headers = self.DEFAULT_HEADERS)
    
    if r.status_code == 200:
      response_json : dict = r.json()
      response_data : typing.List[dict] = response_json.get("data", [])
      if len(response_data) > 0:
        return TwitchChannelInfo(response_data[0])
      else:
        raise TwitchChannelInfo.DoesNotExist(f"Broadcaster ID \"{broadcaster_id}\" was not found.")
    elif r.status_code == 401:
      if self.refresh_authorization():
        return self.get_channel_info(broadcaster_id)
      else:
        self.__raise_req_error(r)
    else:
      self.__raise_req_error(r)
      
  def get_category_by_id(self, category_id : str) -> TwitchCategoryInfo:
    """Get category information from category name

    Args:
        category_id (str): Category ID

    Returns:
        dict: Category information
    """
    url = f"{self.API_URL}/games?id={category_id}"
    r : requests.Response = self.rlrequests.get(url = url, headers = self.DEFAULT_HEADERS)
    
    if r.status_code == 200:
      response_json : dict = r.json()
      response_data : typing.List[dict] = response_json.get("data", [])
      if len(response_data) > 0:
        return TwitchCategoryInfo(response_data[0])
      else:
        raise TwitchCategoryInfo.DoesNotExist(f"Category ID \"{category_id}\" was not found.")
    elif r.status_code == 401:
      if self.refresh_authorization():
        return self.get_category_by_id(category_id)
      else:
        self.__raise_req_error(r)
    else:
      self.__raise_req_error(r)
      
  def get_category_by_name(self, category_name : str) -> TwitchCategoryInfo:
    """Get category information from category name

    Args:
        category_id (str): Category ID

    Returns:
        dict: Category information
    """
    url = f"{self.API_URL}/games?name={category_name}"  
    r : requests.Response = self.rlrequests.get(url = url, headers = self.DEFAULT_HEADERS)
    
    if r.status_code == 200:
      response_json : dict = r.json()
      response_data : typing.List[dict] = response_json.get("data", [])
      if len(response_data) > 0:
        return TwitchCategoryInfo(response_data[0])
      else:
        raise TwitchCategoryInfo.DoesNotExist(f"Category \"{category_name}\" was not found.")
    elif r.status_code == 401:
      if self.refresh_authorization():
        return self.get_category_by_name(category_name)
      else:
        self.__raise_req_error(r)
    else:
      self.__raise_req_error(r)
      
  def get_category_id(self, category_name : str) -> str:
    """Get category ID

    Args:
        category_name (str): _description_

    Returns:
        str: _description_
    """
    return self.get_category_by_name(category_name).category_id

  def get_clip(self, clip_id : str) -> TwitchClip:
    """Get info for one clip from ID.

    Args:
        clip_id (string): Video ID

    Returns:
        dict: clip info
    """
    url = f"{self.API_URL}/clips?id={clip_id}"
    r: requests.Response = self.rlrequests.get(url = url, headers = self.DEFAULT_HEADERS)
    
    if r.status_code == 200:
      response_json : dict = r.json()
      response_data : typing.List[dict] = response_json.get("data", [])
      if len(response_data) > 0:
        return TwitchClip(response_data[0])
      else:
        raise TwitchClip.DoesNotExist(f"Clip ID \"{clip_id}\" was not found.")
    elif r.status_code == 401:
      if self.refresh_authorization():
        return self.get_clip(clip_id)
      else:
        self.__raise_req_error(r)
    else:
      self.__raise_req_error(r)
      
  def create_clip(self, broadcaster_id : str, has_delay : bool = False) -> dict:
    """Create a clip of a broadcast.

    Args:
        broadcaster_id (str): Broadcaster ID
        has_delay (bool, optional): Add delay to clip. Defaults to False.

    Returns:
        dict: Dictionary containing id and edit_url
    """
    url = f'{self.API_URL}/clips'
    url = self.__add_parameters(url, { 'broadcaster_id': broadcaster_id, 'has_delay': 'true' if has_delay else 'false'})
    
    r: requests.Response = self.rlrequests.post(url = url, headers = self.DEFAULT_HEADERS)
    
    if r.status_code == 202:
      response_json : dict = r.json()
      response_data : typing.List[dict] = response_json.get("data", [])
      if len(response_data) > 0:
        return CreateClipResponse(response_data[0])
      else:
        raise CreateClipResponse.DoesNotExist("Create clip failed.")
    elif r.status_code == 401:
      if self.refresh_authorization():
        return self.create_clip(broadcaster_id, has_delay)
      else:
        self.__raise_req_error(r)
    else:
      self.__raise_req_error(r)

  def get_clips(self, params : dict) -> typing.List[TwitchClip]:
    """Get clips based on params.

    Args:
        params (dict): Dictionary of parameters for the API request. The valid params are:
            id (string): Clip ID
            broadcaster_id (string): Broadcaster ID
            game_id (string): Game/Category ID
            started_at (string): RFC3339 format, use TWITCH_API_TIME_FORMAT from this library
            ended_at (string): RFC3339 format, use TWITCH_API_TIME_FORMAT from this library
            first (int): fetch the first n clips
            before (string): reverse pagination
            after (string): forward pagination

    Returns:
        list: list of clip info
    """
    url = f"{self.API_URL}/clips"
    url = self.__add_parameters(url, params)
    
    r : requests.Response = self.rlrequests.get(url = url, headers=self.DEFAULT_HEADERS)
    
    if r.status_code == 200:
      response_json : dict = r.json()
      response_data : typing.List[dict] = response_json.get("data", [])
      response_pagination : dict = response_json.get("pagination", {})
      
      video_list = [TwitchClip(data) for data in response_data]
      cursor = response_pagination['cursor'] if "cursor" in response_pagination else ""
      
      return video_list, cursor
    elif r.status_code == 401:
      if self.refresh_authorization():
        return self.get_clips(params)
      else:
        self.__raise_req_error(r)
    else:
      self.__raise_req_error(r)

  def get_all_clips(self, params : dict) -> typing.List[TwitchClip]:
    """Get all clips based on params (auto-pagination).

    Args:
        params (dict): Dictionary of parameters for the API request. The valid params are:
            id (string): Clip ID
            broadcaster_id (string): Broadcaster ID
            game_id (string): Game/Category ID
            started_at (string): RFC3339 format, use TWITCH_API_TIME_FORMAT from this library
            ended_at (string): RFC3339 format, use TWITCH_API_TIME_FORMAT from this library
            first (int): fetch the first n clips
            before (string): reverse pagination
            after (string): forward pagination

    Returns:
        list: list of clip info
    """
    all_clips = []
    while True:
      clips, cursor = self.get_clips(params)

      for clip in clips:
        all_clips.append(clip)
      
      if cursor == "":
        return all_clips
      else:
        params["after"] = cursor

  def get_video(self, video_id : typing.Union[str, int]) -> TwitchVideo:
    """Get info for one video from ID.

    Args:
        video_id (string|int): Video ID

    Returns:
        dict: Video info
    """
    url = f"{self.API_URL}/videos?id={video_id}"
    r : requests.Response = self.rlrequests.get(url = url, headers = self.DEFAULT_HEADERS)
    
    if r.status_code == 200:
      response_json : dict = r.json()
      response_data : typing.List[dict] = response_json.get("data", [])
      if len(response_data) > 0:
        return TwitchVideo(response_data[0])
      else:
        raise TwitchVideo.DoesNotExist(f"Video ID \"{video_id}\" returned no results.")
    elif r.status_code == 401:
      if self.refresh_authorization():
        return self.get_video(video_id)
      else:
        self.__raise_req_error(r)
    else:
      self.__raise_req_error(r)

  def get_videos(self, params : dict) -> typing.Tuple[typing.List[TwitchVideo], str]:
    """Get videos based on params.

    Args:
        params (dict): Dictionary of parameters for the API request. The valid params are:
            id (string): Video ID
            user_id (string): User ID
            game_id (string): Game/Category ID
            language (string): ISO 639-1
            period (string): "all", "day", "month", or "week"
            sort (string): "time", "trending", or "views"
            type (string): "all", "archive", "highlight", or "upload"
            first (int): fetch the first n videos
            before (string): reverse pagination
            after (string): forward pagination

    Returns:
        list: list of video info
        string: Pagination cursor
    """
    url = f"{self.API_URL}/videos"
    url = self.__add_parameters(url, params)
    
    r : requests.Response = self.rlrequests.get(url = url, headers = self.DEFAULT_HEADERS)
    
    if r.status_code == 200:
      response_json : dict = r.json()
      response_data : typing.List[dict] = response_json.get("data", [])
      response_pagination : dict = response_json.get("pagination", {})
      
      video_list = [TwitchVideo(data) for data in response_data]
      cursor = response_pagination['cursor'] if "cursor" in response_pagination else ""
      
      return video_list, cursor
    elif r.status_code == 401:
      if self.refresh_authorization():
        return self.get_videos(params)
      else:
        self.__raise_req_error(r)
    else:
      self.__raise_req_error(r)

  def get_all_videos(self, params : dict) -> typing.List[TwitchVideo]:
    """Get all videos based on params (auto-pagination).

    Args:
        params (dict): Dictionary of parameters for the API request. The valid params are:
            id (string): Video ID
            user_id (string): User ID
            game_id (string): Game/Category ID
            language (string): ISO 639-1
            period (string): "all", "day", "month", or "week"
            sort (string): "time", "trending", or "views"
            type (string): "all", "archive", "highlight", or "upload"
            first (int): fetch the first n videos
            before (string): reverse pagination
            after (string): forward pagination

    Returns:
        list: list of videos
    """
    all_videos = []
    while True:
      vids, cursor = self.get_videos(params)

      for vod in vids:
        all_videos.append(vod)
      
      if cursor == "":
        return all_videos
      else:
        params["after"] = cursor

  def get_streams(self, params : dict) -> typing.Tuple[typing.List[TwitchStream], str]:
    """Get a list of streams.

    Args:
        params (dict): Dictionary of parameters for the API request. The valid params are:
            user_id (string): User ID
            user_login (string): Username
            game_id (string): Game/Category ID
            type (string): "all" or "live"
            language (string): ISO 639-1
            first (int): fetch the first n streams
            before (string): reverse pagination
            after (string): forward pagination

    Returns:
        list: list of stream info
        str: Pagination cursor
    """
    url = f"{self.API_URL}/streams/"
    url = self.__add_parameters(url, params)
    
    r : requests.Response = self.rlrequests.get(url = url, headers = self.DEFAULT_HEADERS)
    
    if r.status_code == 200:
      response_json : dict = r.json()
      response_data : typing.List[dict] = response_json.get("data", [])
      response_pagination : dict = response_json.get("pagination", {})
      
      stream_list = [TwitchStream(data) for data in response_data]
      cursor = response_pagination['cursor'] if "cursor" in response_pagination else ""
      
      return stream_list, cursor
    elif r.status_code == 401:
      if self.refresh_authorization():
        return self.get_streams(params)
      else:
        self.__raise_req_error(r)
    else:
      self.__raise_req_error(r)
      
  def get_all_streams(self, params : dict) -> typing.List[TwitchStream]:
    """Get a list of streams.

    Args:
        params (dict): Dictionary of parameters for the API request. The valid params are:
            user_id (string): User ID
            user_login (string): Username
            game_id (string): Game/Category ID
            type (string): "all" or "live"
            language (string): ISO 639-1
            first (int): fetch the first n streams
            before (string): reverse pagination
            after (string): forward pagination

    Returns:
        list: list of stream info
    """
    all_streams = []
    while True:
      streams, cursor = self.get_streams(params)

      for s in streams:
        all_streams.append(s)
      
      if cursor == "":
        return all_streams
      else:
        params["after"] = cursor

  def is_user_live(self, user_id : str) -> bool:
    stream_info = self.get_all_streams({ "user_id": user_id })
    return (len(stream_info) > 0)
  
  def get_channel_emotes(self, broadcaster_id : str) -> typing.Tuple[typing.List[TwitchChannelEmote], str]:
    """Get Channel Emotes

    Args:
        broadcaster_id (string): User ID

    Returns:
        list: List of channel emotes.
        str: Template
    """
    url = f"{self.API_URL}/chat/emotes?broadcaster_id={broadcaster_id}"
    r : requests.Response = self.rlrequests.get(url = url, headers = self.DEFAULT_HEADERS)
    
    if r.status_code == 200:
      response_json : dict = r.json()
      response_data : typing.List[dict] = response_json.get("data", [])
      
      emote_list = [TwitchChannelEmote(data) for data in response_data]
      template : str = response_json.get("template", "")
      
      return emote_list, template
    elif r.status_code == 401:
      if self.refresh_authorization():
        return self.get_channel_emotes(broadcaster_id)
      else:
        self.__raise_req_error(r)
    else:
      self.__raise_req_error(r)
  
  def get_global_emotes(self) -> typing.Tuple[typing.List[TwitchEmote], str]:
    """Get Global Emotes.

    Returns:
        list: List of global emote information.
    """
    url = f"{self.API_URL}/chat/emotes/global"
    r : requests.Response = self.rlrequests.get(url = url, headers = self.DEFAULT_HEADERS)
    
    if r.status_code == 200:
      response_json : dict = r.json()
      response_data : typing.List[dict] = response_json.get("data", [])
      
      emote_list = [TwitchEmote(data) for data in response_data]
      template : str = response_json.get("template", "")
      
      return emote_list, template
    elif r.status_code == 401:
      if self.refresh_authorization():
        return self.get_global_emotes()
      else:
        self.__raise_req_error(r)
    else:
      self.__raise_req_error(r)
    
  def get_custom_rewards(self, params : dict) -> list:
    """Get a list of custom rewards for a channel.

    Args:
        params (dict): dictionary of parameters for the request
          broadcaster_id (int): The ID of the broadcaster whose custom rewards you want to get
          id (string): Rewards ID
          only_manageable_rewards (bool): only get custom rewards that the app may manage

    Returns:
        _type_: _description_
    """
    url = f"{self.API_URL}/channel_points/custom_rewards"
    url = self.__add_parameters(url, params)
    
    r : requests.Response = self.rlrequests.get(url = url, headers = self.DEFAULT_HEADERS)
    
    if r.status_code == 200:
      return r.json()['data']
    elif r.status_code == 401:
      if self.refresh_authorization():
        return self.get_custom_rewards(params)
      else:
        self.__raise_req_error(r)
    else:
      self.__raise_req_error(r)
    
  def create_custom_reward(self, broadcaster_id : str, reward_params : dict) -> dict:
    url = f"{self.API_URL}/channel_points/custom_rewards?broadcaster_id={broadcaster_id}"
    
    r : requests.Response = self.rlrequests.post(url = url, headers = self.DEFAULT_HEADERS, json = reward_params)
    
    if r.status_code == 200:
      return r.json()['data'][0]
    elif r.status_code == 401:
      if self.refresh_authorization():
        return self.create_custom_reward(broadcaster_id, reward_params)
      else:
        self.__raise_req_error(r)
    else:
      self.__raise_req_error(r)
    
  def setup_websocket(self, url_override = None):
    """Connect to the Twitch WebSockets interface for subscribing to events.

    Args:
        url_override (str, optional): Pass a different websockets url for testing purposes. Defaults to None.
    """
    self.TWITCH_WEBSOCKET = TwitchWebSocket(url_override)
    
  def websocket_session_id(self) -> str:
    return self.TWITCH_WEBSOCKET.SESSION_ID
    
  def join_websocket_thread(self):
    self.TWITCH_WEBSOCKET.THREAD.join()
    
  def _add_subscription(self, params : dict) -> bool:
    if not self.TWITCH_WEBSOCKET.CONNECTED:
      print("WebSocket is not connected.")
      return False
    
    url = f'{self.API_URL}/eventsub/subscriptions'
    
    r : requests.Response = self.rlrequests.post(url = url, headers = self.DEFAULT_HEADERS, json=params)
    
    if r.status_code == 202:
      return r.json()['data'][0]['status'] == 'enabled'
    elif r.status_code == 401:
      if self.refresh_authorization():
        return self._add_subscription(params)
      else:
        self.__raise_req_error(r)
    else:
      return False
    
  def get_active_subscriptions(self) -> list:
    """Get active subscriptions in current WebSocket instance.

    Returns:
        list: list of active subscriptions
    """
    url = f'{self.API_URL}/eventsub/subscriptions'
    r : requests.Response = self.rlrequests.get(url = url, headers = self.DEFAULT_HEADERS)
    
    if r.status_code == 200:
      return r.json()['data']
    elif r.status_code == 401:
      if self.refresh_authorization():
        return self.get_active_subscriptions()
      else:
        self.__raise_req_error(r)
    else:
      self.__raise_req_error(r)
    
  def add_subscription(self, event : TwitchEvent, callback) -> bool:
    """Add a subscription to the WebSocket interface.

    Args:
        event (TwitchEvent): Desired subscription event type
        callback (function): Callback for handling notifications matching this subscription

    Returns:
        bool: Success.
    """
    self.TWITCH_WEBSOCKET.add_callback(event.notification_type(), callback)
    return self._add_subscription(event.params())
  
  def subscribe_to_updates(self, user_id : str, callback : typing.Callable[[object, str], None]) -> bool:
    return self.add_subscription(UpdateEvent(user_id, self.websocket_session_id()), callback)
    
  def subscribe_to_follows(self, user_id : str, callback : typing.Callable[[object, str], None]) -> bool:
    return self.add_subscription(FollowEvent(user_id, self.websocket_session_id()), callback)
    
  def subscribe_to_subscriptions(self, user_id : str, callback : typing.Callable[[object, str], None]) -> bool:
    return self.add_subscription(SubscribeEvent(user_id, self.websocket_session_id()), callback)
    
  def subscribe_to_gifted_subscriptions(self, user_id : str, callback : typing.Callable[[object, str], None]) -> bool:
    return self.add_subscription(SubscriptionGiftEvent(user_id, self.websocket_session_id()), callback)
    
  def subscribe_to_subscription_messages(self, user_id : str, callback : typing.Callable[[object, str], None]) -> bool:
    return self.add_subscription(SubscriptionMessageEvent(user_id, self.websocket_session_id()), callback)
  
  def subscribe_to_cheers(self, user_id : str, callback : typing.Callable[[object, str], None]) -> bool:
    return self.add_subscription(CheerEvent(user_id, self.websocket_session_id()), callback)
  
  def subscribe_to_raids(self, user_id : str, callback : typing.Callable[[object, str], None]) -> bool:
    return self.add_subscription(RaidEvent(user_id, self.websocket_session_id()), callback)
  
  def subscribe_to_bans(self, user_id : str, callback : typing.Callable[[object, str], None]) -> bool:
    return self.add_subscription(BanEvent(user_id, self.websocket_session_id()), callback)
  
  def subscribe_to_unbans(self, user_id : str, callback : typing.Callable[[object, str], None]) -> bool:
    return self.add_subscription(UnbanEvent(user_id, self.websocket_session_id()), callback)
  
  def subscribe_to_reward_redemption(self, user_id : str, callback : typing.Callable[[object, str], None], reward_id : str = None) -> bool:
    return self.add_subscription(CustomRewardRedemptionAddEvent(user_id, self.websocket_session_id(), reward_id), callback)
    
  def subscribe_to_stream_online(self, user_id : str, callback : typing.Callable[[object, str], None]) -> bool:
    return self.add_subscription(StreamOnlineEvent(user_id, self.websocket_session_id()), callback)
    
  def subscribe_to_stream_offline(self, user_id : str, callback : typing.Callable[[object, str], None]) -> bool:
    return self.add_subscription(StreamOfflineEvent(user_id, self.websocket_session_id()), callback)