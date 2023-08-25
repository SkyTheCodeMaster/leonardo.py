class LeonardoError(Exception):
  pass

class RequestError(LeonardoError):
  pass

class InvalidInitImageFormat(RequestError):
  pass