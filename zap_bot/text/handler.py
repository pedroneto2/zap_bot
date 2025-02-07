from app import redis
from threading import Timer
from .worker import parse_text_message

def handle_text_requests(wa_id, wa_name, message):
  message_inputs = redis.lrange(wa_id, 0, -1)
  message_inputs_length = len(message_inputs)
  if message_inputs_length < 7:
    redis.lpush(wa_id, message)
    if not message_inputs_length:
      work = Timer(5, work_function, args = [wa_id, wa_name])
      work.start()

def work_function(wa_id, wa_name, len = 1):
  message_inputs_length = redis.llen(wa_id)
  if len >= message_inputs_length:
    message_inputs = redis.lrange(wa_id, 0, -1)
    redis.delete(wa_id)
    parse_text_message(wa_id, wa_name, message_inputs)
  else:
    work = Timer(5, work_function, args = [wa_id, wa_name, message_inputs_length])
    work.start()