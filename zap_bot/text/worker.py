from .messages_builder import MessagesBuilder
from .llm_switcher import LlmSwitcher 
from .llm_requester import LlmRequester
from urllib.request import Request, urlopen
from datetime import datetime
import json

MSGS_LIMIT = 20

def build_prompt(wa_id, wa_name):
  return f"""
  You are a seller who serves customers via whatsapp.

  The products you sell can be retrieved by the get_products function.
  If you need to search for a specific product, you can use the get_products function with
  the name of the product as a parameter. When searching for a single product, use
  the name in singular form.

  You are not allowed to sell any other product.

  The get_products function returns the products informations like the id, the name and prices_per_unit.
  The prices_per_unit indicates the prices per unit a product could be sold. For example, if the prices_per_unit of the product
  "apple" is ["13.99/kg", "9.10/unit"], than the product "apple" could be sold for 13,99 for each kg of "apple" or
  could be sold for 9.10 for each "apple".

  Advise customer if he asks for a product using an unexisting unit for that product.

  Only list the products if the customer asks for it.

  Ask customer his address to complete an order.

  Before and only before complete an order, ask customer if he needs anything else. If not, detail
  the order to the customer and ask him if it is right.

  Each product bought by the customer must be add to customer_products in a unique order.

  After a customer complete his order, save the order informations with the save_order function.

  Your customer name is {wa_name}.
  Your customer phone is {wa_id}.
  The current date and time is {datetime.now()}.
  """
  
def parse_text_message(phone_id, wa_id, wa_name, message_inputs):
  message = '. '.join(message_inputs)
  prompt = build_prompt(wa_id, wa_name)

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
