from app import connection

def get_products(product_name = None):
  if product_name:
    sql = f"SELECT id, name, prices_per_unit FROM products WHERE name like '%{product_name.lower()}%'"
  else:
    sql = "SELECT id, name, price, unit FROM products"
  
  cursor = connection.cursor()
  cursor.execute(sql)
  products = cursor.fetchall()
  cursor.close()

  return list(map(lambda product: { 'id': product[0], 'name': product[1], 'prices_per_unit': product[2] }, products))