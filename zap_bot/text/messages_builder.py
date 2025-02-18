import json
from app import connection

class MessagesBuilder:
  def __init__(self, wa_id, prompt, new_message = None, msgs_limit = 20):
    self.wa_id = wa_id
    self.prompt = prompt
    self.new_message = new_message
    self.msgs_limit = msgs_limit
    self.message_history = self.get_message_history()

  def build(self):
    self.message_history.append({ 'role': 'user', 'content': self.new_message })

    return self.message_history

  def get_message_history(self):
    sql = f"SELECT role, content, tool_calls, tool_call_id, name FROM messages WHERE wa_id = '{self.wa_id}' ORDER BY created_at DESC LIMIT {self.msgs_limit}"

    cursor = connection.cursor()
    cursor.execute(sql)
    messages = cursor.fetchall()
    cursor.close()
    messages = list(reversed(list(map(lambda row: self.compact_row(row), messages))))
    if messages:
      return messages
    else:
      return [{ 'role': 'system', 'content': self.prompt }]

  def compact_row(self, row):
    row = { 'role': row[0], 'content': self.safe_json_loads(row[1]), 'tool_calls': self.safe_json_loads(row[2]), 'tool_call_id': row[3], 'name': row[4] }

    return {k: v for k, v in row.items() if v is not None}

  def safe_json_loads(self, value):
    try:  
      return json.loads(value.replace("\'", "\""))
    except (json.JSONDecodeError, TypeError):
      return value or None