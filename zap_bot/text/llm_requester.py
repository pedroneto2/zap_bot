from .llm_switcher import LlmSwitcher 
from app import connection

class LlmRequester:
  def __init__(self, messages, model = None, stream = False, max_tokens = 200):
    self.client_info = LlmSwitcher(model).get_client_info()
    self.messages = messages
    self.stream = stream
    self.max_tokens = max_tokens

  def send(self):
    response = self.client_info['client'].chat.completions.create(
        messages = self.messages,
        model = self.client_info['model'],
        stream = self.stream,
        max_tokens = self.max_tokens
    )

    self.response_message = response['choices'][0]['message']['content']
    self.messages.append({ 'role': 'assistant', 'content': self.response_message })

    return response
 
  def persist_response_to_db(self, wa_id):
    sql = "INSERT INTO messages(wa_id, role, content) VALUES (?, ?, ?)"

    cursor = connection.cursor()

    if len(self.messages) <= 2:
      cursor.execute(sql, wa_id, 'system', self.messages[0][2])

    cursor.execute(sql, wa_id, 'assistant', self.response_message)

    connection.commit()
    cursor.close()