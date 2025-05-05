import requests
from ratelimit import limits, sleep_and_retry

class RateLimitedRequests:
  __CALLS_PER_MINUTE = 400
  __PERIOD = 60
  
  def __init__(self, cpm, period):
    self.__CALLS_PER_MINUTE = cpm
    self.__PERIOD = period
  
  @sleep_and_retry
  @limits(calls=__CALLS_PER_MINUTE, period=__PERIOD)
  def get(self, **params : dict) -> requests.Response:
    """Rate limited GET

    Returns:
        requests.Response: GET response
    """
    r = requests.get(**params)
    return r
  
    
  @sleep_and_retry
  @limits(calls=__CALLS_PER_MINUTE, period=__PERIOD)
  def post(self, **params : dict) -> requests.Response:
    """Rate limited POST

    Returns:
        requests.Response: POST response
    """
    r = requests.post(**params)
    return r