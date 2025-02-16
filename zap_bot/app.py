import os
from redis import Redis
from sqlite3.dbapi2 import connect
from flask import Flask, request
from urllib.parse import urlparse

def create_db():
  sql = '''
    CREATE TABLE IF NOT EXISTS "messages"(
      "wa_id" TEXT,
      "role" TEXT,
      "content" TEXT,
      "tool_calls" TEXT,
      "tool_call_id" TEXT,
      "name" TEXT,
      "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS "products"(
      "id" INTEGER,
      "name" TEXT,
      "price" TEXT,
      "unit" TEXT,
      "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY("id")
    );
    CREATE TABLE IF NOT EXISTS "orders"(
      "id" INTEGER,
      "customer_name" TEXT,
      "customer_phone" TEXT,
      "customer_address" TEXT,
      PRIMARY KEY("id")
    )
  '''
  cursor = connection.cursor()
  cursor.executescript(sql)
  connection.commit()
  cursor.close()

app = Flask(__name__)
url = urlparse(os.environ['REDISTOGO_URL'])
redis = Redis(host=url.hostname, port=url.port, password=url.password, decode_responses=True)
connection = connect('./database.db', check_same_thread=False)
create_db()

@app.route('/whatsapp/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
  if request.method == 'GET':
    if request.args.get('hub.mode') == 'subscribe':
      return request.args.get('hub.challenge')
    else:
      return 'error', 400
  else:
    data = request.get_json()
    message_type = data['entry'][0]['changes'][0]['value']['messages'][0]['type']
    wa_name = data['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']
    wa_id = data['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']
    phone_id = data['entry'][0]['changes'][0]['value']['metadata']['phone_number_id']
    if message_type == 'text':
      message = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
      handle_text_requests(phone_id, wa_id, wa_name, message)
      
    return {}
  
from text.handler import handle_text_requests