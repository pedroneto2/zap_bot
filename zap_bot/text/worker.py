from .messages_builder import MessagesBuilder
from .llm_requester import LlmRequester
from urllib.request import Request, urlopen
import json

MSGS_LIMIT = 20

def build_prompt(wa_name):
  return f'Você é um assistente prestativo, porém só responde na lingua dos gatos. O nome do seu cliente é {wa_name}.'
  
def parse_text_message(phone_id, wa_id, wa_name, message_inputs):
  message = '. '.join(message_inputs)
  prompt = build_prompt(wa_name)

  messages = MessagesBuilder(wa_id, prompt, message, MSGS_LIMIT).build()

  llm_requester = LlmRequester(messages)
  llm_requester.send()
  llm_requester.persist_response_to_db(wa_id)

  response_message = llm_requester.response_message

  # remove this and adds to env
  auth_token = 'EAAoB3OkSZATwBO5ZCu2fVCVSEHdODsZBZAdlfh97Ag8lWWl6wwjxWc7B5xXfZAf1PwDZArkQfdTivwv3nbkrvuheNjGj9DZBIvdpveno5A9JkPUZB6BBZB6vwETbwrIDrYfD5kttISkXrAQYKXLEmnx2JsBX2dZBpr96yFZCphiKg3pTZCceLiHEZAwhyGMH1jb6Nv0LWrLQ00Rx5fPP8EZByxp0xE4WerDPwZD'

  headers = { 
    'Authorization': 'Bearer ' + auth_token,
    'Content-Type': 'application/json'
  }

  zap_url = f'https://graph.facebook.com/v21.0/{phone_id}/messages'

  body = {
    "messaging_product": "whatsapp",    
    "recipient_type": "individual",
    "to": wa_id,
    "type": "text",
    "text": {
      "preview_url": False,
      "body": response_message
    }
  }

  encoded_body = json.dumps(body).encode("utf-8")

  request = Request(zap_url, data = encoded_body, headers = headers)

  urlopen(request)
