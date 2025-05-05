import typing
import datetime
import json

TWITCH_API_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

def str_to_datetime(value : str) -> datetime.datetime:
  try:
    return datetime.datetime.strptime(value, TWITCH_API_TIME_FORMAT).replace(tzinfo=datetime.timezone.utc)
  except:
    return None

class LusciousBaseObject:
  class DoesNotExist(Exception):
    def __init__(self, message : str):
      super().__init__(message)
  
  class InvalidFormat(KeyError):
    def __init__(self, message : str):
      super().__init__(message)
      
  @property
  def attributes(self) -> typing.List[str]:
    return []
  
  @property
  def optional_attributes(self) -> typing.List[str]:
    return []
  
  def parse_attribute(self, key : str, value : object) -> bool:
    setattr(self, key, value)
    return True
    
  def __init__(self, object_data : dict):
    missing_keys = []
    invalid_keys = []
    
    for key in self.attributes:
      if key not in object_data:
        missing_keys.append(key)
        continue
      
      success = self.parse_attribute(key, object_data.get(key, None))
      
      if not success:
        invalid_keys.append(key)
        continue
    
    for key in self.optional_attributes:
      self.parse_attribute(key, object_data.get(key, None))
        
    if len(missing_keys) > 0:
      raise LusciousBaseObject.InvalidFormat(f"{type(self).__name__} JSON data is missing keys: {', '.join(missing_keys)}")
    
    if len(invalid_keys) > 0:
      raise LusciousBaseObject.InvalidFormat(f"{type(self).__name__} JSON data has invalid values for keys: {', '.join(invalid_keys)}")

class TwitchClip(LusciousBaseObject):
  clip_id : str = None
  url : str = None
  embed_url : str = None
  broadcaster_id : str = None
  broadcaster_name : str = None
  creator_id : str = None
  creator_name : str = None
  video_id : str = None
  game_id : str = None
  language : str = None
  title : str = None
  view_count : int = None
  created_at : datetime.datetime = None
  thumbnail_url : str = None
  duration : float = None
  vod_offset : int = None
  is_featured : bool = None
  
  def __str__(self) -> str:
    return f"{self.title} ({self.clip_id})"
      
  @property
  def attributes(self) -> typing.List[str]:
    return [
      "id",
      "url",
      "embed_url",
      "broadcaster_id",
      "broadcaster_name",
      "creator_id",
      "creator_name",
      "video_id",
      "game_id",
      "language",
      "title",
      "view_count",
      "created_at",
      "thumbnail_url",
      "duration",
      "vod_offset",
      "is_featured",
    ]
  
  def parse_attribute(self, key : str, value : object) -> bool:
    if key == "id":
      setattr(self, "clip_id", value)
    elif key == "created_at":
      try:
        setattr(self, key, datetime.datetime.strptime(value, TWITCH_API_TIME_FORMAT))
      except:
        return False
    else:
      setattr(self, key, value)
      
    return True
  
class GQL_PlaybackAccessToken(LusciousBaseObject):
  signature : str = None
  value : dict = None
  value_raw : str = None
  
  @property
  def attributes(self) -> typing.List[str]:
    return [
      "signature",
      "value",
    ]
    
  def parse_attribute(self, key : str, value : object):
    if key == "value":
      setattr(self, 'value_raw', value)
      setattr(self, key, json.loads(value))
    else:
      setattr(self, key, value)
    return True
    
class GQL_VideoQuality(LusciousBaseObject):
  frameRate : float = -1.0
  quality : str = None
  sourceURL : str = None
    
  def __str__(self):
    return f"{self.quality} @ {self.frameRate:.2f}Hz: {self.sourceURL}"
  
  @property
  def attributes(self) -> typing.List[str]:
    return [
      "frameRate",
      "quality",
      "sourceURL",
    ]
  
class GQL_Clip(LusciousBaseObject):
  clipId : str = None
  playbackAccessToken : GQL_PlaybackAccessToken = None
  videoQualities : typing.List[GQL_VideoQuality] = []
  
  @property
  def attributes(self) -> typing.List[str]:
    return [
      "id",
      "playbackAccessToken",
      "videoQualities",
    ]
    
  def parse_attribute(self, key : str, value : object) -> bool:
    if key == "id":
      setattr(self, "clipId", value)
    elif key == "playbackAccessToken":
      setattr(self, key, GQL_PlaybackAccessToken(value))
    elif key == "videoQualities":
      setattr(self, key, [GQL_VideoQuality(vq) for vq in value])
    else:
      setattr(self, key, value)
    return True

class GQL_Video(LusciousBaseObject):
  videoId : str = None
  title : str = None
  thumbnailURLs : typing.List[str] = []
  createdAt : datetime.datetime = None
  publishedAt : datetime.datetime = None
  lengthSeconds : int = -1
  owner : typing.Dict[str, str] = {}
  extensions : typing.Dict[str, typing.Union[str, int]] = {}
  
  @property
  def attributes(self) -> typing.List[str]:
    return [
      "id",
      "title",
      "thumbnailURLs",
      "createdAt",
      "publishedAt",
      "lengthSeconds",
      "owner",
    ]
    
  @property
  def optional_attributes(self) -> typing.List[str]:
    return [ "extensions" ]
    
  def parse_attribute(self, key : str, value : object) -> bool:
    if key == "id":
      setattr(self, "videoId", value)
    elif key == "createdAt" or key == "publishedAt":
      dt = str_to_datetime(value)
      setattr(self, key, dt)
      if dt is None:
        return False
    else:
      setattr(self, key, value)
      
    return True
      

class CreateClipResponse(LusciousBaseObject):
  edit_url : str = None
  clip_id : str = None
  
  @property
  def attributes(self) -> typing.List[str]:
    return [
      "edit_url",
      "id",
    ]
    
  def parse_attribute(self, key : str, value : object) -> bool:
    if key == "id":
      setattr(self, "clip_id", value)
    else:
      setattr(self, key, value)
      
    return True
    
class TwitchVideo(LusciousBaseObject):
  video_id : str = None
  stream_id : str = None
  user_id : str = None
  user_login : str = None
  user_name : str = None
  title : str = None
  description : str = None
  created_at : datetime.datetime = None
  published_at : datetime.datetime = None
  url : str = None
  thumbnail_url : str = None
  viewable : bool = None
  view_count : int = None
  language : str = None
  type : str = None
  duration : str = None
  muted_segments : typing.Optional[typing.List[typing.Dict[str, int]]] = None
  
  def __str__(self) -> str:
    return f"{self.title} ({self.video_id})"
      
  @property
  def attributes(self) -> typing.List[str]:
    return [
      "id",
      "stream_id",
      "user_id",
      "user_login",
      "user_name",
      "title",
      "description",
      "created_at",
      "published_at",
      "url",
      "thumbnail_url",
      "viewable",
      "view_count",
      "language",
      "type",
      "duration",
      "muted_segments"
    ]
  
  def parse_attribute(self, key : str, value : object) -> bool:
    if key == "id":
      setattr(self, "video_id", value)
    elif key == "created_at" or key == "published_at":
      dt = str_to_datetime(value)
      setattr(self, key, dt)
      if dt is None:
        return False
    else:
      setattr(self, key, value)
      
    return True

class TwitchStream(LusciousBaseObject):
  stream_id : str = None
  user_id : str = None
  user_login : str = None
  user_name : str = None
  game_id : str = None
  game_name : str = None
  type : str = None
  title : str = None
  tags : typing.List[str] = []
  viewer_count : int = -1
  started_at : datetime.datetime = None
  language : str = None
  thumbnail_url : str = None
  tag_ids : typing.List[str] = []
  is_mature : bool = False
  
  def __str__(self) -> str:
    return f"{self.title} ({self.stream_id})"
  
  @property
  def attributes(self) -> typing.List[str]:
    return [
      "id",
      "user_id",
      "user_login",
      "user_name",
      "game_id",
      "game_name",
      "type",
      "title",
      "tags",
      "viewer_count",
      "started_at",
      "language",
      "thumbnail_url",
      "is_mature",
    ]
    
  @property
  def optional_attributes(self) -> typing.List[str]:
    return [ "tag_ids" ]
    
  def parse_attribute(self, key, value):
    if key == "id":
      setattr(self, "stream_id", value)
    elif key == "started_at":
      dt = str_to_datetime(value)
      setattr(self, key, dt)
      if dt is None:
        return False
    else:
      setattr(self, key, value)
      
    return True
      
class TwitchUser(LusciousBaseObject):
  user_id : str = None
  login : str = None
  display_name = None
  user_type : str = None
  broadcaster_type : str = None
  description : str = None
  profile_image_url : str = None
  offline_image_url : str = None
  view_count : int = None
  email : str = None
  created_at : datetime.datetime = None
  
  def __str__(self) -> str:
    return f"{self.display_name}/{self.login} ({self.user_id})"
  
  @property
  def attributes(self) -> typing.List[str]:
    return [
      "id",
      "login",
      "display_name",
      "type",
      "broadcaster_type",
      "description",
      "profile_image_url",
      "offline_image_url",
      "created_at",
    ]
    
  @property
  def optional_attributes(self) -> typing.List[str]:
    return [
      "view_count",
      "email",
    ]
    
  def parse_attribute(self, key, value):
    if key == "id":
      setattr(self, "user_id", value)
    elif key == "created_at":
      dt = str_to_datetime(value)
      setattr(self, key, dt)
      if dt is None:
        return False
    else:
      setattr(self, key, value)
      
    return True
  
class TwitchChannelInfo(LusciousBaseObject):
  broadcaster_id : str = None
  broadcaster_login : str = None
  broadcaster_name : str = None
  broadcaster_language : str = None
  game_name : str = None
  game_id : str = None
  title : str = None
  delay : int = None
  tags : typing.List[str] = None
  content_classification_labels : typing.List[str] = None
  is_branded_content : bool = False
  
  def __str__(self) -> str:
    return f"{self.title} - {self.broadcaster_name}"
  
  @property
  def attributes(self) -> typing.List[str]:
    return [
      "broadcaster_id",
      "broadcaster_login",
      "broadcaster_name",
      "broadcaster_language",
      "game_name",
      "game_id",
      "title",
      "delay",
      "tags",
      "content_classification_labels",
      "is_branded_content",
    ]
    
class TwitchCategoryInfo(LusciousBaseObject):
  category_id : str = None
  name : str = None
  box_art_url = None
  igdb_id = None
  
  def __str__(self) -> str:
    return f"{self.name} ({self.category_id})"
  
  @property
  def attributes(self) -> typing.List[str]:
    return [
      "id",
      "name",
      "box_art_url",
      "igdb_id",
    ]
    
  def parse_attribute(self, key, value):
    if key == "id":
      setattr(self, "category_id", value)
    else:
      setattr(self, key, value)
      
    return True
  
class TwitchEmote(LusciousBaseObject):
  emote_id : str = None
  name : str = None
  images : typing.Dict[str, str] = {}
  format : typing.List[str] = []
  scale : typing.List[str] = []
  theme_mode : typing.List[str] = []
  
  def __str__(self):
    return self.name
  
  @property
  def attributes(self) -> typing.List[str]:
    return [
      "id",
      "name",
      "images",
      "format",
      "scale",
      "theme_mode",
    ]
    
  def parse_attribute(self, key, value):
    if key == "id":
      setattr(self, "emote_id", value)
    else:
      setattr(self, key, value)
      
    return True
    
class TwitchChannelEmote(TwitchEmote):
  tier : str = None
  emote_type : str = None
  emote_set_id : str = None
  
  @property
  def attributes(self) -> typing.List[str]:
    attr_list = []
    attr_list.extend(super().attributes)
    attr_list.extend([
      "tier",
      "emote_type",
      "emote_set_id",
    ])
    return attr_list