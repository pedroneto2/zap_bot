from app import connection

def get_products(product_name = None):
  if product_name:
    sql = f"SELECT id, name, price, unit FROM products WHERE name like '%{product_name.lower()}%'"
  else:
    sql = "SELECT id, name, price, unit FROM products"
  
  cursor = connection.cursor()
  cursor.execute(sql)
  products = cursor.fetchall()
  cursor.close()

  return list(map(lambda product: { 'id': product[0], 'name': product[1], 'price': product[2], 'unit': product[3] }, products))