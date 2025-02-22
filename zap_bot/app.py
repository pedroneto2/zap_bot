import os
import json
from redis import Redis
from sqlite3.dbapi2 import connect
from flask import Flask, request, render_template, redirect, url_for
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
      "items" TEXT,
      "total_price" TEXT,
      "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
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

@app.get('/admin/orders/edit/<id>')
def edit_order(id):
  sql = "SELECT * FROM orders WHERE id = ?"

  cursor = connection.cursor()
  cursor.execute(sql, (id))
  orders = cursor.fetchall()
  cursor.close()

  order = orders[0]

  parsed_order = dict()

  parsed_order['id'] = order[0]
  parsed_order['customer_name'] = order[1]
  parsed_order['customer_phone'] = order[2]
  parsed_order['customer_address'] = order[3]
  parsed_order['items'] = json.loads(order[4].replace("\'", "\""))
  parsed_order['total_price'] = order[5]
  parsed_order['created_at'] = order[6]

  return render_template('edit.html', order = parsed_order)

@app.get('/admin/orders')
def index():
  page = request.args.get('page', default = 1, type = int)
  per_page = 10

  offset = (page - 1) * per_page

  sql = "SELECT * FROM orders ORDER BY created_at DESC LIMIT ?, ?"
  sql2 = "SELECT COUNT(*) FROM orders"

  cursor = connection.cursor()
  cursor.execute(sql, (offset, per_page))
  orders = cursor.fetchall()
  cursor.execute(sql2)
  data_length = cursor.fetchall()[0]
  cursor.close()

  print(data_length)
  
  parsed_orders = list(map(lambda order:
                            { 
                              'id': order[0],
                              'customer_name': order[1],
                              'customer_phone': order[2],
                              'customer_address': order[3],
                              'items': json.loads(order[4].replace("\'", "\"")),
                              'total_price': order[5],
                              'created_at': order[6]
                            }, orders))
  
  return render_template('index.html', orders = parsed_orders, per_page = per_page, data_length = data_length)

@app.get('/admin/orders/save/<id>')
def save_order(id):
  customer_name = request.args.get('cname', type = str)
  customer_phone = request.args.get('cphone', type = str)
  customer_address = request.args.get('caddress', type = str)
  customer_price = request.args.get('tprice', type = str)

  sql = '''
    UPDATE orders SET customer_name = ?, customer_phone = ?,
                      customer_address = ?, total_price = ?
    WHERE id = ?
  '''

  cursor = connection.cursor()
  cursor.execute(sql, (customer_name, customer_phone, customer_address, customer_price, id))
  cursor.close()  

  return redirect(url_for('index'))

@app.delete('/admin/orders/delete')
def delete_orders():
  order_id = request.args.get('id', type = str)
  sql = "DELETE FROM orders WHERE id = ?"

  cursor = connection.cursor()
  cursor.execute(sql, (order_id))
  cursor.close()

  return {}

from text.handler import handle_text_requests