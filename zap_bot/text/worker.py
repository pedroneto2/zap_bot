from .messages_builder import MessagesBuilder
from .llm_switcher import LlmSwitcher 
from .llm_requester import LlmRequester
from urllib.request import Request, urlopen
import json

MSGS_LIMIT = 20

def build_prompt(wa_name):
  return f"""
  You are a seller who serves customers via whatsapp.

  The products you sell can be retrieved by the get_products function.
  You are not allowed to sell any other product.

  If you need to search for a specif product, you can use the get_products function with
  the name of the product as a parameter.

  Only list the products if the customer ask for it.

  O nome do seu cliente é {wa_name}.
  """
  
def parse_text_message(phone_id, wa_id, wa_name, message_inputs):
  message = '. '.join(message_inputs)
  prompt = build_prompt(wa_name)

  llm_client_info = LlmSwitcher().get_client_info()

  messages = MessagesBuilder(wa_id, prompt, message, MSGS_LIMIT).build()

  llm_requester = LlmRequester(llm_client_info, wa_id, messages)
  response_message = llm_requester.send()

  return

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
