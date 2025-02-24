import json
from app import app, connection
from flask import request, render_template, redirect, url_for
from auth import authenticate_token

@app.get('/admin/products')
def products_index():
  access_token = request.cookies.get('access_token')

  if not authenticate_token(access_token):
    return redirect(url_for('login', message = 'Invalid Credentials'))

  page = request.args.get('page', default = 1, type = int)
  per_page = 10

  offset = (page - 1) * per_page

  sql = "SELECT * FROM products ORDER BY created_at DESC LIMIT ?, ?"
  sql2 = "SELECT COUNT(*) FROM products"

  cursor = connection.cursor()
  cursor.execute(sql, (offset, per_page))
  products = cursor.fetchall()
  cursor.execute(sql2)
  data_length = cursor.fetchall()[0]
  cursor.close()
  
  parsed_products = list(map(lambda product:
                            { 
                              'id': product[0],
                              'name': product[1],
                              'prices_per_unit': json.loads(product[2].replace("\'", "\"")),
                              'created_at': product[3]
                            }, products))
  
  return render_template('product_index.html', products = parsed_products, per_page = per_page,
                                               data_length = data_length, access_token = access_token)





@app.get('/admin/products/edit/<id>')
def edit_product(id):
  access_token = request.cookies.get('access_token')

  if not authenticate_token(access_token):
    return redirect(url_for('login', message = 'Invalid Credentials'))

  sql = "SELECT * FROM products WHERE id = ?"

  cursor = connection.cursor()
  cursor.execute(sql, (id))
  products = cursor.fetchall()
  cursor.close()

  product = products[0]

  parsed_product = dict()

  parsed_product['id'] = product[0]
  parsed_product['name'] = product[1]
  parsed_product['prices_per_unit'] = json.loads(product[2].replace("\'", "\""))

  return render_template('product_edit.html', product = parsed_product,
                                              prices_per_unit_count = len(parsed_product['prices_per_unit']),
                                              access_token = access_token)





@app.get('/admin/products/save/<id>')
def save_product(id):
  access_token = request.args.get('access_token', type = str)

  if not authenticate_token(access_token):
    return redirect(url_for('login', message = 'Invalid Credentials'))

  product_name = request.args.get('pname', type = str)

  prices_per_unit_amount = request.args.get('ppu-product-amount', type = int)

  prices_per_unit = []

  for i in range(1, prices_per_unit_amount + 1):
    price_per_unit_value = request.args.get(f'price-ppu{i}', type = float)
    price_per_unit_unit = request.args.get(f'unit-ppu{i}', type = str)

    if price_per_unit_unit == 'unidade':
      price_per_unit_unit = 'unit'

    if not (price_per_unit_value and price_per_unit_unit):
      continue

    price_per_unit = f"{price_per_unit_value}/{price_per_unit_unit}"

    prices_per_unit.append(price_per_unit)

  prices_per_unit = json.dumps(prices_per_unit)

  sql = "UPDATE products SET name = ?, prices_per_unit = ? WHERE id = ?"

  cursor = connection.cursor()
  cursor.execute(sql, (product_name, prices_per_unit, id))
  connection.commit()
  cursor.close()

  return redirect(url_for('products_index'))





@app.post('/admin/products/new')
def add_product():
  access_token = request.args.get('access_token', type = str)

  if not authenticate_token(access_token):
    return { 'success': False, 'error': 'Invalid Credentials' }

  product_name = request.args.get('pname', type = str)

  prices_per_unit = ["1.00/unit"]

  prices_per_unit = json.dumps(prices_per_unit)

  sql = "INSERT INTO products(name, prices_per_unit) VALUES (?, ?)"

  cursor = connection.cursor()
  cursor.execute(sql, (product_name, prices_per_unit))
  connection.commit()
  cursor.close()

  return { "success": True }





@app.delete('/admin/products/delete')
def delete_products():
  access_token = request.args.get('access_token', type = str)

  if not authenticate_token(access_token):
    return { 'success': False, 'error': 'Invalid Credentials' }

  order_id = request.args.get('id', type = str)
  access_token = request.args.get('access_token', type = str)
  sql = "DELETE FROM products WHERE id = ?"

  cursor = connection.cursor()
  cursor.execute(sql, (order_id))
  connection.commit()
  cursor.close()

  return { 'success': True }
