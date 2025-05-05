class TwitchEvent:
  _TYPE = ''
  _VERSION = 1
  _CONDITION = {}
  _TRANSPORT = {}
  def __init__(self, type, version, condition, transport):
    self._TYPE = type
    self._VERSION = version
    self._CONDITION = condition
    self._TRANSPORT = transport
    
  def notification_type(self):
    return self._TYPE
    
  def params(self):
    return {
      'type': self._TYPE,
      'version': self._VERSION,
      'condition': self._CONDITION,
      'transport': self._TRANSPORT
    }
  
class UpdateEvent(TwitchEvent):
  def __init__(self, user_id, session_id):
    super().__init__(type = 'channel.update', 
                     version =  1, 
                     condition =  { 'broadcaster_user_id': user_id }, 
                     transport =  { 'method': 'websocket', 'session_id': session_id })
    
class FollowEvent(TwitchEvent):
  def __init__(self, user_id, session_id):
    super().__init__(type = 'channel.follow', 
                     version =  2, 
                     condition =  { 'broadcaster_user_id': user_id, 'moderator_user_id': user_id }, 
                     transport =  { 'method': 'websocket', 'session_id': session_id })
    
class SubscribeEvent(TwitchEvent):
  def __init__(self, user_id, session_id):
    super().__init__(type = 'channel.subscribe', 
                     version =  1, 
                     condition =  { 'broadcaster_user_id': user_id }, 
                     transport =  { 'method': 'websocket', 'session_id': session_id })
    
class SubscriptionEndEvent(TwitchEvent):
  def __init__(self, user_id, session_id):
    super().__init__(type = 'channel.subscription.end', 
                     version =  1, 
                     condition =  { 'broadcaster_user_id': user_id }, 
                     transport =  { 'method': 'websocket', 'session_id': session_id })
    
class SubscriptionGiftEvent(TwitchEvent):
  def __init__(self, user_id, session_id):
    super().__init__(type = 'channel.subscription.gift', 
                     version =  1, 
                     condition =  { 'broadcaster_user_id': user_id }, 
                     transport =  { 'method': 'websocket', 'session_id': session_id })
    
class SubscriptionMessageEvent(TwitchEvent):
  def __init__(self, user_id, session_id):
    super().__init__(type = 'channel.subscription.message', 
                     version =  1, 
                     condition =  { 'broadcaster_user_id': user_id }, 
                     transport =  { 'method': 'websocket', 'session_id': session_id })
    
class CheerEvent(TwitchEvent):
  def __init__(self, user_id, session_id):
    super().__init__(type = 'channel.cheer', 
                     version =  1, 
                     condition =  { 'broadcaster_user_id': user_id }, 
                     transport =  { 'method': 'websocket', 'session_id': session_id })
    
class RaidEvent(TwitchEvent):
  def __init__(self, user_id, session_id):
    super().__init__(type = 'channel.raid', 
                     version =  1, 
                     condition =  { 'to_broadcaster_user_id': user_id }, 
                     transport =  { 'method': 'websocket', 'session_id': session_id })
    
class BanEvent(TwitchEvent):
  def __init__(self, user_id, session_id):
    super().__init__(type = 'channel.ban', 
                     version =  1, 
                     condition =  { 'broadcaster_user_id': user_id }, 
                     transport =  { 'method': 'websocket', 'session_id': session_id })
    
class UnbanEvent(TwitchEvent):
  def __init__(self, user_id, session_id):
    super().__init__(type = 'channel.unban', 
                     version =  1, 
                     condition =  { 'broadcaster_user_id': user_id }, 
                     transport =  { 'method': 'websocket', 'session_id': session_id })
    
class ModeratorAddEvent(TwitchEvent):
  def __init__(self, user_id, session_id):
    super().__init__(type = 'channel.moderator.add', 
                     version =  1, 
                     condition =  { 'broadcaster_user_id': user_id }, 
                     transport =  { 'method': 'websocket', 'session_id': session_id })
    
class ModeratorRemoveEvent(TwitchEvent):
  def __init__(self, user_id, session_id):
    super().__init__(type = 'channel.moderator.remove', 
                     version =  1, 
                     condition =  { 'broadcaster_user_id': user_id }, 
                     transport =  { 'method': 'websocket', 'session_id': session_id })
    
class CustomRewardAddEvent(TwitchEvent):
  def __init__(self, user_id, session_id):
    super().__init__(type = 'channel.channel_points_custom_reward.add', 
                     version =  1, 
                     condition =  { 'broadcaster_user_id': user_id }, 
                     transport =  { 'method': 'websocket', 'session_id': session_id })
    
class CustomRewardUpdateEvent(TwitchEvent):
  def __init__(self, user_id, session_id, reward_id = None):
    condition = { 'broadcaster_user_id': user_id } if not reward_id else { 'broadcaster_user_id': user_id, 'reward_id': reward_id }
    super().__init__(type = 'channel.channel_points_custom_reward.update', 
                     version =  1, 
                     condition =  condition, 
                     transport =  { 'method': 'websocket', 'session_id': session_id })
    
class CustomRewardRemoveEvent(TwitchEvent):
  def __init__(self, user_id, session_id, reward_id = None):
    condition = { 'broadcaster_user_id': user_id } if not reward_id else { 'broadcaster_user_id': user_id, 'reward_id': reward_id }
    super().__init__(type = 'channel.channel_points_custom_reward.remove', 
                     version =  1, 
                     condition =  condition, 
                     transport =  { 'method': 'websocket', 'session_id': session_id })
    
class CustomRewardRedemptionAddEvent(TwitchEvent):
  def __init__(self, user_id, session_id, reward_id = None):
    condition = { 'broadcaster_user_id': user_id } if not reward_id else { 'broadcaster_user_id': user_id, 'reward_id': reward_id }
    super().__init__(type = 'channel.channel_points_custom_reward_redemption.add', 
                     version =  1, 
                     condition =  condition, 
                     transport =  { 'method': 'websocket', 'session_id': session_id })
    
class CustomRewardRedemptionUpdateEvent(TwitchEvent):
  def __init__(self, user_id, session_id, reward_id = None):
    condition = { 'broadcaster_user_id': user_id } if not reward_id else { 'broadcaster_user_id': user_id, 'reward_id': reward_id }
    super().__init__(type = 'channel.channel_points_custom_reward_redemption.update', 
                     version =  1, 
                     condition =  condition, 
                     transport =  { 'method': 'websocket', 'session_id': session_id })
    
class StreamOnlineEvent(TwitchEvent):
  def __init__(self, user_id, session_id):
    super().__init__(type = 'stream.online', 
                     version = 1, 
                     condition =  { 'broadcaster_user_id': user_id }, 
                     transport =  { 'method': 'websocket', 'session_id': session_id })
    
class StreamOfflineEvent(TwitchEvent):
  def __init__(self, user_id, session_id):
    super().__init__(type = 'stream.offline', 
                     version =  1, 
                     condition =  { 'broadcaster_user_id': user_id }, 
                     transport =  { 'method': 'websocket', 'session_id': session_id })