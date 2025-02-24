import json
from app import app, connection
from flask import request, render_template, redirect, url_for
from auth import authenticate_token

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
  
  parsed_orders = list(map(lambda order:
                            { 
                              'id': order[0],
                              'customer_name': order[1],
                              'customer_phone': order[2],
                              'customer_address': order[3],
                              'customer_products': json.loads(order[4].replace("\'", "\"")),
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
  sql2 = "SELECT id, name, prices_per_unit FROM products"

  cursor = connection.cursor()
  cursor.execute(sql, (id))
  orders = cursor.fetchall()
  cursor.execute(sql2)
  products = cursor.fetchall()
  cursor.close()

  order = orders[0]

  parsed_order = dict()

  parsed_order['id'] = order[0]
  parsed_order['customer_name'] = order[1]
  parsed_order['customer_phone'] = order[2]
  parsed_order['customer_address'] = order[3]
  parsed_order['customer_products'] = json.loads(order[4].replace("\'", "\""))
  parsed_order['total_price'] = order[5]
  parsed_order['created_at'] = order[6]

  parsed_products = list(map(lambda product:
                            {
                              'id': product[0],
                              'name': product[1],
                              'prices_per_unit': json.loads(product[2].replace("\'", "\""))
                            }, products))

  return render_template('edit.html', order = parsed_order,
                                      products = parsed_products,
                                      order_products_count = len(parsed_order['customer_products']),
                                      access_token = access_token)





@app.get('/admin/orders/save/<id>')
def save_order(id):
  access_token = request.args.get('access_token', type = str)

  if not authenticate_token(access_token):
    return redirect(url_for('login', message = 'Invalid Credentials'))

  customer_name = request.args.get('cname', type = str)
  customer_phone = request.args.get('cphone', type = str)
  customer_address = request.args.get('caddress', type = str)
  customer_price = request.args.get('tprice', type = float)

  product_amount = request.args.get('product-amount', type = int)

  customer_products = []

  for i in range(1, product_amount + 1):
    product = request.args.get(f'oproduct{i}', type = str)
    price_per_unit = request.args.get(f'uprice{i}', type = str)
    quantity = request.args.get(f'pquantity{i}', type = float)

    if not quantity:
      continue

    product = json.loads(product.replace("\'", "\""))
    product['price_per_unit'] = price_per_unit
    product['quantity'] = quantity

    customer_products.append(product)

  customer_products = json.dumps(customer_products)

  sql = '''
    UPDATE orders SET customer_name = ?, customer_phone = ?,
                      customer_address = ?, customer_products = ?,
                      total_price = ?
    WHERE id = ?
  '''

  cursor = connection.cursor()
  cursor.execute(sql, (customer_name, customer_phone, customer_address,
                       customer_products, customer_price, id))
  connection.commit()
  cursor.close()

  return redirect(url_for('index'))





@app.post('/admin/orders/new')
def add_order():
  access_token = request.args.get('access_token', type = str)

  if not authenticate_token(access_token):
    return { 'success': False, 'error': 'Invalid Credentials' }

  customer_name = request.args.get('cname', type = str)
  customer_phone = request.args.get('cphone', type = str)
  customer_address = request.args.get('caddress', type = str)
  customer_products = '[]'

  sql = "INSERT INTO orders(customer_name, customer_phone, customer_address, customer_products) VALUES (?, ?, ?, ?)"

  cursor = connection.cursor()
  cursor.execute(sql, (customer_name, customer_phone, customer_address, customer_products))
  connection.commit()
  cursor.close()

  return { "success": True }





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
  connection.commit()
  cursor.close()

  return { 'success': True }
