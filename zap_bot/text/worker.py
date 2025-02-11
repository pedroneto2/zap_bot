from .messages_builder import MessagesBuilder
from .llm_requester import LlmRequester
from sqlite3.dbapi2 import connect

MSGS_LIMIT = 20

def build_prompt(wa_name):
  return f'Você é um assistente prestativo, porém só responde na lingua dos gatos. O nome do seu cliente é {wa_name}.'
  
def parse_text_message(wa_id, wa_name, message_inputs):
  message = '. '.join(message_inputs)
  prompt = build_prompt(wa_name)

  messages = MessagesBuilder(wa_id, prompt, message, MSGS_LIMIT).build()

  llm_requester = LlmRequester(messages)
  llm_requester.send()
  llm_requester.persist_response_to_db(wa_id)

  response_message = llm_requester.response_message

  print(response_message)