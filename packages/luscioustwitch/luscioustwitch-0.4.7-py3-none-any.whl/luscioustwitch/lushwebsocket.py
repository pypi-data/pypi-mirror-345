import websocket
import threading
import time
import json

class TwitchWebSocket:
  WEBSOCKET_URL = "wss://eventsub-beta.wss.twitch.tv/ws"
  SESSION_ID = ""
  
  MSG_CALLBACKS = { }
  CLOSE_CB = lambda wsapp, close_status_code, close_msg: None 
  
  def __init__(self, url_override = None):
    self.MSG_CALLBACKS['default']           = self.default_message_handler
    self.MSG_CALLBACKS['session_welcome']   = self.handle_welcome_message
    self.MSG_CALLBACKS['session_keepalive'] = self.handle_keepalive_message
    self.MSG_CALLBACKS['session_reconnect'] = self.handle_reconnect_message
    self.MSG_CALLBACKS['revocation']        = self.handle_revocation_message
    
    if url_override:
      self.WEBSOCKET_URL = url_override
    
    self.connect()
    
  def add_callback(self, message_type, callback):
    self.MSG_CALLBACKS[message_type] = callback
    
  def connect(self, wait_for_welcome = True):
    self.CONNECTED = False
    self.SESSION_ID = ""
    self.WS = websocket.WebSocketApp(self.WEBSOCKET_URL, on_message = self.on_message, on_close = self.on_close)
    self.THREAD = threading.Thread(target = self.WS.run_forever, daemon = True)
    self.THREAD.start()
    
    time_waiting = 0
    while time_waiting < 10.0 and wait_for_welcome and self.SESSION_ID == "":
      time.sleep(0.1)
      time_waiting += 0.1
      
    if not self.CONNECTED:
      self.WS.close()
      print("Server did not send welcome message. Connection failed.")
    
  def disconnect(self):
    self.WS.close()
    
  def handle_welcome_message(self, wsapp, message):
    print('Handling welcome message.')
    msg_json = json.loads(message)
    try:
      self.SESSION_ID = msg_json['payload']['session']['id']
      self.CONNECTED = True
    except:
      print("Invalid welcome message format.")
      self.CONNECTED = False
      
  def handle_reconnect_message(self, wsapp, message):
    msg_json = json.loads(message)
    
    self.CONNECTED = False
    self.SESSION_ID = ""
    
    new_ws = websocket.WebSocketApp(url = msg_json['payload']['session']['reconnect_url'], on_message = self.on_message, on_close = self.on_close)
    new_thread = threading.Thread(target = new_ws.run_forever, daemon = True)
    new_thread.start()
    
    time_waiting = 0
    while time_waiting < 10.0 and not self.CONNECTED:
      time.sleep(0.1)
      time_waiting += 0.1
      
    if self.CONNECTED:
      self.WS.close()
      self.WS = new_ws
      self.THREAD = new_thread
    else:
      print("Failed to reconnect. Connection lost.")
      new_ws.close()
      self.WS.close()
      
  def handle_revocation_message(self, wsapp, message):
    msg_json = json.loads(message)
    
    status = msg_json['payload']['subscription']['status']
    
    if status == "user_removed":
      print("")
    
  def handle_keepalive_message(self, wsapp, message):
    None
    
  def default_message_handler(self, wsapp, message):
    print("Unhandled message received.")
    print(f"Content: {message}")
    
  def on_message(self, wsapp, message):
    msg_json = json.loads(message)
    message_type = msg_json['metadata']['message_type']
    
    if message_type == 'notification':
      notif_type = msg_json['payload']['subscription']['type']
      if notif_type in self.MSG_CALLBACKS:
        self.MSG_CALLBACKS[notif_type](wsapp, message)
      else:
        self.MSG_CALLBACKS['default'](wsapp, message)
    else:
      if message_type in self.MSG_CALLBACKS:
        self.MSG_CALLBACKS[message_type](wsapp, message)
      else:
        self.MSG_CALLBACKS['default'](wsapp, message)
    
  def on_close(self, wsapp, close_status_code, close_msg):
    print(f'{close_msg} (Status: {close_status_code})')
    self.SESSION_ID = ""
    self.CONNECTED  = False