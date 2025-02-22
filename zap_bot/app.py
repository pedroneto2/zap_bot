import os
from redis import Redis
from sqlite3.dbapi2 import connect
from flask import Flask, request, redirect, url_for
from urllib.parse import urlparse
from init_db import create_db

app = Flask(__name__)
url = urlparse(os.environ['REDISTOGO_URL'])
redis = Redis(host=url.hostname, port=url.port, password=url.password, decode_responses=True)
connection = connect('./database.db', check_same_thread=False)
create_db(connection)

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





@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('index'))




from auth import *
from orders import *
from text.handler import handle_text_requests