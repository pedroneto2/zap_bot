import os
import json
import jwt
from redis import Redis
from sqlite3.dbapi2 import connect
from flask import Flask, request, render_template, redirect, url_for, make_response
from urllib.parse import urlparse
from init_db import create_db
from datetime import datetime, timedelta

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





@app.get('/login')
def login():
  access_token = request.cookies.get('access_token')

  if authenticate_token(access_token):
    return redirect(url_for('index'))

  message = request.args.get('message', default = '', type = str)

  return render_template('login.html', message = message)





@app.get('/authentication')
def authentication():
  user = request.args.get('user', type = str)
  pwd = request.args.get('pwd', type = str)

  if authenticate_user(user, pwd):
    payload = {}
    payload['username'] = user
    payload['password'] = pwd
    payload['exp'] = datetime.now() + timedelta(minutes = 60)
    encoded_jwt = jwt.encode(payload, os.environ['JWT_SECRET'], algorithm="HS256")
    response = make_response(redirect(url_for('index')))
    response.set_cookie('access_token', encoded_jwt)
    return response
  else:
    return redirect(url_for('login', message = 'Invalid Credentials'))





@app.get('/admin/orders')
def index():
  access_token = request.cookies.get('access_token')

  if not authenticate_token(access_token):
    return redirect(url_for('login', message = 'Invalid Credentials'))

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
  
  return render_template('index.html', orders = parsed_orders, per_page = per_page,
                                       data_length = data_length, access_token = access_token)





@app.get('/admin/orders/edit/<id>')
def edit_order(id):
  access_token = request.cookies.get('access_token')

  if not authenticate_token(access_token):
    return redirect(url_for('login', message = 'Invalid Credentials'))

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

  return render_template('edit.html', order = parsed_order, access_token = access_token)





@app.get('/admin/orders/save/<id>')
def save_order(id):
  access_token = request.args.get('access_token', type = str)

  if not authenticate_token(access_token):
    return redirect(url_for('login', message = 'Invalid Credentials'))

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
  access_token = request.args.get('access_token', type = str)

  if not authenticate_token(access_token):
    return { 'success': False, 'error': 'Invalid Credentials' }

  order_id = request.args.get('id', type = str)
  access_token = request.args.get('access_token', type = str)
  sql = "DELETE FROM orders WHERE id = ?"

  cursor = connection.cursor()
  cursor.execute(sql, (order_id))
  cursor.close()

  return { 'success': True }





@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('index'))





def authenticate_user(name, password):
  sql = "SELECT name, password FROM users WHERE name = ? AND password = ?"

  cursor = connection.cursor()
  cursor.execute(sql, (name, password))
  user = cursor.fetchall()
  cursor.close()

  return bool(user)





def authenticate_token(access_token):
  try:
    payload = jwt.decode(access_token, os.environ['JWT_SECRET'], algorithms=["HS256"])
  except:
    return False
  
  return authenticate_user(payload['username'], payload['password'])





from text.handler import handle_text_requests