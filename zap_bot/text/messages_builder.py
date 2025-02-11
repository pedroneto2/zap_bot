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
    sql = f"SELECT role, content FROM messages WHERE wa_id = '{self.wa_id}' ORDER BY created_at DESC LIMIT {self.msgs_limit}"

    cursor = connection.cursor()
    cursor.execute(sql)
    messages = cursor.fetchall()
    cursor.close()
    messages = list(reversed(list(map(lambda row: { 'role': row[0], 'content': row[1] }, messages))))
    if messages:
      return messages
    else:
      return [{ 'role': 'system', 'content': self.prompt }]
    